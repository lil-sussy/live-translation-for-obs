from threading import Event
import speech_recognition as sr

from deepl_app.views import deepl_request
from django.shortcuts import render
import threading
import twitchlivetranslation.consumers as consumers
from asgiref.sync import async_to_sync
import asyncio
import pyaudio

progress_consumer = consumers.TaskProgressConsumer()

def listenMic():
    listen("microphone", 5)
def listenDiscord():
    listen("discord", 3)

def listen(text_id, DEVICE_INDEX=0):
    recognizer = sr.Recognizer()
    while(True):
        with sr.Microphone(DEVICE_INDEX) as source:
            # read the audio data from the default microphone
            print("Speak up !")
            try:
                audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                async_to_sync(progress_consumer.send_json)("translation-text", {"text": "xddddddddddddddddd", "id": text_id})
            except sr.WaitTimeoutError:
                print("Timeout !")
                continue
            print("Over !")
            # convert speech to text
            threading.Thread(target=speech_to_text_translate, args=(text_id, audio_data, recognizer)).start()
      

def speech_to_text_translate(text_id, audio_data, recognizer):
    try:
        text = recognizer.recognize_google(audio_data, language='fr-FR')
        translation = deepl_request(text, 'en')['translations'][0]['text']
        async_to_sync(progress_consumer.send_json)("translation-text", {"text": translation, "id": text_id})
    except:
        text = "Sorry, I did not get that"

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
    # threading.Thread(target=send_simple_message).start()
    # threading.Thread(target=listenDiscord).start()
    return render(request, 'index.html')