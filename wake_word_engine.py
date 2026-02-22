import pyaudio
import numpy as np
import threading
from openwakeword.model import Model

class WakeWordEngine:
    def __init__(self, on_wake_callback):
        self.callback = on_wake_callback
        self.running = False
        # Downloads ~50MB model automatically on first run, then offline forever
        self.model = Model(wakeword_models=['hey_jarvis'])
        self.RATE = 16000
        self.CHUNK = 1280  # 80ms chunks

    def start(self):
        self.running = True
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()
        print('[WAKE] Always listening... Say: hey jarvis')

    def _loop(self):
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        while self.running:
            audio_chunk = np.frombuffer(
                stream.read(self.CHUNK, exception_on_overflow=False),
                dtype=np.int16
            )
            prediction = self.model.predict(audio_chunk)
            for word, score in prediction.items():
                if score > 0.5:
                    print(f'[WAKE] Detected: {word} (confidence: {score:.2f})')
                    self.callback()
                    self.model.reset()
                    break
        stream.stop_stream()
        stream.close()
        pa.terminate()

    def stop(self):
        self.running = False
