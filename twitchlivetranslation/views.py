import speech_recognition as sr


from django.shortcuts import render
import threading

r = sr.Recognizer()
def speech_to_text():
    while(True):
        with sr.Microphone() as source:
            # read the audio data from the default microphone
            print("Speak up !")
            audio_data = r.listen(source, timeout=5, phrase_time_limit=5)
            print("Over !")
        # convert speech to text
        try:
            text = r.recognize_google(audio_data, language='fr-FR')
        except:
            text = "Sorry, I did not get that"
        print(text)

def index(request):
    voice_recording_thread = threading.Thread(target=speech_to_text)
    voice_recording_thread.start()
    return render(request, 'index.html')