"""
Browser automation tool using Playwright for web scraping.
"""
from typing import Dict, Any, List, Optional
import asyncio
from playwright.async_api import async_playwright, Browser, Page
import logging

from app.tools.base import BaseTool, ExecutionError

logger = logging.getLogger(__name__)

class PlaywrightTool(BaseTool):
    """
    Tool for browser automation using Playwright.
    Handles web scraping with proper error handling and retry logic.
    """
    
    def __init__(self):
        super().__init__()
        self.browser: Optional[Browser] = None
        self.max_retries = 3
        self.timeout = 30000  # 30 seconds
        
    async def _init_browser(self) -> None:
        """Initialize the browser if not already initialized"""
        if not self.browser:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox']
            )
            
    async def _get_page(self) -> Page:
        """Get a new browser page with default configuration"""
        await self._init_browser()
        page = await self.browser.new_page()
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        return page
        
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute a browser automation task.
        
        Args:
            url: URL to navigate to
            selectors: List of CSS selectors to extract
            wait_for: Optional selector to wait for before extraction
            
        Returns:
            Dict containing extracted data
        """
        url = kwargs.get('url')
        selectors = kwargs.get('selectors', [])
        wait_for = kwargs.get('wait_for')
        
        try:
            page = await self._get_page()
            
            # Navigate to URL with retry logic
            for attempt in range(self.max_retries):
                try:
                    response = await page.goto(url, timeout=self.timeout)
                    if response and response.ok:
                        break
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise ExecutionError(f"Failed to load URL after {self.max_retries} attempts: {str(e)}")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
            # Wait for specific element if requested
            if wait_for:
                await page.wait_for_selector(wait_for, timeout=self.timeout)
            
            # Extract data based on selectors
            data = {}
            for selector in selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    data[selector] = [
                        await element.inner_text()
                        for element in elements
                    ]
                except Exception as e:
                    logger.warning(f"Failed to extract selector {selector}: {str(e)}")
                    data[selector] = []
            
            # Get page title and meta description
            data['title'] = await page.title()
            description_meta = await page.query_selector('meta[name="description"]')
            if description_meta:
                data['description'] = await description_meta.get_attribute('content')
            
            return {
                "url": url,
                "extracted_data": data,
                "success": True
            }
            
        except Exception as e:
            raise ExecutionError(f"Browser automation failed: {str(e)}")
            
        finally:
            if 'page' in locals():
                await page.close()
    
    def validate_input(self, **kwargs) -> bool:
        """
        Validate the input parameters for browser automation.
        
        Args:
            url: URL to navigate to
            selectors: Optional list of CSS selectors
            wait_for: Optional selector to wait for
            
        Returns:
            bool: True if input is valid
        """
        url = kwargs.get('url')
        selectors = kwargs.get('selectors', [])
        
        if not url:
            raise ValueError("URL is required")
            
        if not isinstance(url, str):
            raise ValueError("URL must be a string")
            
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
            
        if not isinstance(selectors, list):
            raise ValueError("Selectors must be a list")
            
        return True
        
    async def cleanup(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()
            self.browser = None
