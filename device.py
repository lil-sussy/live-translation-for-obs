import sounddevice
for device in sounddevice.query_devices():
    if 'aux' in device['name']:
        # if 'output' in device['name']:
            print(device)
# sounddevice.default.device = 50
# sounddevice.default.device = 'VoiceMeeter Aux Output (VB-Audio VoiceMeeter AUX VAIO), Windows DirectSound'
# sounddevice.default.device = 'VoiceMeeter Aux Output (VB-Audio VoiceMeeter AUX VAIO), Windows WASAPI'
freq = 44100
sample_id = 0
recording = sounddevice.rec(int(5 * freq), 
                samplerate=freq, channels=2)
sounddevice.wait()
sounddevice.play(recording, freq)
sounddevice.wait()