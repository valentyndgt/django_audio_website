import os
import re
import mimetypes
import json

from django.conf import settings
from django.core import serializers
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, StreamingHttpResponse, \
    HttpResponseForbidden, FileResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic import TemplateView

from rest_framework import status, generics

from .models import Track, get_duration
from .forms import ContactUsForm, TrackUploadForm, TrackCutForm, IdForm, TrackRenameForm
from .serializers import TrackInfoSerializer
from .workers import perform_cut


class AboutUsView(TemplateView):
    template_name = 'app_main/about_us.html'


class ContactUsView(FormView):
    template_name = 'app_main/contact_us.html'
    form_class = ContactUsForm

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()
        return HttpResponseRedirect(reverse('contact_us_done'))


class ContactUsDoneView(TemplateView):
    template_name = 'app_main/contact_us_done.html'


class TrackListView(View):
    def get(self, *args, **kwargs):
        query_param = self.request.GET.get('q')
        track_objects = self.request.user.track_set.all()
        if query_param:
            track_objects = track_objects.filter(name__icontains=query_param.strip())
        # tracks_json = [TrackSerializer(track).data for track in track_objects]
        html = render_to_string(
            template_name='app_main/playlist.html',
            context={'tracks': track_objects},
        )
        return JsonResponse({'data': html})


class HomePageView(View):
    def get(self, *args, **kwargs):
        context = {'user': self.request.user,
                   'profile': self.request.user.profile,
                   'tracks': self.request.user.track_set.all(),
                   'form_cut_track': TrackCutForm(),
                   'id_form': IdForm(),
                   'track_rename_form': TrackRenameForm()}
        return render(self.request, 'app_main/homepage.html', context)

    def post(self, *args, **kwargs):
        def upload_track():
            form = TrackUploadForm(self.request.POST, self.request.FILES)
            if form.is_valid() and self.request.FILES:
                tracks = []
                for file in self.request.FILES.getlist('file'):
                    track = Track.objects.create(file=file, name=file.name,
                                                 user=self.request.user)
                    track.duration = get_duration(track.file.path)
                    track.save()
                    tracks.append(TrackInfoSerializer(track).data)
                data = {'data': tracks}
                return JsonResponse(data, status=status.HTTP_200_OK)
            return JsonResponse({'error': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        def cut_track():
            form = TrackCutForm(self.request.POST)
            if form.is_valid():
                track = form.cleaned_data['track']
                if not self.request.user.is_superuser and track.user != self.request.user:
                    return JsonResponse({'msg': 'forbidden'}, status.HTTP_403_FORBIDDEN)
                new_track = perform_cut(form.cleaned_data, self.request.user)
                if isinstance(new_track, str):
                    return JsonResponse({'error': new_track}, status=status.HTTP_400_BAD_REQUEST)
                return JsonResponse(TrackInfoSerializer(new_track).data, status=status.HTTP_200_OK)
            return JsonResponse({'error': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        def remove_track():
            form = IdForm(self.request.POST)
            if form.is_valid():
                try:
                    track = Track.objects.get(pk=form.cleaned_data['id'])
                    if not self.request.user.is_superuser and track.user != self.request.user:
                        return JsonResponse({'msg': 'forbidden'}, status.HTTP_403_FORBIDDEN)
                    track.delete()
                    return JsonResponse({'msg': 'target deleted'}, status=status.HTTP_204_NO_CONTENT)
                except Track.DoesNotExist:
                    return JsonResponse({'error': 'pk does not exist'}, status=status.HTTP_404_NOT_FOUND)
            return JsonResponse({'error': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        def rename_track():
            form = TrackRenameForm(self.request.POST)
            if form.is_valid():
                try:
                    track = Track.objects.get(pk=form.cleaned_data['id'])
                    if not self.request.user.is_superuser and track.user != self.request.user:
                        return JsonResponse({'msg': 'forbidden'}, status.HTTP_403_FORBIDDEN)
                    track.name = form.cleaned_data['name']
                    track.save()
                    return JsonResponse({'msg': 'target renamed'}, status=status.HTTP_200_OK)
                except Track.DoesNotExist:
                    return JsonResponse({'error': 'pk does not exist'}, status=status.HTTP_404_NOT_FOUND)
            return JsonResponse({'error': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        # determine which form is submitting (based on hidden input called 'action')
        if 'action' not in self.request.POST:
            return JsonResponse({'error': 'action not specified'}, status=status.HTTP_400_BAD_REQUEST)
        action = self.request.POST['action']
        if action == 'upload_file':
            return upload_track()
        elif action == 'cut_track':
            return cut_track()
        elif action == 'remove_track':
            return remove_track()
        elif action == 'rename_track':
            return rename_track()
        return JsonResponse({'error': 'action not supported: {0}'.format(action)}, status=status.HTTP_400_BAD_REQUEST)


class RangeFileIterator:
    def __init__(self, filelike, blksize=8192, offset=0, length=None):
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self.filelike, 'close'):
            self.filelike.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining is None:
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data


class TrackStream(View):
    range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)

    def get(self, *args, **kwargs):
        track_name = kwargs['track_name']
        if track_name == 'placeholder':
            path = settings.PLACEHOLDER_TRACK
        else:
            path = 'user_{0}/tracks/{1}'.format(self.request.user.id, kwargs['track_name'])
            path = os.path.join(settings.MEDIA_ROOT, path)

        range_header = self.request.META.get('HTTP_RANGE', '').strip()
        range_match = self.range_re.match(range_header)
        size = os.path.getsize(path)
        content_type, encoding = mimetypes.guess_type(path)
        content_type = content_type or 'application/octet-stream'
        if range_match:
            first_byte, last_byte = range_match.groups()
            first_byte = int(first_byte) if first_byte else 0
            last_byte = int(last_byte) if last_byte else size - 1
            if last_byte >= size:
                last_byte = size - 1
            length = last_byte - first_byte + 1
            resp = StreamingHttpResponse(RangeFileIterator(open(path, 'rb'), offset=first_byte, length=length),
                                         status=206, content_type=content_type)
            resp['Content-Length'] = str(length)
            resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
        else:
            resp = StreamingHttpResponse(RangeFileIterator(open(path, 'rb')), content_type=content_type)
            resp['Content-Length'] = str(size)
        resp['Accept-Ranges'] = 'bytes'
        return resp


class TrackDownload(View):
    def get(self, *args, **kwargs):
        track = get_object_or_404(Track, id=kwargs['track_id'])
        if not self.request.user.is_superuser and track.user != self.request.user:
            return HttpResponseForbidden()
        return FileResponse(open(track.file.path, 'rb'), as_attachment=True)


class TrackRowHTMLView(View):
    def post(self, *args, **kwargs):
        track_id = json.loads(self.request.body)['track_id']
        try:
            track = Track.objects.get(pk=track_id)
        except Track.DoesNotExist:
            return JsonResponse({'error': 'pk does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return JsonResponse({'data': render_to_string(template_name='app_main/track_row.html', context={'track': track})})
