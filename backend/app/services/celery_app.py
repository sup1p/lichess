from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "lichess",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.beat_schedule = {
    "sync-games": {
        "task": "app.tasks.sync_recent_games",
        "schedule": 60.0,
    }
}

celery_app.autodiscover_tasks(["app.tasks"])
