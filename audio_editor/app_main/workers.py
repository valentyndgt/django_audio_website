from pydub import AudioSegment
import os

from django.conf import settings
from django.core.files import File

from .models import Track, get_duration


def perform_cut(data, user):
    # define input params
    track = data['track']
    time_start = data['time_start']
    time_end = data['time_end']

    # check if time_start and time_end are legit. if not, return error string
    if time_start < 0 or time_end < 0 or time_start >= time_end \
            or time_start >= track.duration or time_end > track.duration:
        return 'err: invalid time_start or time_end params'

    # define file names and paths
    input_filepath = os.path.join(settings.MEDIA_ROOT, str(track.file))
    target_folder = os.path.dirname(input_filepath)
    input_filename, extension = os.path.splitext(track.filename)
    if extension[0] == '.':
        extension = extension[1:]
    track_name = track.name
    if track_name.endswith('.' + extension):
        track_name = track_name[:-(len(extension) + 1)]
    result_trackname = make_result_filename('cut', track_name, extension,
                                            time_start=time_start, time_end=time_end)
    result_filename = result_trackname.replace(' ', '_')
    result_filepath = os.path.join(target_folder, result_filename)

    # load audio segment and cut
    audio_segment = AudioSegment.from_file(input_filepath, extension)
    segment_cut = audio_segment[time_start:time_end]
    # save audio segment as result file
    file_handle = segment_cut.export(result_filepath, extension)

    # create Track object
    track = Track.objects.create(user=user)
    track.file = File(file_handle)
    track.name = result_trackname
    track.duration = get_duration(track.file.path)
    track.save()

    file_handle.close()
    return track


def make_result_filename(operation, input_filename, extension, replace_spaces=False, **kwargs):
    result = input_filename + ' ' + operation
    if operation == 'cut':
        result += '_' + turn_millis_to_mmss_string(kwargs['time_start']) \
                  + '_' + turn_millis_to_mmss_string(kwargs['time_end'])
    result += '.' + extension
    if replace_spaces:
        result = result.replace(' ', '_')
    return result


def turn_millis_to_mmss_string(millis):
    # assumes no hour long tracks
    seconds = millis / 1000
    mm = int(seconds // 60)
    ss = int(seconds % 60)
    return '{0}m{1}s'.format(mm, ss)
