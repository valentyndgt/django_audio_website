import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site

from .tasks import async_send_email


def send_email_account_activation(request, user, to_email):
    send_email_uidb64_token(request, user, to_email,
                            url_name='activate_account',
                            mail_subject='Activate your Audio Editor Account',
                            email_template_name='users/account_activation_email.html')


def send_email_password_reset(request, user, to_email):
    send_email_uidb64_token(request, user, to_email,
                            url_name='password_reset_confirm',
                            mail_subject='Audio Editor: password reset',
                            email_template_name='users/password_reset_email.html')


def send_email_uidb64_token(request, user, to_email, url_name, mail_subject, email_template_name):
    message = render_to_string(email_template_name, {
        'username': user.username,
        'href': make_uidb64_token_url_for_user(request, user, url_name),
    })
    async_send_email.delay(mail_subject, message, to_email)     # celery


def make_uidb64_token_url_for_user(request, user, url_name):
    """
    make url such as
    {{ protocol }}://{{ domain }}{% url 'activate_account' uidb64=uid token=token %}
    {{ protocol }}://{{ domain }}{% url 'password_reset_confirm' uidb64=uid token=token %}
    """
    domain = get_current_site(request).domain
    protocol = request.scheme
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    return '{0}://{1}'.format(protocol, domain) + reverse(url_name, args=(uidb64, token))


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, **kwargs):
        # If the filename already exists, remove it as if it was a true file system
        # https://stackoverflow.com/questions/9522759/imagefield-overwrite-image-file-with-same-name
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name
