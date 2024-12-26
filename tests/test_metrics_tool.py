"""
Tests for the metrics generation tool.
"""
import pytest
from unittest.mock import Mock, patch
import json

from app.tools.llm.metrics_tool import MetricsGenerationTool
from app.tools.base import ExecutionError

@pytest.fixture
def sample_references():
    """Sample references for testing"""
    return [
        {
            "url": "https://example.com/company1",
            "source_type": "web",
            "search_engine": "google"
        },
        {
            "url": "https://example.com/company2",
            "source_type": "web",
            "search_engine": "duckduckgo"
        }
    ]

@pytest.fixture
def sample_llm_response():
    """Sample LLM response for testing"""
    return {
        "success": True,
        "data": {
            "metrics": [
                {
                    "name": "company_size",
                    "value": "1000-5000 employees",
                    "confidence_score": 0.8,
                    "references": ["https://example.com/company1"],
                    "supporting_data": ["Company has over 1000 employees worldwide"]
                }
            ]
        },
        "model_info": {
            "model": "gpt-4",
            "tokens_used": 150
        }
    }

@pytest.mark.asyncio
async def test_metrics_tool_validation():
    """Test metrics tool input validation"""
    tool = MetricsGenerationTool()
    
    # Test valid input
    assert tool.validate_input(
        entity_id="123",
        entity_name="Test Company",
        entity_type="company",
        references=[{"url": "https://example.com"}]
    ) is True
    
    # Test missing entity_id
    with pytest.raises(ValueError):
        tool.validate_input(
            entity_name="Test Company",
            entity_type="company",
            references=[{"url": "https://example.com"}]
        )
    
    # Test missing references
    with pytest.raises(ValueError):
        tool.validate_input(
            entity_id="123",
            entity_name="Test Company",
            entity_type="company",
            references=[]
        )
    
    # Test invalid entity_type
    with pytest.raises(ValueError):
        tool.validate_input(
            entity_id="123",
            entity_name="Test Company",
            entity_type="invalid",
            references=[{"url": "https://example.com"}]
        )

@pytest.mark.asyncio
@patch('app.tools.llm.openai_tool.OpenAITool.run')
async def test_metrics_generation(mock_llm, sample_references, sample_llm_response):
    """Test metrics generation with mocked LLM"""
    mock_llm.return_value = sample_llm_response
    
    tool = MetricsGenerationTool()
    
    # Mock database session
    with patch('app.tools.llm.metrics_tool.get_db') as mock_db:
        mock_session = Mock()
        mock_db.return_value.__aenter__.return_value = mock_session
        
        result = await tool.run(
            entity_id="123",
            entity_name="Test Company",
            entity_type="company",
            references=sample_references
        )
        
        assert result["success"] is True
        assert result["entity_id"] == "123"
        assert result["metrics_generated"] > 0
        
        # Verify metric structure
        metric = result["metrics"][0]
        assert "name" in metric
        assert "value" in metric
        assert "confidence_score" in metric
        assert "type" in metric

@pytest.mark.asyncio
async def test_prompt_generation():
    """Test prompt generation for different entity types"""
    tool = MetricsGenerationTool()
    
    # Test company prompts
    company_types = [type_name for type_name, _ in tool.metric_types['company']]
    assert 'overview' in company_types
    assert 'sustainability' in company_types
    assert 'innovation' in company_types
    
    # Test product prompts
    product_types = [type_name for type_name, _ in tool.metric_types['product']]
    assert 'product_metrics' in product_types
    assert 'innovation' in product_types

@pytest.mark.asyncio
@patch('app.tools.llm.openai_tool.OpenAITool.run')
async def test_error_handling(mock_llm):
    """Test error handling in metrics generation"""
    mock_llm.side_effect = Exception("API Error")
    
    tool = MetricsGenerationTool()
    
    with pytest.raises(ExecutionError):
        await tool.run(
            entity_id="123",
            entity_name="Test Company",
            entity_type="company",
            references=[{"url": "https://example.com"}]
        )
