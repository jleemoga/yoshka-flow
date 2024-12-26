"""
Search service for handling entity queries and research initiation.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Company, Product, AIJob
from app.core.config import get_settings
from app.tools.validation import EntityValidationTool
from app.services.research import ResearchService

logger = logging.getLogger(__name__)

class SearchService:
    """
    Service for handling search queries and initiating research when needed.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()
        self.validation_tool = EntityValidationTool()
        self.research_service = ResearchService(db)
    
    async def search_entity(self, query: str, entity_type: str = 'company') -> Dict[str, Any]:
        """
        Search for an entity, initiate research if not found.
        
        Args:
            query: Search query
            entity_type: Type of entity to search for (company/product)
            
        Returns:
            Dict containing search results or research status
        """
        # First, try to find existing entity
        entity = await self._find_existing_entity(query, entity_type)
        if entity:
            return {
                "found": True,
                "entity": entity.to_dict(),
                "metrics": await self._get_entity_metrics(entity)
            }
        
        # Check if research is already in progress
        active_job = await self._get_active_research_job(query, entity_type)
        if active_job:
            return {
                "found": False,
                "research_in_progress": True,
                "job_id": str(active_job.job_id),
                "status": active_job.status
            }
        
        # Validate query before starting research
        validation_result = await self.validation_tool.run(
            name=query,
            entity_type=entity_type
        )
        
        if not validation_result['valid']:
            return {
                "found": False,
                "error": "Invalid query",
                "details": validation_result['validation_details']
            }
        
        # Start research process
        research_job = await self.research_service.start_research(
            query=validation_result['sanitized_name'],
            entity_type=entity_type
        )
        
        return {
            "found": False,
            "research_started": True,
            "job_id": str(research_job.job_id),
            "status": research_job.status
        }
    
    async def _find_existing_entity(self, query: str, entity_type: str) -> Optional[Any]:
        """Find existing entity in database"""
        if entity_type == 'company':
            stmt = select(Company).where(Company.name.ilike(f"%{query}%"))
        else:
            stmt = select(Product).where(Product.name.ilike(f"%{query}%"))
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _get_active_research_job(self, query: str, entity_type: str) -> Optional[AIJob]:
        """Check for active research jobs for this query"""
        stmt = select(AIJob).where(
            AIJob.job_type == f"{entity_type}_research",
            AIJob.status.in_(['pending', 'in_progress']),
            AIJob.result_data['query'].astext == query
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _get_entity_metrics(self, entity: Any) -> List[Dict[str, Any]]:
        """Get metrics for an entity"""
        metrics = []
        if hasattr(entity, 'metrics'):
            for metric in entity.metrics:
                metric_dict = metric.to_dict()
                # Add related sources
                sources = [source.to_dict() for source in metric.sources]
                metric_dict['sources'] = sources
                metrics.append(metric_dict)
        return metrics
