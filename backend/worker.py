import os
from celery import Celery
from services.media_engine import process_media

broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery("memorial_worker", broker=broker_url, backend=result_backend)

@celery_app.task
def process_uploaded_media_task(media_id: int):
    # This will run the extraction pipeline via deepface
    process_media(media_id)
