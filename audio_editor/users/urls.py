from django.urls import path, include
from django.contrib.auth.decorators import login_required

from .views import LoginView, LogoutView, SignUpView, SignUpDoneView, ActivateAccountView, \
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView, \
    UserProfileEditView


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signup/done/', SignUpDoneView.as_view(), name='signup_done'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate_account'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('social-auth/', include('social_django.urls', namespace='social')),

    path('profile/', UserProfileEditView.as_view(), name='user_profile'),
]
