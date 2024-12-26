"""
Research service for orchestrating the AI research process.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Company, Product, AIJob, Category, Metric, Source
from app.tools.search.reference_tool import ReferenceGatheringTool
from app.tools.llm.metrics_tool import MetricsGenerationTool
from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)

class ResearchService:
    """
    Service for managing the AI research process.
    Coordinates tools and database operations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.reference_tool = ReferenceGatheringTool()
        self.metrics_tool = MetricsGenerationTool()
    
    async def start_research(self, query: str, entity_type: str = 'company') -> AIJob:
        """
        Start the research process for an entity.
        
        Args:
            query: Entity name to research
            entity_type: Type of entity (company/product)
            
        Returns:
            AIJob: Created job record
        """
        # Create AI job record
        job = AIJob(
            job_type=f"{entity_type}_research",
            status='pending',
            result_data={'query': query}
        )
        self.db.add(job)
        await self.db.commit()
        
        # Start async research task
        celery_app.send_task(
            'app.tasks.research.execute_research',
            args=[str(job.job_id), query, entity_type]
        )
        
        return job
    
    async def execute_research(self, job_id: UUID, query: str, entity_type: str) -> Dict[str, Any]:
        """
        Execute the research process.
        
        Args:
            job_id: ID of the research job
            query: Entity name to research
            entity_type: Type of entity
            
        Returns:
            Dict containing research results
        """
        try:
            # Update job status
            job = await self._get_job(job_id)
            job.status = 'in_progress'
            job.started_at = datetime.utcnow()
            await self.db.commit()
            
            # Create entity
            entity = await self._create_entity(query, entity_type)
            
            # Update job with entity ID
            if entity_type == 'company':
                job.company_id = entity.company_id
            else:
                job.product_id = entity.product_id
            await self.db.commit()
            
            # Gather references
            reference_result = await self.reference_tool.run(
                entity_id=str(entity.company_id if entity_type == 'company' else entity.product_id),
                entity_name=query,
                entity_type=entity_type
            )
            
            # Generate metrics
            metrics_result = await self.metrics_tool.run(
                entity_id=str(entity.company_id if entity_type == 'company' else entity.product_id),
                entity_name=query,
                entity_type=entity_type,
                references=reference_result['references']
            )
            
            # Update job status
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            job.result_data.update({
                'references_found': reference_result['references_found'],
                'metrics_generated': metrics_result['metrics_generated']
            })
            await self.db.commit()
            
            return {
                "success": True,
                "entity_id": str(entity.company_id if entity_type == 'company' else entity.product_id),
                "references": reference_result['references'],
                "metrics": metrics_result['metrics']
            }
            
        except Exception as e:
            logger.error(f"Research failed: {str(e)}")
            if job:
                job.status = 'failed'
                job.result_data['error'] = str(e)
                await self.db.commit()
            raise
    
    async def _get_job(self, job_id: UUID) -> Optional[AIJob]:
        """Get AI job by ID"""
        stmt = select(AIJob).where(AIJob.job_id == job_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _create_entity(self, name: str, entity_type: str) -> Any:
        """Create new entity record"""
        if entity_type == 'company':
            entity = Company(name=name)
        else:
            # For products, we'd need a company_id
            raise NotImplementedError("Product creation not yet implemented")
            
        self.db.add(entity)
        await self.db.commit()
        return entity
