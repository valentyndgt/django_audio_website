from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django import forms

from .models import Profile


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Email',)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')


class RequestPasswordResetForm(forms.Form):
    email = forms.EmailField(max_length=200,)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar', 'bg_picture')
