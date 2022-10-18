import os

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    email = models.EmailField('email address', unique=True)


def get_user_avatars_path(instance, filename):
    return 'user_{0}/avatars/{1}'.format(instance.user.id, os.path.basename(filename))


def get_user_profile_bg_img_path(instance, filename):
    return 'user_{0}/profile_bg/{1}'.format(instance.user.id, os.path.basename(filename))


def get_user_tracks_path(instance, filename):
    return 'user_{0}/tracks/{1}'.format(instance.user.id, os.path.basename(filename))


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True)
    moto = models.CharField(max_length=64, blank=True)
    avatar = models.ImageField(upload_to=get_user_avatars_path, blank=True, null=True)
    bg_picture = models.ImageField(upload_to=get_user_profile_bg_img_path, blank=True, null=True)

    def __str__(self):
        return self.user.username + ' ' + self.user.email


@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
