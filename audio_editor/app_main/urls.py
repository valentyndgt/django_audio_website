from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import HomePageView, AboutUsView, ContactUsView, ContactUsDoneView, TrackStream, \
    TrackListView, TrackDownload, TrackRowHTMLView


urlpatterns = [
    path('about/', AboutUsView.as_view(), name='about_us'),
    path('contact_us/', login_required(ContactUsView.as_view()), name='contact_us'),
    path('contact_us/thanks/', login_required(ContactUsDoneView.as_view()), name='contact_us_done'),
    path('', login_required(HomePageView.as_view()), name='homepage'),
    path('stream/<track_name>/', TrackStream.as_view(), name='stream'),
    path('query/', TrackListView.as_view(), name='query_tracks'),
    path('download/<track_id>/', TrackDownload.as_view(), name='download_track'),
    path('html/track_row/', TrackRowHTMLView.as_view(), name='html_track_row'),
]
