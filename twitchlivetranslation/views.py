from threading import Event
from django.http import JsonResponse

from deepl_app.views import deepl_request, aws_request
from django.shortcuts import render
from asgiref.sync import async_to_sync
import numpy as np
import pytz
from datetime import datetime
import queue
from datetime import timedelta
SERVER_START_TIME = datetime.now(pytz.utc)
import twitchlivetranslation.settings as settings
from twitchlivetranslation.settings import LISTENING_THREADS_STARTED


# def list_microphone_devices():
#     p = pyaudio.PyAudio()
#     for i in range(p.get_device_count()):
#         device_info = p.get_device_info_by_index(i)
#         if device_info.get('maxInputChannels') > 0:
#             if 'Desktop' in device_info.get('name'):
#                 print(f"Device ID {i}: {device_info.get('name')} - {device_info.get('maxInputChannels')} input channels - {device_info.get('maxOutputChannels')} output channels")
#     p.terminate()
# list_microphone_devices()
    

def index(request):
    # start_listening()
    return render(request, 'index.html')

import twitchlivetranslation.ContinuousRecognizer as ContinuousRecognizer
discord_recognizer = ContinuousRecognizer.ContinuousRecognizer(4)
mic_recognizer = ContinuousRecognizer.ContinuousRecognizer(1) # discord 4 mic 1
def apirequest_translated_text(request):
    try:
        request_time_str = request.headers.get('Request-Time')
        if request_time_str is None:
            return JsonResponse(status=400, data={"error":"Please include Request-Time header in the request. Format: 'YYYY-MM-DDTHH:MM:SS.ssssss+00:00'"})
        # request_time = datetime.fromisoformat(request_time_str)
        # If the datetime string ends with 'Z', replace 'Z' with '+00:00'
        if request_time_str.endswith('Z'):
            request_time_str = request_time_str[:-1] + '+00:00'
        request_time = datetime.strptime(request_time_str, '%Y-%m-%dT%H:%M:%S.%f%z')
    except ValueError:
        # Handle the error or re-raise with a custom message
        return JsonResponse(status=400, data={
            "error": "Request time is too old"
        })
    if request_time < datetime.now(pytz.utc) - timedelta(seconds=1):
        return JsonResponse(status=400, data={
            "error": "Request time is too old"
        })
    
    mic_recognizer.start()
    discord_recognizer.start()
    return JsonResponse({
        "discord": {
            "translated_text": discord_recognizer.last_translated_text,
        },
        "mic": {
            "translated_text": mic_recognizer.last_translated_text,
        }
    })