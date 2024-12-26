from celery import Celery
from app.core.config import get_settings

settings = get_settings()

# Initialize Celery
celery_app = Celery(
    "yoshka_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,  # Retry connection on startup
)
