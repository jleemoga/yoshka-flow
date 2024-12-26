"""
Prompt templates for metrics generation.
"""
from typing import Dict, Any, List

class MetricPrompts:
    """Collection of prompt templates for different metric types"""
    
    @staticmethod
    def get_company_overview_prompt(company_name: str, references: List[Dict[str, Any]]) -> str:
        """Generate prompt for company overview metrics"""
        urls = "\n".join([f"- {ref['url']}" for ref in references])
        return f"""Based on the following references about {company_name}:

{urls}

Generate a structured analysis with the following metrics:
1. Company Size (employees range)
2. Industry Classification
3. Revenue Range (if public)
4. Geographic Presence
5. Key Products/Services
6. Market Position
7. Competitive Advantages

For each metric:
- Provide a confidence score (0-1)
- Cite specific references used
- Include relevant quotes or data points

Output in JSON format:
{{
    "metrics": [
        {{
            "name": "metric_name",
            "value": "metric_value",
            "confidence_score": 0.0-1.0,
            "references": ["url1", "url2"],
            "supporting_data": ["quote1", "quote2"]
        }}
    ]
}}"""

    @staticmethod
    def get_sustainability_metrics_prompt(company_name: str, references: List[Dict[str, Any]]) -> str:
        """Generate prompt for sustainability metrics"""
        urls = "\n".join([f"- {ref['url']}" for ref in references])
        return f"""Based on the following references about {company_name}:

{urls}

Generate sustainability metrics focusing on:
1. Environmental Impact
2. Carbon Footprint
3. Sustainability Initiatives
4. Resource Usage
5. Waste Management
6. Environmental Certifications

For each metric:
- Provide a confidence score (0-1)
- Cite specific references
- Include quantitative data where available

Output in JSON format:
{{
    "metrics": [
        {{
            "name": "metric_name",
            "value": "metric_value",
            "confidence_score": 0.0-1.0,
            "references": ["url1", "url2"],
            "supporting_data": ["quote1", "quote2"]
        }}
    ]
}}"""

    @staticmethod
    def get_product_metrics_prompt(product_name: str, references: List[Dict[str, Any]]) -> str:
        """Generate prompt for product metrics"""
        urls = "\n".join([f"- {ref['url']}" for ref in references])
        return f"""Based on the following references about {product_name}:

{urls}

Generate product metrics focusing on:
1. Market Share
2. Price Range
3. Target Audience
4. Key Features
5. Customer Satisfaction
6. Competitive Analysis

For each metric:
- Provide a confidence score (0-1)
- Cite specific references
- Include customer feedback or reviews where available

Output in JSON format:
{{
    "metrics": [
        {{
            "name": "metric_name",
            "value": "metric_value",
            "confidence_score": 0.0-1.0,
            "references": ["url1", "url2"],
            "supporting_data": ["quote1", "quote2"]
        }}
    ]
}}"""

    @staticmethod
    def get_innovation_metrics_prompt(entity_name: str, entity_type: str, references: List[Dict[str, Any]]) -> str:
        """Generate prompt for innovation metrics"""
        urls = "\n".join([f"- {ref['url']}" for ref in references])
        return f"""Based on the following references about {entity_name}:

{urls}

Generate innovation metrics for this {entity_type} focusing on:
1. R&D Investment
2. Patent Portfolio
3. Innovation Pipeline
4. Technology Adoption
5. Industry Leadership
6. Future Developments

For each metric:
- Provide a confidence score (0-1)
- Cite specific references
- Include specific innovations or patents where available

Output in JSON format:
{{
    "metrics": [
        {{
            "name": "metric_name",
            "value": "metric_value",
            "confidence_score": 0.0-1.0,
            "references": ["url1", "url2"],
            "supporting_data": ["quote1", "quote2"]
        }}
    ]
}}"""
