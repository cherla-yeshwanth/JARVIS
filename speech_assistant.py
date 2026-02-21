"""
JARVIS v1.0 — Speech-to-Speech Assistant
Simple speech-to-speech loop using SpeechRecognition and gTTS.
"""

import speech_recognition as sr
from gtts import gTTS
import pygame
import tempfile
import os

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("[🎤] Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"[You]: {text}")
        return text
    except sr.UnknownValueError:
        print("[!] Could not understand audio.")
        return ""
    except sr.RequestError as e:
        print(f"[!] Could not request results; {e}")
        return ""

def speak_text(text):
    import uuid
    tts = gTTS(text=text, lang='en')
    temp_dir = tempfile.gettempdir()
    unique_name = f'jarvis_tts_{uuid.uuid4().hex}.mp3'
    temp_path = os.path.join(temp_dir, unique_name)
    tts.save(temp_path)
    pygame.mixer.init()
    pygame.mixer.music.load(temp_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    try:
        os.remove(temp_path)
    except Exception:
        pass

def main():
    print("JARVIS Speech-to-Speech Assistant. Say 'quit' to exit.")
    while True:
        text = recognize_speech()
        if not text:
            continue
        if text.lower() in ("quit", "exit", "bye", "goodbye"):
            speak_text("Goodbye! Have a great day.")
            break
        # Here you can add logic to process the text and generate a response
        response = f"You said: {text}"
        print(f"[JARVIS]: {response}")
        speak_text(response)

if __name__ == "__main__":
    main()
