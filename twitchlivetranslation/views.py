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

freq = 44100
duration = 5


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
  sample_id = 0
  while(True):
      recording = sounddevice.rec(int(duration * 48000), 
                      samplerate=freq, channels=2)
      sounddevice.wait()
      audio_data = array_to_audio(recording, 48000)
      threading.Thread(target=speech_to_text_translate, args=(sample_id, "microphone", audio_data, recognizer, 48000)).start()
      sample_id = (sample_id + 1) % 4

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
    sample_id = 0
    while(True):
        with sr.Microphone(1) as source:  # discord 4 mic 1
            # read the audio data from the default microphone
            try:
                audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            except sr.WaitTimeoutError:
                continue
            # convert speech to text
            # speech_to_text_translate(sample_id, "discord", audio_data, recognizer)
            threading.Thread(target=speech_to_text_translate, args=(sample_id, "discord", audio_data, recognizer)).start()
            sample_id = (sample_id + 1) % 4

import traceback
def speech_to_text_translate(sample_id, text_id, audio_data, recognizer, frequency=44100):
    try:
        if sample_id == 0:
            text_array[text_id] = audio_to_array(audio_data, frequency)
            untranslated_text[text_id] = recognizer.recognize_google(audio_data, language='fr-FR')
            previous_translated_text[text_id] = translated_text[text_id]
            translated_text[text_id] = deepl_request(untranslated_text[text_id], 'EN-US')
        elif sample_id == 2:
            np.append(text_array[text_id], audio_to_array(audio_data, frequency))
            audio = array_to_audio(text_array[text_id], frequency)
            untranslated_text[text_id] = recognizer.recognize_google(audio, language='fr-FR')
            translated_text[text_id] = aws_request(untranslated_text[text_id], 'FR-FR', 'EN-US')
        else:
            np.append(text_array[text_id], audio_to_array(audio_data, frequency))
            untranslated_text[text_id] += " " + recognizer.recognize_google(audio_data, language='fr-FR')
            translated_text[text_id] = deepl_request(untranslated_text[text_id], 'EN-US')
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
    start_listening()
    return render(request, 'index.html')
  
microphone_thread = threading.Thread(target=listenMic)
discord_thread = threading.Thread(target=listenDiscord)

def start_listening():
    if not discord_thread.is_alive():
        discord_thread.start()
    if not microphone_thread.is_alive():
        microphone_thread.start()

def apirequest_translated_text(request):
    # if not discord_thread.is_alive():
    #       discord_thread.start()
    # start_listening()
    return JsonResponse({
        "discord": {
            "raw_text": untranslated_text["discord"],
            "translated_text": translated_text["discord"]
        },
        "mic": {
            "raw_text": untranslated_text["microphone"],
            "translated_text": translated_text["microphone"]
        }
    })