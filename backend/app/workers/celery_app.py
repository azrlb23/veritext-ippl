try:
    from celery import Celery
except ImportError:
    class MockCeleryControl:
        def revoke(self, *args, **kwargs):
            pass

    class Celery:
        def __init__(self, *args, **kwargs):
            self.conf = {}
            self.control = MockCeleryControl()

        def task(self, *args, **kwargs):
            def decorator(f):
                f.delay = lambda *a, **k: type("TaskResult", (), {"id": f"mock-{id(f)}"})()
                return f
            return decorator

from app.core.config import settings

celery_app = Celery(
    "veritext_ai_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Jakarta",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes hard limit
    task_soft_time_limit=1500,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=86400,  # 24 hours TTL to avoid Redis key accumulation
    broker_connection_retry_on_startup=True,
    beat_schedule={
        "reap_zombie_tasks_periodic": {
            "task": "app.workers.tasks.reap_zombie_tasks",
            "schedule": 600.0,  # Every 10 minutes
        },
    },
)
