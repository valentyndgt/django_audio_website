from django import forms

from .models import ContactUs, Track, TrackRegion


class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ('subject', 'message')


class TrackUploadForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ('file',)


class TrackCutForm(forms.ModelForm):
    class Meta:
        model = TrackRegion
        fields = '__all__'


class IdForm(forms.Form):
    id = forms.IntegerField()


class TrackRenameForm(forms.ModelForm):
    id = forms.IntegerField()

    class Meta:
        model = Track
        fields = ('name', )
