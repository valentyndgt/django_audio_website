from django.shortcuts import get_object_or_404

from rest_framework.permissions import AllowAny
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Track, get_duration
from .serializers import ContactUsSerializer, TrackInfoSerializer, TrackRegionSerializer, FullTrackSerializer
from .workers import perform_cut


class ApiContactUsView(generics.CreateAPIView):
    serializer_class = ContactUsSerializer

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class ApiCutTrack(generics.CreateAPIView):
    serializer_class = TrackRegionSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        new_track = perform_cut(serializer.validated_data, self.request.user)
        if isinstance(new_track, str):
            return Response({'error': new_track}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.validated_data)
        data = TrackInfoSerializer(new_track).data

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class ApiTrackDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FullTrackSerializer
    parser_classes = (MultiPartParser, FormParser)
    queryset = Track.objects.all()


class ApiUploadTrackView(generics.CreateAPIView):
    serializer_class = FullTrackSerializer
    parser_classes = (MultiPartParser, FormParser)

    # !_!
    def create(self, request, *args, **kwargs):
        data = request.data
        data['file'] = request.FILES['file']
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        track = Track.objects.create(file=data['file'], name=data['file'].name,
                                     user=request.user)
        track.duration = get_duration(track.file.path)
        track.save()
        headers = self.get_success_headers(serializer.data)
        return Response(FullTrackSerializer(track).data, status=status.HTTP_201_CREATED, headers=headers)
