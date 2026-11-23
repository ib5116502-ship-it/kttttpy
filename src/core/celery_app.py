from celery import Celery

from src.core.config import settings

celery_app = Celery(
    "kt6_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.tasks.notifications"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)