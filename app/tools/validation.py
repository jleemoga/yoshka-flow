"""
Entity validation tool for YoshkaFlow.
Validates entity names and details before creation.
"""
from typing import Dict, Any
import re
from profanity_check import predict_prob

from app.tools.base import BaseTool, ValidationError

class EntityValidationTool(BaseTool):
    """
    Tool for validating entity names and details.
    Checks for profanity, valid characters, and reasonable length.
    """
    
    def __init__(self):
        super().__init__()
        # Compile regex pattern for valid entity names
        self.name_pattern = re.compile(r'^[\w\s\-\&\.,\'\"]+$')
        
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute validation checks on the entity name.
        
        Args:
            name: Entity name to validate
            entity_type: Type of entity (company, product)
            
        Returns:
            Dict containing validation results
        """
        name = kwargs.get('name')
        entity_type = kwargs.get('entity_type', 'company')
        
        # Check profanity
        profanity_score = predict_prob([name])[0]
        
        # Validate name pattern
        pattern_valid = bool(self.name_pattern.match(name))
        
        # Validate length
        length_valid = 2 <= len(name) <= 200
        
        # Overall validation result
        is_valid = all([
            profanity_score < 0.5,  # Less than 50% chance of being profane
            pattern_valid,
            length_valid
        ])
        
        return {
            "valid": is_valid,
            "sanitized_name": name.strip(),
            "confidence_score": 1 - profanity_score,
            "validation_details": {
                "profanity_check": profanity_score < 0.5,
                "pattern_valid": pattern_valid,
                "length_valid": length_valid
            }
        }
    
    def validate_input(self, **kwargs) -> bool:
        """
        Validate the input parameters for entity validation.
        
        Args:
            name: Entity name to validate
            entity_type: Type of entity (optional)
            
        Returns:
            bool: True if input is valid
            
        Raises:
            ValidationError: If input validation fails
        """
        name = kwargs.get('name')
        entity_type = kwargs.get('entity_type', 'company')
        
        if not name:
            raise ValidationError("Entity name is required")
            
        if not isinstance(name, str):
            raise ValidationError("Entity name must be a string")
            
        if entity_type not in ['company', 'product']:
            raise ValidationError("Invalid entity type")
            
        return True
