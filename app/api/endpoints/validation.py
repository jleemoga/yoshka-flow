from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from app.core.tasks import validate_entity_query

router = APIRouter()

class QueryValidationRequest(BaseModel):
    query: str

class QueryValidationResponse(BaseModel):
    valid: bool
    sanitized_name: Optional[str] = None
    error_message: Optional[str] = None
    task_id: Optional[str] = None

def basic_sanitize(query: str) -> str:
    """Basic sanitization of input query"""
    # Remove extra whitespace
    sanitized = " ".join(query.split())
    # Remove special characters except common ones used in company names
    sanitized = re.sub(r'[^a-zA-Z0-9\s\'\"\-\&\.,]', '', sanitized)
    return sanitized.strip()

@router.post("/validate_query", 
            response_model=QueryValidationResponse,
            summary="Validate entity query",
            description="Validates a query string for entity creation. Performs basic validation and sanitization.")
async def validate_query(request: QueryValidationRequest):
    # Submit validation task to Celery
    task = validate_entity_query.delay(request.query)
    
    # Return task ID immediately
    return QueryValidationResponse(
        valid=True,  # Initial state
        task_id=task.id
    )

@router.get("/validate_query/{task_id}",
           response_model=QueryValidationResponse,
           summary="Get validation result",
           description="Get the result of an async validation task")
async def get_validation_result(task_id: str):
    # Get task result from Celery
    task = validate_entity_query.AsyncResult(task_id)
    
    if task.ready():
        result = task.get()
        return QueryValidationResponse(
            valid=result["valid"],
            sanitized_name=result["sanitized_name"],
            error_message=result["error_message"]
        )
    else:
        return QueryValidationResponse(
            valid=True,  # Still processing
            task_id=task_id
        )
