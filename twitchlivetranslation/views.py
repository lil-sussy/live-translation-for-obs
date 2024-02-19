from threading import Event
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

freq = 44100
duration = 5


progress_consumer = consumers.TaskProgressConsumer()

def listenMic():
  recognizer = sr.Recognizer()
  print(sd.DeviceList())
  while(True):
      print("Speak up mic !")
      recording = sd.rec(int(duration * freq), 
                      samplerate=freq, channels=2)
      sd.wait()
      mono_audio = np.mean(recording, axis=1)

      scaled_audio = np.int16(mono_audio * 32767)

      audio_bytes = scaled_audio.tobytes()

      sample_rate = 44100  # Example sample rate
      audio_data = sr.AudioData(audio_bytes, sample_rate, 2)
      print("Over mic !")
      threading.Thread(target=speech_to_text_translate, args=("microphone", audio_data, recognizer)).start()
  
def listenDiscord():
    recognizer = sr.Recognizer()
    while(True):
        with sr.Microphone(20) as source:  # discord 3 mic 5
            # read the audio data from the default microphone
            print("Speak up discord !")
            try:
                audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            except sr.WaitTimeoutError:
                print("Timeout discord !")
                continue
            print("Over discord !")
            # convert speech to text
            threading.Thread(target=speech_to_text_translate, args=("discord", audio_data, recognizer)).start()      

def speech_to_text_translate(text_id, audio_data, recognizer):
    try:
        text = recognizer.recognize_google(audio_data, language='fr-FR')
        translation = deepl_request(text, 'en')['translations'][0]['text']
        async_to_sync(progress_consumer.send_json)("translation-text", {"text": translation, "id": text_id})
    except:
        print("Sorry, I did not get that")

def socketThread():
    asyncio.run(consumers.runserver(progress_consumer))
    
def list_microphone_devices():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info.get('maxInputChannels') > 0:
            print(f"Device ID {i}: {device_info.get('name')}")
    p.terminate()
list_microphone_devices()

def send_simple_message():
    while True:
        async_to_sync(progress_consumer.send_json)("translation-text", {"text": "sdfsfsdfsdf", "id": "discord"})
    

def index(request):
    async_to_sync(progress_consumer.create_channel)('translation-text')
    threading.Thread(target=socketThread).start()
    threading.Thread(target=listenMic).start()
    threading.Thread(target=listenDiscord).start()
    return render(request, 'index.html')