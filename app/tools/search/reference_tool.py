"""
Reference gathering tool for collecting information about entities.
"""
from typing import Dict, Any, List
import logging
from urllib.parse import quote_plus

from app.tools.base import BaseTool, ExecutionError
from app.tools.browser.playwright_tool import PlaywrightTool
from app.db.models import Source  # We'll need to create this
from app.db.session import get_db  # We'll need to create this

logger = logging.getLogger(__name__)

class ReferenceGatheringTool(BaseTool):
    """
    Tool for gathering references about companies and products.
    Uses browser automation to search and extract information from various sources.
    """
    
    def __init__(self):
        super().__init__()
        self.browser_tool = PlaywrightTool()
        self.search_engines = {
            'google': 'https://www.google.com/search?q={}',
            'duckduckgo': 'https://duckduckgo.com/?q={}'
        }
        
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute reference gathering for an entity.
        
        Args:
            entity_id: ID of the entity
            entity_name: Name of the entity
            entity_type: Type of entity (company/product)
            
        Returns:
            Dict containing gathered references
        """
        entity_id = kwargs['entity_id']
        entity_name = kwargs['entity_name']
        entity_type = kwargs.get('entity_type', 'company')
        
        try:
            # Generate search queries
            queries = self._generate_search_queries(entity_name, entity_type)
            
            # Collect references from each search engine
            references = []
            for engine, base_url in self.search_engines.items():
                for query in queries:
                    url = base_url.format(quote_plus(query))
                    
                    # Use browser tool to get search results
                    result = await self.browser_tool.run(
                        url=url,
                        selectors=[
                            'div.g div.yuRUbf > a',  # Google search result links
                            'h2 > a.result__a'        # DuckDuckGo result links
                        ],
                        wait_for='body'
                    )
                    
                    if result['success']:
                        references.extend(
                            self._process_search_results(
                                result['extracted_data'],
                                engine
                            )
                        )
            
            # Store references in database
            unique_refs = self._deduplicate_references(references)
            stored_refs = await self._store_references(entity_id, unique_refs)
            
            return {
                "entity_id": entity_id,
                "references_found": len(stored_refs),
                "references": stored_refs,
                "success": True
            }
            
        except Exception as e:
            raise ExecutionError(f"Reference gathering failed: {str(e)}")
            
        finally:
            await self.browser_tool.cleanup()
    
    def validate_input(self, **kwargs) -> bool:
        """
        Validate the input parameters for reference gathering.
        
        Args:
            entity_id: ID of the entity
            entity_name: Name of the entity
            entity_type: Type of entity
            
        Returns:
            bool: True if input is valid
        """
        entity_id = kwargs.get('entity_id')
        entity_name = kwargs.get('entity_name')
        entity_type = kwargs.get('entity_type', 'company')
        
        if not entity_id:
            raise ValueError("Entity ID is required")
            
        if not entity_name:
            raise ValueError("Entity name is required")
            
        if entity_type not in ['company', 'product']:
            raise ValueError("Invalid entity type")
            
        return True
    
    def _generate_search_queries(self, entity_name: str, entity_type: str) -> List[str]:
        """Generate search queries for the entity"""
        queries = [
            f"{entity_name} {entity_type} overview",
            f"{entity_name} official website",
            f"{entity_name} about us",
            f"{entity_name} company profile" if entity_type == 'company' else f"{entity_name} product details"
        ]
        return queries
    
    def _process_search_results(self, data: Dict[str, List[str]], engine: str) -> List[Dict[str, str]]:
        """Process and format search results"""
        references = []
        
        # Process Google results
        if engine == 'google':
            links = data.get('div.g div.yuRUbf > a', [])
            for link in links:
                if self._is_valid_url(link):
                    references.append({
                        'url': link,
                        'source_type': 'web',
                        'search_engine': engine
                    })
        
        # Process DuckDuckGo results
        elif engine == 'duckduckgo':
            links = data.get('h2 > a.result__a', [])
            for link in links:
                if self._is_valid_url(link):
                    references.append({
                        'url': link,
                        'source_type': 'web',
                        'search_engine': engine
                    })
        
        return references
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format and check against blacklist"""
        if not url.startswith(('http://', 'https://')):
            return False
            
        # Add your blacklist logic here
        blacklist = ['example.com', 'test.com']
        return not any(domain in url for domain in blacklist)
    
    def _deduplicate_references(self, references: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Remove duplicate references based on URL"""
        seen_urls = set()
        unique_refs = []
        
        for ref in references:
            if ref['url'] not in seen_urls:
                seen_urls.add(ref['url'])
                unique_refs.append(ref)
                
        return unique_refs
    
    async def _store_references(self, entity_id: str, references: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Store references in the database"""
        stored_refs = []
        async with get_db() as db:
            for ref in references:
                source = Source(
                    entity_id=entity_id,
                    url=ref['url'],
                    source_type=ref['source_type'],
                    metadata={'search_engine': ref['search_engine']}
                )
                db.add(source)
                stored_refs.append(source.to_dict())
            await db.commit()
        
        return stored_refs
