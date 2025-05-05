from celery import Celery
from celery.schedules import crontab

from app.config import settings

app = Celery(
    "price_tracker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.price_checks"]
)

# Configure Celery
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_max_tasks_per_child=100,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True
)

# Scheduled tasks
app.conf.beat_schedule = {
    'check-prices-every-6-hours': {
        'task': 'app.tasks.price_checks.check_all_prices',
        'schedule': crontab(minute=0, hour='*/6'),
        'options': {'queue': 'periodic'}
    },
    'train-models-weekly': {
        'task': 'app.tasks.price_checks.retrain_all_models',
        'schedule': crontab(day_of_week=0, hour=3),  # Sunday at 3AM
        'options': {'queue': 'periodic'}
    }
}

if __name__ == '__main__':
    app.start()