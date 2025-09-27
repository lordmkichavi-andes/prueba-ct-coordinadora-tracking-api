from celery import Celery
import os

# Configuración de Celery
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

celery = Celery(
    'tracking_app',
    broker=redis_url,
    backend=redis_url,
    include=[
        'src.infrastructure.external.tasks'
    ]
)

# Configuración de Celery
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hora
    task_routes={
        'src.infrastructure.external.tasks.process_checkpoint': {'queue': 'checkpoints'},
        'src.infrastructure.external.tasks.send_notification': {'queue': 'notifications'},
    }
)

