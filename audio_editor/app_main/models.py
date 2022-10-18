import os
from mutagen.mp3 import MP3
# import sox

from django.db import models

from users.models import CustomUser, get_user_tracks_path
from users.utils import OverwriteStorage


class ContactUs(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    subject = models.CharField(max_length=200)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Contact us'

    def __str__(self):
        return '{0}: {1}'.format(self.user.email, self.subject)

    def email(self):
        return self.user.email


class Track(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    file = models.FileField(upload_to=get_user_tracks_path, storage=OverwriteStorage(), max_length=1024)
    name = models.TextField()
    duration = models.PositiveIntegerField(null=True, default=None)

    def __str__(self):
        return '{0}'.format(self.name)

    @property
    def filename(self):
        return os.path.basename(self.file.name)


class TrackRegion(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)

    time_start = models.IntegerField()
    time_end = models.IntegerField()


def get_duration(path):
    def to_millis(duration):
        if duration is not None:
            return int(duration * 1000)
        return None

    def mutagen_length(path):
        try:
            audio = MP3(path)
            length = audio.info.length
            return length
        except:
            return None

    # def sox_length(path):
    #     try:
    #         length = sox.file_info.duration(path)
    #         return length
    #     except:
    #         return None

    duration = to_millis(mutagen_length(path))
    if duration is not None:
        return duration
    # return to_milis(sox_length(path))
    return None
