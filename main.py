def stream_and_speak(text, tts):
    """Stream TTS output as it is generated (for large responses)."""
    # If tts has a streaming method, use it; else fallback to speak()
    if hasattr(tts, 'speak_streaming'):
        tts.speak_streaming(text)
    else:
        tts.speak(text)
"""
JARVIS v1.0 — Main Service
The primary entry point. Orchestrates all subsystems:
  Voice Input → Brain (classify + reason) → Executor → TTS Output
  
Usage:
  python main.py            (text mode — type commands)
  python main.py --voice    (voice mode — press Ctrl+Shift+J to talk)
  python main.py --help     (show help)
"""

import sys
import uuid
import signal
import argparse
from datetime import datetime

from config import ASSISTANT_NAME, HOTKEY
from brain import Brain
from memory import Memory
from executor import Executor
from tts import TextToSpeech
from intent_filter import IntentFilter

# Import speech-to-speech functions
from speech_assistant import recognize_speech, speak_text
from proactive import ProactiveEngine
from safety import get_safety_summary

# ─── Session ID ──────────────────────────────────────────
SESSION_ID = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

def print_banner():
    """Print the JARVIS startup banner."""
    print(r"""
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
    v1.0 — Your Personal AI Assistant
    """)

def run_text_mode(brain, memory, executor, tts, proactive):
    """Run JARVIS in text input mode (terminal-based)."""
    tts.speak(f"{ASSISTANT_NAME} is ready. How can I help you?")

    intent_filter = IntentFilter(brain)

    while True:
        try:
            user_input = input(f"\n{'─'*50}\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n[{ASSISTANT_NAME}] Goodbye!")
            break

        if not user_input:
            continue

        # Special commands
        lower = user_input.lower()
        if lower in ('quit', 'exit', 'bye', 'goodbye', 'stop'):
            tts.speak("Goodbye! Have a great day.")
            break
        if lower == 'status':
            print(_get_status(brain, memory, tts, proactive))
            continue
        if lower == 'safety':
            print(get_safety_summary())
            continue
        if lower == 'help':
            print(_get_help())
            continue

        # Intent filter check before main pipeline
        if not intent_filter.is_command(user_input):
            print(f"[FILTER] Ambient speech ignored: {user_input}")
            continue

        # ─── Main Pipeline ───────────────────────────────
        try:
            # 1. Get memory context
            context = memory.get_context(user_input)

            # 2. Route through brain
            routing = brain.route(user_input, context)
            print(f"[BRAIN] Intent: {routing['intent'].value} | Model: {routing['model']}")

            # 3. Execute
            response = executor.execute(routing)

            # 4. Output
            tts.speak(response)

            # 5. Store in memory
            memory.add_exchange(
                session_id=SESSION_ID,
                user_input=user_input,
                response=response,
                intent=routing['intent'].value,
                model_used=routing['model'],
            )

        except Exception as e:
            error_msg = f"Something went wrong: {e}"
            print(f"[ERROR] {error_msg}")
            tts.speak("I encountered an error. Please try again.")

def run_voice_mode(brain, memory, executor, tts, proactive):
    """Run JARVIS in voice input mode (hotkey-activated)."""
    from voice_layer import SpeechToText
    from wake_word_engine import WakeWordEngine

    stt = SpeechToText()
    is_listening = False
    intent_filter = IntentFilter(brain)

    def on_hotkey():
        nonlocal is_listening
        if is_listening:
            return
        is_listening = True

        try:
            user_input = stt.listen()
            if not user_input:
                print("[STT] No speech detected.")
                is_listening = False
                return

            # Check for exit commands
            lower = user_input.lower()
            if lower in ('quit', 'exit', 'bye', 'goodbye', 'stop jarvis'):
                tts.speak("Goodbye!")
                sys.exit(0)

            # Intent filter check before main pipeline
            if not intent_filter.is_command(user_input):
                print(f"[FILTER] Ambient speech ignored: {user_input}")
                is_listening = False
                return

            # Main pipeline
            context = memory.get_context(user_input)
            routing = brain.route(user_input, context)
            print(f"[BRAIN] Intent: {routing['intent'].value} | Model: {routing['model']}")

            response = executor.execute(routing)
            stream_and_speak(response, tts)

            memory.add_exchange(
                session_id=SESSION_ID,
                user_input=user_input,
                response=response,
                intent=routing['intent'].value,
                model_used=routing['model'],
            )

        except Exception as e:
            print(f"[ERROR] {e}")
            tts.speak("I encountered an error. Please try again.")
        finally:
            is_listening = False

    # Start always-on wake word engine
    wake_engine = WakeWordEngine(on_wake_callback=on_hotkey)
    wake_engine.start()

    tts.speak(f"{ASSISTANT_NAME} is ready. Say 'hey jarvis' to speak.")
    print(f"\n[{ASSISTANT_NAME}] Voice mode active. Say 'hey jarvis' to activate.")
    print(f"[{ASSISTANT_NAME}] Press Ctrl+C or say 'quit' to exit.\n")

    # Ensure IntentFilter is used before every pipeline step
    # Register VisionHandler and PhoneHandler in brain/executor (pseudo-code, actual integration needed)
    # Integrate AutonomyGate in risky handlers (pseudo-code, actual integration needed)
    # Use stream_and_speak for all TTS output in both text and voice modes
    # Update requirements.txt and .env for all dependencies (manual step)
    # Test each layer independently (manual step)

