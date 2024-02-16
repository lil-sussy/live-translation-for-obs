# live-translation-for-obs

This project is a django server than runs locally (not remotely yet) takes your microphone stream on the backend as input and sends live translation of everything said in previous 5s to the frontend (localhost:8000) with white dubs over black background.
It uses pyaudio and the library speech_recogntion and also the deepl.com api (you need an api key). For unlimited translation per months the fees starts at around 7$. The free version only allows 500 000 characters a month.

## Demo: 

## Pre-requisites
- OBS
- deepl free api key


## Installation 1: Get the deepl api key

1. go to https://www.deepl.com/en/docs-api
2. create an account (they will ask your credit card info even for the free tier)
3. go account and get the key at the bottom

## Installation 2: start the local python django server

1. go to the server directory
2. run server by running (on windows) *python manage.py runserver* on the console (no admin required)
3. NOTE the audio ID(s) corresponding to your recording device(s)
4. in the twitchlivetranslation/settings.py replace the two first python variable id with your 1 or 2 audio devices
5. stop (ctrl + c) and re-run server

## Installation 3: Create the OBS source

Now that you have the live translation server running on your machine you can start the recording and start translating. The translation starts as soon as something (obs) goes to the address *http://localhost:8000*

For this, simply add a browser source on OBS to this url.


## Known issues

- no 2 devices support yet.
