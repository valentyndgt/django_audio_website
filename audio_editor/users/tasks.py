from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model

from audio_editor.celery import celery_app

# hint : launch with
# celery -A audio_editor worker -l INFO


@celery_app.task
def async_send_email(mail_subject, message, to_email):
    EmailMessage(
        mail_subject, message, to=[to_email]
    ).send()
