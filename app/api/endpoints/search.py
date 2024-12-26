"""
Search endpoints for the Yoshka API.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db
from app.services.search import SearchService

router = APIRouter()

class SearchRequest(BaseModel):
    """Search request model"""
    query: str
    entity_type: str = 'company'

class SearchResponse(BaseModel):
    """Search response model"""
    found: bool
    entity: Optional[dict] = None
    metrics: Optional[list] = None
    research_in_progress: Optional[bool] = None
    research_started: Optional[bool] = None
    job_id: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None
    details: Optional[dict] = None

@router.post("/search", response_model=SearchResponse)
async def search_entity(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Search for an entity, initiating research if not found.
    
    Args:
        request: Search request containing query and entity type
        db: Database session
        
    Returns:
        Search results or research status
    """
    try:
        search_service = SearchService(db)
        result = await search_service.search_entity(
            query=request.query,
            entity_type=request.entity_type
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/research/status/{job_id}")
async def get_research_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the status of a research job.
    
    Args:
        job_id: ID of the research job
        db: Database session
        
    Returns:
        Current status of the research job
    """
    try:
        # Get job status from database
        stmt = select(AIJob).where(AIJob.job_id == UUID(job_id))
        result = await db.execute(stmt)
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found"
            )
            
        return {
            "job_id": str(job.job_id),
            "status": job.status,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "result_data": job.result_data
        }
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid job ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job status: {str(e)}"
        )
