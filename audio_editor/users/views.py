from django.contrib.auth import views as auth_views
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status

from .utils import send_email_account_activation, send_email_password_reset
from .forms import LoginForm, SignUpForm, RequestPasswordResetForm, ProfileForm


class LoginView(auth_views.LoginView):
    template_name = 'users/login.html'
    form_class = LoginForm


class LogoutView(auth_views.LogoutView):
    template_name = 'users/logout.html'


class SignUpView(View):
    signup_template_name = 'users/signup.html'
    email_template_name = 'users/account_activation_email.html'
    notification_template_name = 'users/account_activation_notification.html'

    def get(self, *args):
        return render(self.request, self.signup_template_name, {'form': SignUpForm()})

    def post(self, *args):
        form = SignUpForm(self.request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False                          # user is not active until email confirmation link clicked
            user.save()
            email = form.cleaned_data.get('email')
            send_email_account_activation(self.request, user, email)
            return HttpResponseRedirect(reverse('signup_done'))
        return render(self.request, self.signup_template_name, {'form': form})


class SignUpDoneView(TemplateView):
    template_name = 'users/account_activation_notification.html'


class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        user_model = get_user_model()
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = user_model.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, user_model.DoesNotExist):
            user = None
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return HttpResponseRedirect(reverse('login'))
        else:
            return render(request, 'users/account_activation_link_invalid.html')


class PasswordResetView(View):
    user_model = get_user_model()
    template_name = 'users/password_reset.html'
    subject_template_name = 'users/password_reset_subject.txt'
    email_template_name = 'users/password_reset_email.html'
    notification_template_name = 'users/password_reset_done.html'

    def get(self, *args):
        return render(self.request, self.template_name, {'form': RequestPasswordResetForm()})

    def post(self, *args):
        form = RequestPasswordResetForm(self.request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = self.user_model.objects.filter(email=email, is_active=True).first()
            if user is not None:
                send_email_password_reset(self.request, user, email)
            return HttpResponseRedirect(reverse('password_reset_done'))
        return render(self.request, self.template_name, {'form': form})


class PasswordResetDoneView(TemplateView):
    template_name = 'users/password_reset_done.html'


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'


class UserProfileEditView(TemplateView):
    template_name = 'users/user_profile_edit.html'

    def get(self, *args, **kwargs):
        profile = self.request.user.profile
        form = ProfileForm(instance=profile)
        return render(self.request, self.template_name,
                      {'form': form, 'profile': profile})

    def post(self, *args, **kwargs):
        form = ProfileForm(self.request.POST, self.request.FILES, instance=self.request.user.profile)
        if form.is_valid():
            form.save()
            return JsonResponse({'msg': 'avatar changed'}, status=status.HTTP_200_OK)
        return JsonResponse({'error': form.errors}, status=status.HTTP_400_BAD_REQUEST)