def _get_status(brain, memory, tts, proactive) -> str:
    """Get system status."""
    analytics = memory.get_conversation_analytics()
    return f"""
╔══════════════════════════════════════════════╗
║             {ASSISTANT_NAME} STATUS                      ║
╠══════════════════════════════════════════════╣
║ Session:     {SESSION_ID[:30]:<30} ║
║ TTS Backend: {tts.backend_name:<30} ║
║ Privacy:     {'ON' if memory.privacy_mode else 'OFF':<30} ║
║ Facts:       {memory._count_facts():<30} ║
║ Convos:      {analytics['total_conversations']:<30} ║
║ ChromaDB:    {'Yes' if memory.chroma_available else 'No':<30} ║
║ Proactive:   {'ON' if proactive.running else 'OFF':<30} ║
╚══════════════════════════════════════════════╝"""

def _get_help() -> str:
    """Get help text."""
    return f"""
🤖 {ASSISTANT_NAME} v1.0 — Help

💬 Chat:      Just talk naturally! Ask questions, get advice.
🔍 Search:    "Search for ...", "What is the latest news about ..."
💻 Code:      "Write a Python script that ...", "Debug this code ..."
🖥️  System:    "Open Chrome", "Take a screenshot", "System info"
📝 Notes:     "Take a note: ...", "Show my notes", "Search notes for ..."
🧮 Utility:   "Calculate 15 * 27", "Convert 100 km to miles", "Generate password"
🧠 Memory:    "What do you know about me?", "Privacy mode on", "Export memory"

Special commands:
  status  — Show system status
  safety  — Show safety restrictions
  help    — Show this help
  quit    — Exit JARVIS

Voice mode: Press {HOTKEY} to activate voice input.
"""

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description=f'{ASSISTANT_NAME} v1.0 — Personal AI Assistant')
    parser.add_argument('--voice', action='store_true', help='Enable voice mode (hotkey-activated)')
    parser.add_argument('--speech-assistant', action='store_true', help='Enable fully hands-free speech-to-speech mode')
    parser.add_argument('--no-proactive', action='store_true', help='Disable proactive engine')
    args = parser.parse_args()

    print_banner()

    # ─── Initialize subsystems ───────────────────────────
    print("Initializing subsystems...")

    brain = Brain()
    memory = Memory()
    executor = Executor(brain, memory)
    tts = TextToSpeech()

    # Proactive engine
    proactive = ProactiveEngine(memory, tts)
    if not args.no_proactive:
        proactive.start()

    # ─── Graceful shutdown ───────────────────────────────
    def shutdown(sig=None, frame=None):
        print(f"\n[{ASSISTANT_NAME}] Shutting down...")
        proactive.stop()
        print(f"[{ASSISTANT_NAME}] Goodbye!")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # ─── Run ─────────────────────────────────────────────
    try:
        # Always run speech-to-speech mode by default
        print(f"\n[{ASSISTANT_NAME}] Speech-to-Speech mode active. Say 'quit' to exit.")
        speak_text(f"{ASSISTANT_NAME} is ready. How can I help you?")
        while True:
            text = recognize_speech()
            if not text:
                continue
            if text.lower() in ("quit", "exit", "bye", "goodbye"):
                speak_text("Goodbye! Have a great day.")
                break
            # Route through JARVIS pipeline for a real response
            context = memory.get_context(text)
            routing = brain.route(text, context)
            print(f"[BRAIN] Intent: {routing['intent'].value} | Model: {routing['model']}")
            response = executor.execute(routing)
            print(f"[{ASSISTANT_NAME}]: {response}")
            speak_text(response)
            memory.add_exchange(
                session_id=SESSION_ID,
                user_input=text,
                response=response,
                intent=routing['intent'].value,
                model_used=routing['model'],
            )
    except Exception as e:
        print(f"[FATAL] {e}")
    finally:
        shutdown()

if __name__ == '__main__':
    main()