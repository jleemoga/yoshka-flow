from app.core.celery_app import celery_app
import re
from typing import Dict, Optional

@celery_app.task(name="validate_entity_query")
def validate_entity_query(query: str) -> Dict[str, Optional[str]]:
    """
    Validate and sanitize an entity query.
    This is a placeholder for more complex validation that will be added later.
    """
    # Basic validation
    if not query or len(query.strip()) < 2:
        return {
            "valid": False,
            "sanitized_name": None,
            "error_message": "Query must be at least 2 characters long"
        }
    
    # Basic sanitization
    sanitized = " ".join(query.split())
    sanitized = re.sub(r'[^a-zA-Z0-9\s\'\"\-\&\.,]', '', sanitized).strip()
    
    if not sanitized:
        return {
            "valid": False,
            "sanitized_name": None,
            "error_message": "Query contains no valid characters after sanitization"
        }
    
    # In the future, we'll add:
    # 1. Profanity check
    # 2. Company name format validation
    # 3. Duplicate check against existing entities
    # 4. AI-powered validation
    
    return {
        "valid": True,
        "sanitized_name": sanitized,
        "error_message": None
    }
