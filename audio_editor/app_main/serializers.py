from rest_framework import serializers

from .models import ContactUs, Track, TrackRegion


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ('subject', 'message', 'date')


class TrackInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ('id', 'filename', 'name', 'duration')


class FullTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        exclude = ('user', )


class TrackRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackRegion
        fields = '__all__'

