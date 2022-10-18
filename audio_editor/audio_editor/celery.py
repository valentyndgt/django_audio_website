import os
from celery import Celery

# hint : launch with
# celery -A audio_editor worker -l INFO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'audio_editor.settings')

celery_app = Celery('audio_editor')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()
