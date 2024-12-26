"""
Metrics generation tool that processes references and generates structured metrics.
"""
from typing import Dict, Any, List
import logging
import json
from datetime import datetime

from app.tools.base import BaseTool, ExecutionError
from app.tools.llm.openai_tool import OpenAITool
from app.tools.llm.prompt_templates.metrics import MetricPrompts
from app.db.models import Metric, Source  # We'll need to create this
from app.db.session import get_db  # We'll need to create this

logger = logging.getLogger(__name__)

class MetricsGenerationTool(BaseTool):
    """
    Tool for generating metrics from collected references.
    Uses LLM to analyze references and extract structured metrics.
    """
    
    def __init__(self):
        super().__init__()
        self.llm_tool = OpenAITool()
        self.metric_types = {
            'company': [
                ('overview', MetricPrompts.get_company_overview_prompt),
                ('sustainability', MetricPrompts.get_sustainability_metrics_prompt),
                ('innovation', MetricPrompts.get_innovation_metrics_prompt)
            ],
            'product': [
                ('product_metrics', MetricPrompts.get_product_metrics_prompt),
                ('innovation', MetricPrompts.get_innovation_metrics_prompt)
            ]
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute metrics generation for an entity.
        
        Args:
            entity_id: ID of the entity
            entity_name: Name of the entity
            entity_type: Type of entity (company/product)
            references: List of references to analyze
            
        Returns:
            Dict containing generated metrics
        """
        entity_id = kwargs['entity_id']
        entity_name = kwargs['entity_name']
        entity_type = kwargs.get('entity_type', 'company')
        references = kwargs['references']
        
        try:
            all_metrics = []
            
            # Generate metrics for each metric type
            for metric_type, prompt_func in self.metric_types[entity_type]:
                # Generate prompt
                prompt = prompt_func(
                    entity_name if entity_type == 'product' else entity_name,
                    references
                )
                
                # Get metrics from LLM
                result = await self.llm_tool.run(
                    prompt=prompt,
                    system_prompt=(
                        f"You are analyzing {entity_type} metrics for {entity_name}. "
                        "Focus on extracting factual information from the provided references. "
                        "If information is uncertain, reflect this in the confidence score."
                    )
                )
                
                if result['success']:
                    metrics = result['data'].get('metrics', [])
                    for metric in metrics:
                        metric['type'] = metric_type
                        all_metrics.append(metric)
                
            # Store metrics in database
            stored_metrics = await self._store_metrics(entity_id, all_metrics)
            
            return {
                "entity_id": entity_id,
                "metrics_generated": len(stored_metrics),
                "metrics": stored_metrics,
                "success": True
            }
            
        except Exception as e:
            raise ExecutionError(f"Metrics generation failed: {str(e)}")
    
    def validate_input(self, **kwargs) -> bool:
        """
        Validate the input parameters for metrics generation.
        
        Args:
            entity_id: ID of the entity
            entity_name: Name of the entity
            entity_type: Type of entity
            references: List of references
            
        Returns:
            bool: True if input is valid
        """
        entity_id = kwargs.get('entity_id')
        entity_name = kwargs.get('entity_name')
        entity_type = kwargs.get('entity_type', 'company')
        references = kwargs.get('references', [])
        
        if not entity_id:
            raise ValueError("Entity ID is required")
            
        if not entity_name:
            raise ValueError("Entity name is required")
            
        if entity_type not in ['company', 'product']:
            raise ValueError("Invalid entity type")
            
        if not isinstance(references, list):
            raise ValueError("References must be a list")
            
        if not references:
            raise ValueError("At least one reference is required")
            
        return True
    
    async def _store_metrics(self, entity_id: str, metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Store generated metrics in the database"""
        stored_metrics = []
        async with get_db() as db:
            for metric_data in metrics:
                metric = Metric(
                    entity_id=entity_id,
                    name=metric_data['name'],
                    value=metric_data['value'],
                    type=metric_data['type'],
                    confidence_score=metric_data['confidence_score'],
                    raw_data=json.dumps({
                        'references': metric_data['references'],
                        'supporting_data': metric_data['supporting_data']
                    }),
                    generated_at=datetime.utcnow()
                )
                db.add(metric)
                stored_metrics.append(metric.to_dict())
            await db.commit()
        
        return stored_metrics
