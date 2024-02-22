from threading import Event
from django.http import JsonResponse
import speech_recognition as sr
import speech_recognition as sr2

from deepl_app.views import deepl_request, aws_request
from django.shortcuts import render
import threading
import twitchlivetranslation.consumers as consumers
from asgiref.sync import async_to_sync
import asyncio
import pyaudio
import sounddevice
from scipy.io.wavfile import write
import wavio as wv
import numpy as np
import pytz
from datetime import datetime
from datetime import timedelta
SERVER_START_TIME = datetime.now(pytz.utc)
import twitchlivetranslation.settings as settings
from twitchlivetranslation.settings import LISTENING_THREADS_STARTED


untranslated_text = {
  "microphone": "",
  "discord": "",
}
translated_text = {
  "microphone": "",
  "discord": "",
}
previous_translated_text = {
  "microphone": "",
  "discord": "",
}
text_array = {
  "microphone": np.array([]),
  "discord": np.array([]),
}
sample_ids = {
  "microphone": 0,
  "discord": 0,
}

freq = 44100
duration = 2
SOURCE_LANG = 'fr-FR'
TARGET_LANG = 'en-US'


progress_consumer = consumers.TaskProgressConsumer()

def listenMic():
  recognizer = sr.Recognizer()
  for device in sounddevice.query_devices():
      if 'aux' in device['name']:
          # if 'output' in device['name']:
              print(device)
  # sounddevice.default.device = 50
  # sounddevice.default.device = 'VoiceMeeter Aux Output (VB-Audio VoiceMeeter AUX VAIO), Windows DirectSound'
  # sounddevice.default.device = 'VoiceMeeter Aux Output (VB-Audio VoiceMeeter AUX VAIO), Windows WASAPI'
  sample_ids["microphone"] = 0
  while(True):
      recording = sounddevice.rec(int(duration * freq), 
                      samplerate=freq, channels=2)
      sounddevice.wait()
      audio_data = array_to_audio(recording, freq)
      threading.Thread(target=speech_to_text_translate, args=(sample_ids["microphone"], "microphone", audio_data, recognizer, freq)).start()
      sample_ids["microphone"] = (sample_ids["microphone"] + 1) % 4

def array_to_audio(array, sample_rate):
    # If array is 2D (stereo), you should convert it to mono by averaging the channels
    if array.ndim == 2:
        mono_audio = np.mean(array, axis=1)
    else:
        mono_audio = array

    # Scale the mono audio array to int16
    scaled_audio = np.int16(mono_audio * 32767)

    # Convert the int16 array to bytes
    audio_bytes = scaled_audio.tobytes()

    # Create an AudioData object
    return sr.AudioData(audio_bytes, sample_rate, 2)

def audio_to_array(audio_data, sample_rate):
    audio_bytes = audio_data.frame_data
    # Step 2: Convert bytes to int16 NumPy array
    audio_array_int16 = np.frombuffer(audio_bytes, dtype=np.int16)
    # Optional Step 3: Scale to float32 range -1.0 to 1.0
    return audio_array_int16.astype(np.float32) / np.iinfo(np.int16).max

def listenDiscord():
    recognizer = sr.Recognizer()
    sample_ids['discord'] = 0
    while(True):
        with sr.Microphone(1) as source:  # discord 4 mic 1
            # read the audio data from the default microphone
            try:
                audio_data = recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            threading.Thread(target=speech_to_text_translate, args=(sample_ids['discord'], "discord", audio_data, recognizer)).start()
            sample_ids['discord'] = (sample_ids['discord'] + 1) % 4

import traceback
def recognize_text(recognizer, audio_data, source_lang):
    try:
        return recognizer.recognize_google(audio_data, language=source_lang)
    except Exception as e:
        return ""

def speech_to_text_translate(sample_id, text_id, audio_data, recognizer, frequency=44100):
    try:
        new_text_is_empty = False
        if sample_id == 0:
            text_array[text_id] = audio_to_array(audio_data, frequency)
            untranslated_text[text_id] = recognize_text(recognizer, audio_data, SOURCE_LANG)
            new_text_is_empty = untranslated_text[text_id] == ""
            translated_text[text_id] = aws_request(untranslated_text[text_id], SOURCE_LANG, TARGET_LANG)
        elif sample_id == 1:
            np.append(text_array[text_id], audio_to_array(audio_data, frequency))
            new_text = recognize_text(recognizer, audio_data, SOURCE_LANG)
            new_text_is_empty = len(new_text) == 0
            untranslated_text[text_id] += " " + new_text
            translated_text[text_id] = aws_request(untranslated_text[text_id], SOURCE_LANG, TARGET_LANG)
        if new_text_is_empty or sample_id == 2:
            sample_ids[text_id] = 0
            np.append(text_array[text_id], audio_to_array(audio_data, frequency))
            audio = array_to_audio(text_array[text_id], frequency)
            untranslated_text[text_id] = recognize_text(recognizer, audio, SOURCE_LANG)
            previous_translated_text[text_id] = aws_request(untranslated_text[text_id], SOURCE_LANG, TARGET_LANG)
            untranslated_text[text_id] = ""
            text_array[text_id] = np.array([])
            translated_text[text_id] = ""
        return sample_id
    except Exception as e:
        print(traceback.format_exc())
        pass

def list_microphone_devices():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info.get('maxInputChannels') > 0:
            if 'Desktop' in device_info.get('name'):
                print(f"Device ID {i}: {device_info.get('name')} - {device_info.get('maxInputChannels')} input channels - {device_info.get('maxOutputChannels')} output channels")
    p.terminate()
list_microphone_devices()
    

def index(request):
    # start_listening()
    return render(request, 'index.html')
  
microphone_thread = threading.Thread(target=listenMic)
discord_thread = threading.Thread(target=listenDiscord)

def start_listening():
    try:
        if LISTENING_THREADS_STARTED:
            return
    except UnboundLocalError as e:
         return
    settings.LISTENING_THREADS_STARTED = True
    if not discord_thread.is_alive():
        discord_thread.start()
    if not microphone_thread.is_alive():
        microphone_thread.start()

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
    start_listening()
    return JsonResponse({
        "discord": {
            "raw_text": untranslated_text["discord"],
            "translated_text": translated_text["discord"],
            "previous_translated_text": previous_translated_text["discord"],
        },
        "mic": {
            "raw_text": untranslated_text["microphone"],
            "translated_text": translated_text["microphone"],
            "previous_translated_text": previous_translated_text["microphone"],
        }
    })