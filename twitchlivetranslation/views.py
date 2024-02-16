import speech_recognition as sr

from deepl_app.views import deepl_request
from django.shortcuts import render
import threading
import twitchlivetranslation.consumers as consumers
from asgiref.sync import async_to_sync
import asyncio
import pyaudio

r = sr.Recognizer()
progress_consumer = consumers.TaskProgressConsumer()

def listenMic():
    listen(7)
def listenDiscord():
    listen(7)

def listen(DEVICE_INDEX=0):
    while(True):
        with sr.Microphone() as source:
            # read the audio data from the default microphone
            print("Speak up !")
            audio_data = r.listen(source, timeout=5, phrase_time_limit=5)
            print("Over !")
        # convert speech to text
        threading.Thread(target=speech_to_text_translate, args=(audio_data,)).start()
        

def speech_to_text_translate(audio_data):
    try:
        text = r.recognize_google(audio_data, language='fr-FR')
    except:
        text = "Sorry, I did not get that"
    translation = deepl_request(text, 'en')['translations'][0]['text']
    async_to_sync(progress_consumer.send_message)("translation-text", translation)

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

def index(request):
    async_to_sync(progress_consumer.create_channel)('translation-text')
    threading.Thread(target=socketThread).start()
    # threading.Thread(target=listenMic).start()
    threading.Thread(target=listenDiscord).start()
    return render(request, 'index.html')