"""
Celery tasks for executing research operations.
"""
from uuid import UUID
from app.core.celery_app import celery_app
from app.services.research import ResearchService
from app.db.session import get_db

@celery_app.task(name='app.tasks.research.execute_research')
async def execute_research(job_id: str, query: str, entity_type: str):
    """
    Execute research process for an entity.
    
    Args:
        job_id: ID of the research job
        query: Entity name to research
        entity_type: Type of entity
    """
    async with get_db() as db:
        research_service = ResearchService(db)
        await research_service.execute_research(
            job_id=UUID(job_id),
            query=query,
            entity_type=entity_type
        )
