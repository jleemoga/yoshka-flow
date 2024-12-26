"""
Tests for the YoshkaFlow tool infrastructure.
"""
import pytest
from app.tools.validation import EntityValidationTool
from app.tools.base import ValidationError

@pytest.mark.asyncio
async def test_entity_validation_tool():
    """Test the entity validation tool"""
    tool = EntityValidationTool()
    
    # Test valid company name
    result = await tool.run(name="Acme Corporation", entity_type="company")
    assert result["valid"] is True
    assert result["sanitized_name"] == "Acme Corporation"
    assert result["confidence_score"] > 0.9  # Should be very confident
    
    # Test invalid input
    with pytest.raises(ValidationError):
        await tool.run(name="", entity_type="company")
    
    # Test invalid entity type
    with pytest.raises(ValidationError):
        await tool.run(name="Acme Corp", entity_type="invalid_type")
    
    # Test caching
    # First call should execute
    result1 = await tool.run(name="Test Company", entity_type="company")
    # Second call should use cache
    result2 = await tool.run(name="Test Company", entity_type="company")
    assert result1 == result2  # Results should be identical

@pytest.mark.asyncio
async def test_validation_with_special_chars():
    """Test validation with special characters"""
    tool = EntityValidationTool()
    
    # Test valid names with special characters
    valid_names = [
        "Johnson & Johnson",
        "Procter & Gamble",
        "Ben & Jerry's",
        "AT&T Corp.",
    ]
    
    for name in valid_names:
        result = await tool.run(name=name, entity_type="company")
        assert result["valid"] is True, f"Failed to validate: {name}"
        
@pytest.mark.asyncio
async def test_profanity_check():
    """Test profanity detection"""
    tool = EntityValidationTool()
    
    # Test with a clean name
    clean_result = await tool.run(name="Clean Company Name", entity_type="company")
    assert clean_result["valid"] is True
    assert clean_result["confidence_score"] > 0.9
    
    # Note: We don't test actual profanity here to keep the tests clean
    # Instead, we could mock the profanity check in a real test suite
