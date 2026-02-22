class KokoroTTS:
    """Best free neural TTS — sounds genuinely natural"""
    def __init__(self):
        self.available = False
        try:
            from kokoro import KPipeline
            self.pipeline = KPipeline(lang_code='a')  # 'a' = American English
            self.available = True
            print('[TTS] Kokoro TTS loaded. Natural voice ready.')
        except Exception as e:
            print(f'[TTS] Kokoro not available: {e}')

    def speak(self, text: str):
        if not self.available or not text.strip():
            return
        import sounddevice as sd
        print(f'[JARVIS]: {text}')
        try:
            # Voice options: 'am_adam', 'am_echo', 'bf_emma'
            # 'am_adam' sounds closest to JARVIS — calm, confident, male
            generator = self.pipeline(text, voice='am_adam', speed=1.05)
            for _, _, audio in generator:
                sd.play(audio, samplerate=24000)
                sd.wait()
        except Exception as e:
            print(f'[TTS] Kokoro error: {e}')
"""
JARVIS v1.0 — Text-to-Speech Module
Supports two backends:
  1. Piper TTS (offline, natural voice, requires model download)
  2. pyttsx3 (offline, Windows SAPI voices, zero setup fallback)
"""

import subprocess
import tempfile
import os
import re
from config import PIPER_EXE, PIPER_MODEL, TTS_BACKEND

class PiperTTS:
    """Piper TTS — high quality offline voice synthesis."""

    def __init__(self):
        self.exe = PIPER_EXE
        self.model = PIPER_MODEL
        self.available = os.path.isfile(self.exe) and os.path.isfile(self.model)
        if self.available:
            print("[TTS] Piper TTS loaded successfully.")
        else:
            print("[TTS] Piper TTS not available (model files not found).")

    def speak(self, text: str):
        """Convert text to speech and play."""
        if not self.available:
            print("[TTS] Piper not available.")
            return
        if not text.strip():
            return

        print(f"[JARVIS]: {text}")
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                tmp_path = f.name

            subprocess.run(
                [self.exe, '--model', self.model, '--output_file', tmp_path],
                input=text.encode('utf-8'),
                capture_output=True,
                timeout=30,
            )

            # Play using PowerShell (Windows)
            subprocess.run(
                ['powershell', '-c',
                 f'(New-Object Media.SoundPlayer "{tmp_path}").PlaySync()'],
                capture_output=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            print("[TTS] Piper timed out.")
        except Exception as e:
            print(f"[TTS] Piper error: {e}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

class Pyttsx3TTS:
    """pyttsx3 TTS — uses Windows SAPI voices. Zero setup required."""

    def __init__(self):
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            # Configure voice
            self.engine.setProperty('rate', 175)    # Words per minute
            self.engine.setProperty('volume', 0.9)  # Volume 0-1
            # Try to use a female voice if available (usually sounds better)
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'zira' in voice.name.lower() or 'female' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
            self.available = True
            print("[TTS] pyttsx3 loaded successfully.")
        except Exception as e:
            self.available = False
            print(f"[TTS] pyttsx3 not available: {e}")

    def speak(self, text: str):
        """Speak text using Windows SAPI."""
        if not self.available:
            print(f"[JARVIS]: {text}")
            return
        if not text.strip():
            return

        print(f"[JARVIS]: {text}")
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"[TTS] pyttsx3 error: {e}")

class TextToSpeech:
    """
    Unified TTS interface. Tries Piper first, falls back to pyttsx3,
    falls back to print-only if both fail.
    """

    def __init__(self):
        self.backend = None
        self.backend_name = "none"

        # Try Kokoro first (best free option)
        kokoro = KokoroTTS()
        if kokoro.available:
            self.backend = kokoro
            self.backend_name = "kokoro"
            return

        # Piper next
        piper = PiperTTS()
        if piper.available:
            self.backend = piper
            self.backend_name = "piper"
            return

        # pyttsx3 as last resort
        py3 = Pyttsx3TTS()
        if py3.available:
            self.backend = py3
            self.backend_name = "pyttsx3"
            return

        self.backend_name = "print-only"
        print("[TTS] No TTS backend available. Will print responses only.")

    def speak(self, text: str):
        """Speak text using the active backend."""
        if not text.strip():
            return
        if self.backend:
            self.backend.speak(text)
        else:
            print(f"[JARVIS]: {text}")

    def speak_streaming(self, text: str):
        """
        Speak text sentence by sentence for lower perceived latency.
        First sentence starts playing while the rest are queued.
        """
        if not text.strip():
            return
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                self.speak(sentence)