"""
OpenAI integration tool for generating metrics using GPT models.
"""
from typing import Dict, Any, List
import json
import logging
from openai import AsyncOpenAI
import backoff

from app.tools.base import BaseTool, ExecutionError
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class OpenAITool(BaseTool):
    """
    Tool for interacting with OpenAI's GPT models.
    Handles API calls, retries, and error handling.
    """
    
    def __init__(self):
        super().__init__()
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4-1106-preview"  # Using the latest GPT-4 model with JSON mode
        self.max_tokens = 4000
        self.temperature = 0.2  # Lower temperature for more focused outputs
        
    @backoff.on_exception(
        backoff.expo,
        (Exception,),
        max_tries=3,
        giveup=lambda e: "invalid_request_error" in str(e)
    )
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute an OpenAI API call with the given prompt.
        
        Args:
            prompt: The prompt to send to the model
            system_prompt: Optional system prompt for context
            
        Returns:
            Dict containing the model's response
        """
        prompt = kwargs.get('prompt')
        system_prompt = kwargs.get('system_prompt', 
            "You are a precise data analyst. Always respond in valid JSON format. "
            "Base your analysis only on the provided references. "
            "If information is not available, use null values and lower confidence scores."
        )
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            try:
                result = json.loads(response.choices[0].message.content)
                return {
                    "success": True,
                    "data": result,
                    "model_info": {
                        "model": self.model,
                        "tokens_used": response.usage.total_tokens
                    }
                }
            except json.JSONDecodeError as e:
                raise ExecutionError(f"Failed to parse OpenAI response as JSON: {str(e)}")
                
        except Exception as e:
            raise ExecutionError(f"OpenAI API call failed: {str(e)}")
    
    def validate_input(self, **kwargs) -> bool:
        """
        Validate the input parameters for the OpenAI API call.
        
        Args:
            prompt: The prompt to validate
            system_prompt: Optional system prompt
            
        Returns:
            bool: True if input is valid
        """
        prompt = kwargs.get('prompt')
        system_prompt = kwargs.get('system_prompt', '')
        
        if not prompt:
            raise ValueError("Prompt is required")
            
        if not isinstance(prompt, str):
            raise ValueError("Prompt must be a string")
            
        if system_prompt and not isinstance(system_prompt, str):
            raise ValueError("System prompt must be a string")
            
        # Check prompt length (rough token estimate)
        if len(prompt) > 32000:  # Assuming ~4 chars per token
            raise ValueError("Prompt is too long")
            
        return True
