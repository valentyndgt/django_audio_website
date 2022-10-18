from django.urls import path

from rest_framework_social_oauth2.views import TokenView, ConvertTokenView, RevokeTokenView, invalidate_sessions

from .views_api import ApiSignUpView, ApiPasswordResetView, ApiProfileView


urlpatterns = [
    path('token/', TokenView.as_view(), name="token"),                                   # api login
    path('signup/', ApiSignUpView.as_view(), name='api_signup'),
    path('password-reset/', ApiPasswordResetView.as_view(), name='api_password_reset'),
    path('convert-token/', ConvertTokenView.as_view(), name="convert_token"),            # api social login
    path('revoke-token/', RevokeTokenView.as_view(), name="revoke_token"),               # api logout
    path('invalidate-sessions/', invalidate_sessions, name="invalidate_sessions"),  # purge sessions on all devices

    path('profile/', ApiProfileView.as_view(), name='api_profile'),
]
