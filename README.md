# YoshkaFlow Backend

Backend services for the YoshkaFlow project - an AI-driven entity research and metrics generation system.

## Project Structure

```
yoshka-flow/
├── app/
│   ├── main.py          # FastAPI application instance
│   ├── api/             # API endpoints
│   │   └── endpoints/
│   │       └── validation.py
│   └── core/           # Core functionality
│       └── config.py   # Configuration settings
├── requirements.txt    # Project dependencies
└── README.md          # This file
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the Redis password in `.env`

4. Start the Celery worker:
```bash
# From the project root directory
celery -A app.core.celery_app worker --loglevel=info -P solo
```

5. Run the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. Access the API documentation at: http://localhost:8000/docs

## API Endpoints

### Validation

- POST `/api/validate_query`: Start async validation of an entity name query
  - Request body: `{"query": "string"}`
  - Response: `{"valid": boolean, "task_id": "string"}`

- GET `/api/validate_query/{task_id}`: Get validation result
  - Response: `{"valid": boolean, "sanitized_name": "string", "error_message": "string"}`

## Development Roadmap

1. **Current Implementation**
   - Basic FastAPI setup
   - Query validation endpoint
   - Input sanitization

2. **Next Steps**
   - Add AI-powered validation
   - Implement entity creation
   - Add search functionality
   - Integrate job queue for async processing

## Contributing

Please follow these guidelines when contributing:
1. Create feature branches from `main`
2. Follow PEP 8 style guide
3. Include docstrings and type hints
4. Add tests for new functionality
