from threading import Event
from django.http import JsonResponse
import speech_recognition as sr
import speech_recognition as sr2

from deepl_app.views import deepl_request
from django.shortcuts import render
import threading
import twitchlivetranslation.consumers as consumers
from asgiref.sync import async_to_sync
import asyncio
import pyaudio
import sounddevice as sd
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
text_array = {
  "microphone": np.array([]),
  "discord": np.array([]),
}

freq = 44100
duration = 5


progress_consumer = consumers.TaskProgressConsumer()

def listenMic():
  recognizer = sr.Recognizer()
  print(sd.DeviceList())
  sample_id = 0
  while(True):
      recording = sd.rec(int(duration * freq), 
                      samplerate=freq, channels=2)
      sd.wait()
      audio_data = array_to_audio(recording, freq)
      threading.Thread(target=speech_to_text_translate, args=(sample_id, "microphone", audio_data, recognizer)).start()
      sample_id = (sample_id + 1) % 4

def array_to_audio(array, sample_rate):
    mono_audio = np.mean(array)
    scaled_audio = np.int16(mono_audio * 32767)
    audio_bytes = scaled_audio.tobytes()
    sample_rate = 44100  # Example sample rate
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
        with sr.Microphone(20) as source:  # discord 3 mic 5
            # read the audio data from the default microphone
            try:
                audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            except sr.WaitTimeoutError:
                continue
            # convert speech to text
            speech_to_text_translate(sample_id, "discord", audio_data, recognizer)
            # threading.Thread(target=speech_to_text_translate, args=(sample_id, "discord", audio_data, recognizer)).start()
            sample_id = (sample_id + 1) % 4

import traceback
def speech_to_text_translate(sample_id, text_id, audio_data, recognizer):
    try:
        if sample_id == 0:
            text_array[text_id] = audio_to_array(audio_data, 44100)
            untranslated_text[text_id] = recognizer.recognize_google(audio_data, language='fr-FR')
            translated_text[text_id] = deepl_request(untranslated_text[text_id], 'EN-US')
        elif sample_id == 2:
            np.append(text_array[text_id], audio_to_array(audio_data, 44100))
            audio = array_to_audio(text_array[text_id], 44100)
            untranslated_text[text_id] = recognizer.recognize_google(audio, language='fr-FR')
            translated_text[text_id] = deepl_request(untranslated_text[text_id], 'EN-US')
        else:
            np.append(text_array[text_id], audio_to_array(audio_data, 44100))
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
            print(f"Device ID {i}: {device_info.get('name')}")
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
    # if not microphone_thread.is_alive():
    #     microphone_thread.start()

def apirequest_translated_text(request):
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