import speech_recognition as sound_recognition
import threading
import pyaudio
import sounddevice
import queue
import numpy as np
from deepl_app.views import aws_request

class ContinuousRecognizer:
    def __init__(self, device_index, source_lang='fr-FR', target_lang='en-US'):
        self.device_index = device_index
        self.translate_queue = queue.Queue()
        self.recognizer = sound_recognition.Recognizer()
        self.running = True
        self.frequency = 24000
        self.frame_buffer_size = 1024
        self.listen_thread = threading.Thread(target=self.audio_capture)
        self.audio_process_thread = threading.Thread(target=self.process_audio)
        self.translate_thread = threading.Thread(target=self.translate_text_queue)
        self.source_language = source_lang
        self.target_language = target_lang
        self.last_translated_text = ""
        self.silence_threshold = 500
        self.audio_queue = queue.Queue()
        self.is_buffer_empty = True
        self.has_sentence_begun = False

    def audio_capture(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=self.frequency,
                        input=True,
                        frames_per_buffer=self.frame_buffer_size,
                        input_device_index=self.device_index)

        print(f"Listening to device {self.device_index}")

        while self.running:
            data = stream.read(self.frame_buffer_size, exception_on_overflow=False)
            if self.is_buffer_empty:
                audio_data = np.frombuffer(data, dtype=np.int16)
                audio_data = np.abs(audio_data)
                self.has_sentence_begun = len(audio_data) > 0 and np.mean(audio_data) > self.silence_threshold
                if self.has_sentence_begun:
                    self.audio_queue.put(data)
            else:
                self.audio_queue.put(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def detect_speech_end(self, audio_buffer, sample_rate=44100, silence_threshold=500, min_silence_duration=0.5):
        """
        Detects if the end of the audio buffer contains a silence indicating the end of a sentence.

        :param audio_buffer: The audio data as a bytearray.
        :param sample_rate: The sample rate of the audio data.
        :param silence_threshold: The volume level that is considered as silence.
        :param min_silence_duration: Minimum duration in seconds of silence to consider as the end of a sentence.
        :return: True if the end of a sentence is detected, False otherwise.
        """
        # Convert the bytearray audio buffer to a numpy array for analysis
        audio_data = np.frombuffer(audio_buffer, dtype=np.int16)

        # Calculate the absolute value to get the volume level and average it
        volume = np.abs(audio_data).mean()

        # Determine the number of samples that constitute the minimum silence duration
        num_samples_silence = int(sample_rate * min_silence_duration)

        if len(audio_data) < num_samples_silence:
            # Not enough data to determine if end of sentence
            return False

        # Analyze the last `num_samples_silence` samples for silence
        end_samples = audio_data[-num_samples_silence:]
        end_volume = np.abs(end_samples).mean()

        # Check if the volume in the last segment is below the silence threshold
        if end_volume < silence_threshold:
            return True  # Silence detected, indicating potential end of a sentence
        else:
            return False
          
    def trim_silence(self, audio_data, threshold=500, sample_rate=16000):
        """
        Trims silence from the beginning of an audio buffer.

        :param audio_data: The audio data as a bytearray.
        :param threshold: The volume level below which audio is considered silence.
        :param sample_rate: The sample rate of the audio data.
        :return: Trimmed audio data as a bytearray.
        """
        # Convert the bytearray to a numpy array for audio signal processing
        audio_array = np.frombuffer(audio_data, dtype=np.int16)

        # Find the first index where the absolute value of the signal exceeds the threshold
        start_index = np.where(np.abs(audio_array) > threshold)[0]

        if len(start_index) > 0:
            # If a start index is found, trim the silence from the start of the audio
            trimmed_audio_array = audio_array[start_index[0]:]
            # Convert the trimmed numpy array back to bytearray for compatibility
            trimmed_audio_data = trimmed_audio_array.tobytes()
            return trimmed_audio_data
        else:
            # If no start index is found (i.e., the entire audio is below the threshold), return the original audio
            return audio_data

    def process_audio(self):
        audio_buffer = bytearray()
        while self.running:
            if not self.audio_queue.empty():
                data = self.audio_queue.get()
                audio_buffer.extend(data)
                
                self.is_buffer_empty = len(audio_buffer) == 0
                
                if self.detect_speech_end(audio_buffer):
                    # Convert buffered audio to AudioData for recognition
                    audio_data = sound_recognition.AudioData(bytes(audio_buffer), self.frequency, 2)
                    audio_buffer = bytearray()  # Clear the buffer after processing
                    try:
                        text = self.recognizer.recognize_google(audio_data, language=self.source_language)
                        print(f"Device {self.device_index}: \"{text}\"")
                        self.translate_queue.put(text)
                    except sound_recognition.UnknownValueError:
                        pass
                    except sound_recognition.RequestError as e:
                        print(f"Could not request results from device {self.device_index}; {e}")
                    
                    # Clear the buffer after processing
                    audio_buffer.clear()

    def translate_text_queue(self):
        while self.running:
            if not self.translate_queue.empty():
                text = self.translate_queue.get()
                try:
                    self.last_translated_text = aws_request(text, self.source_language, self.target_language)
                    print(f"Device {self.device_index}: \"{self.last_translated_text}\"")
                except sound_recognition.RequestError as e:
                    print(f"Could not request translation; {e}")

    def start(self):
        if self.listen_thread.is_alive() or self.audio_process_thread.is_alive() or self.translate_thread.is_alive():
            return
        self.listen_thread.start()
        self.audio_process_thread.start()
        self.translate_thread.start()

    def stop(self):
        self.running = False