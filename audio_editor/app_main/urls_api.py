from django.urls import path, include

from .views_api import ApiContactUsView, ApiCutTrack, ApiTrackDetailView, ApiUploadTrackView


urlpatterns = [
    path('contact-us/', ApiContactUsView.as_view(), name='api_contact_us'),
    path('cut-track/', ApiCutTrack.as_view(), name='cut_track'),
    path('track/<int:pk>/', ApiTrackDetailView.as_view(), name='api_track'),
    path('upload-track/', ApiUploadTrackView.as_view(), name='upload_track'),
]
