"""
JARVIS v1.0 — Voice Layer
Hotkey activation + Speech-to-Text (faster-whisper)
Handles all audio input: voice recording, silence detection, transcription.
"""

import threading
import queue
import numpy as np
import sounddevice as sd
from config import (
    HOTKEY,
    WHISPER_MODEL_SIZE,
    WHISPER_DEVICE,
    WHISPER_COMPUTE_TYPE,
    SILENCE_THRESHOLD,
    SILENCE_DURATION,
    SAMPLE_RATE,
)

class SpeechToText:
    """Speech-to-text using faster-whisper, optimized for CPU."""

    def __init__(self):
        print(f"[STT] Loading faster-whisper model: {WHISPER_MODEL_SIZE}...")
        from faster_whisper import WhisperModel
        self.model = WhisperModel(
            WHISPER_MODEL_SIZE,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )
        self.sample_rate = SAMPLE_RATE
        self.audio_queue = queue.Queue()
        print("[STT] Model loaded successfully.")

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for sounddevice InputStream."""
        self.audio_queue.put(indata.copy())

    def record_until_silence(self) -> np.ndarray:
        """Record audio until silence is detected. Returns numpy array."""
        frames = []
        silent_chunks = 0
        chunk_duration = 0.1  # 100ms per chunk
        frames_per_chunk = int(self.sample_rate * chunk_duration)
        required_silence_chunks = int(SILENCE_DURATION / chunk_duration)
        has_speech = False

        # Clear queue
        while not self.audio_queue.empty():
            self.audio_queue.get()

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32',
            blocksize=frames_per_chunk,
            callback=self._audio_callback,
        ):
            print("[STT] 🎤 Listening... (speak now)")
            while True:
                try:
                    chunk = self.audio_queue.get(timeout=10)
                except queue.Empty:
                    print("[STT] Timeout — no audio detected.")
                    break

                frames.append(chunk)
                volume = np.abs(chunk).mean()

                if volume >= SILENCE_THRESHOLD:
                    has_speech = True
                    silent_chunks = 0
                else:
                    silent_chunks += 1

                # Stop after silence detected AND we have enough speech
                if has_speech and silent_chunks >= required_silence_chunks:
                    break

                # Safety: max 30 seconds recording
                if len(frames) > int(30 / chunk_duration):
                    print("[STT] Max recording duration reached.")
                    break

        if not frames:
            return np.array([], dtype='float32')

        audio = np.concatenate(frames, axis=0).flatten()
        return audio

    def transcribe(self, audio: np.ndarray) -> str:
        """Transcribe audio numpy array to text."""
        if len(audio) == 0:
            return ""

        print("[STT] Transcribing...")
        segments, info = self.model.transcribe(
            audio,
            language='en',
            beam_size=1,          # Faster on CPU
            best_of=1,            # Faster on CPU
            vad_filter=True,      # Filter out non-speech
        )
        text = ' '.join(segment.text for segment in segments).strip()
        if text:
            print(f"[STT] You said: \"{text}\"")
        else:
            print("[STT] No speech detected.")
        return text

    def listen(self) -> str:
        """Record and transcribe in one call."""
        audio = self.record_until_silence()
        return self.transcribe(audio)


class HotkeyListener:
    """Listens for a global hotkey to trigger voice input."""

    def __init__(self, callback):
        """
        callback: function to call when hotkey is pressed.
        """
        self.callback = callback
        self.running = False
        self._thread = None

    def start(self):
        """Start listening for the hotkey in a background thread."""
        import keyboard as kb
        self.running = True

        def _on_hotkey():
            if self.running:
                self.callback()

        kb.add_hotkey(HOTKEY, _on_hotkey, suppress=False)
        print(f"[HOTKEY] Listening for '{HOTKEY}' — press to activate JARVIS.")

    def stop(self):
        """Stop listening for hotkeys."""
        import keyboard as kb
        self.running = False
        try:
            kb.remove_hotkey(HOTKEY)
        except Exception:
            pass
        print("[HOTKEY] Stopped.")


class TextInput:
    """Fallback text input via terminal."""

    @staticmethod
    def get_input(prompt: str = "You: ") -> str:
        """Get text input from the user."""
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return ""