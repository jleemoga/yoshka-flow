"""
Tests for the reference gathering tool.
"""
import pytest
from unittest.mock import Mock, patch
from app.tools.search.reference_tool import ReferenceGatheringTool
from app.tools.base import ExecutionError

@pytest.mark.asyncio
async def test_reference_tool_validation():
    """Test reference tool input validation"""
    tool = ReferenceGatheringTool()
    
    # Test valid input
    assert tool.validate_input(
        entity_id="123",
        entity_name="Test Company",
        entity_type="company"
    ) is True
    
    # Test missing entity_id
    with pytest.raises(ValueError):
        tool.validate_input(
            entity_name="Test Company",
            entity_type="company"
        )
    
    # Test missing entity_name
    with pytest.raises(ValueError):
        tool.validate_input(
            entity_id="123",
            entity_type="company"
        )
    
    # Test invalid entity_type
    with pytest.raises(ValueError):
        tool.validate_input(
            entity_id="123",
            entity_name="Test Company",
            entity_type="invalid"
        )

@pytest.mark.asyncio
async def test_search_query_generation():
    """Test search query generation"""
    tool = ReferenceGatheringTool()
    
    # Test company queries
    company_queries = tool._generate_search_queries("Acme Corp", "company")
    assert len(company_queries) >= 3
    assert any("Acme Corp" in query for query in company_queries)
    assert any("company" in query.lower() for query in company_queries)
    
    # Test product queries
    product_queries = tool._generate_search_queries("iPhone", "product")
    assert len(product_queries) >= 3
    assert any("iPhone" in query for query in product_queries)
    assert any("product" in query.lower() for query in product_queries)

@pytest.mark.asyncio
async def test_url_validation():
    """Test URL validation"""
    tool = ReferenceGatheringTool()
    
    # Test valid URLs
    assert tool._is_valid_url("https://example.org") is True
    assert tool._is_valid_url("http://sub.domain.com/path") is True
    
    # Test invalid URLs
    assert tool._is_valid_url("not-a-url") is False
    assert tool._is_valid_url("ftp://example.com") is False

@pytest.mark.asyncio
@patch('app.tools.browser.playwright_tool.PlaywrightTool.run')
async def test_reference_gathering(mock_browser):
    """Test reference gathering with mocked browser"""
    # Mock browser response
    mock_browser.return_value = {
        "success": True,
        "extracted_data": {
            "div.g div.yuRUbf > a": [
                "https://example.org/about",
                "https://example.org/products"
            ]
        }
    }
    
    tool = ReferenceGatheringTool()
    
    # Mock database session
    with patch('app.tools.search.reference_tool.get_db') as mock_db:
        mock_session = Mock()
        mock_db.return_value.__aenter__.return_value = mock_session
        
        result = await tool.run(
            entity_id="123",
            entity_name="Test Company",
            entity_type="company"
        )
        
        assert result["success"] is True
        assert result["entity_id"] == "123"
        assert result["references_found"] > 0

@pytest.mark.asyncio
async def test_reference_deduplication():
    """Test reference deduplication"""
    tool = ReferenceGatheringTool()
    
    # Create test references with duplicates
    refs = [
        {"url": "https://example.com/1", "source_type": "web", "search_engine": "google"},
        {"url": "https://example.com/1", "source_type": "web", "search_engine": "duckduckgo"},
        {"url": "https://example.com/2", "source_type": "web", "search_engine": "google"}
    ]
    
    unique_refs = tool._deduplicate_references(refs)
    assert len(unique_refs) == 2  # Should remove one duplicate
