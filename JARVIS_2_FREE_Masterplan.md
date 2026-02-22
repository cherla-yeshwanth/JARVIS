# 🤖 JARVIS 2.0 — 100% FREE EDITION
## The Iron Man Upgrade Masterplan — Zero Cost, Fully Offline

> **No API keys. No subscriptions. No internet required. Everything runs on your PC.**
> 
> ₹0 • $0 • £0 • €0 • FOREVER FREE

---

## 🧭 SECTION 1: The Zero-Cost Philosophy

The previous plan included paid services (GPT-4o, ElevenLabs, Picovoice). This plan achieves the **exact same capabilities** using only free, open-source tools:

- **Ollama** — free local LLM runtime (already in your project)
- **OpenWakeWord** — 100% free, open-source wake word detection
- **LLaVA** — free vision model running locally via Ollama
- **Kokoro TTS** — free offline neural voice synthesis (beats ElevenLabs in benchmarks)
- **PyAutoGUI + mss** — free Python libraries for UI control
- **Standard Python libraries** — all pip installable, zero cost

> ⚠️ **The Only Real Trade-off:** Free local models need more RAM/CPU than cloud APIs.
> - Vision: LLaVA:13b needs ~8GB RAM. Use LLaVA:7b if you have less.
> - Speed: 3–8 seconds per response on CPU-only. Acceptable for a voice assistant.
> - Quality: 85–90% as good as GPT-4o for most tasks. Enough for JARVIS.
> - **Recommended:** 16GB RAM PC = perfect. 8GB RAM PC = use smaller variants.

---

## 🆓 Complete Free Stack Overview

| Component | Free Solution |
|---|---|
| Wake Word "hi buddy" | OpenWakeWord (open-source, MIT license, offline) |
| Intent Filter (ambient vs command) | Regex + local LLM — already have it, free |
| Speech-to-Text | faster-whisper — already installed, completely free |
| Brain / Reasoning LLM | mistral-nemo:12b via Ollama — free, surprisingly smart |
| Code Generation LLM | deepseek-coder-v2:16b via Ollama — free, best free coder |
| Screen Vision | LLaVA:13b via Ollama — free, runs locally |
| UI Automation (click/scroll) | PyAutoGUI + mss — free Python libraries |
| Text-to-Speech (natural voice) | Kokoro TTS — free offline neural voice |
| WhatsApp Call Control | PyAutoGUI + LLaVA vision — free automation |
| Memory / Database | SQLite + ChromaDB — already installed, free |
| Web Search | DuckDuckGo — already installed, free |
| Embeddings | nomic-embed-text via Ollama — already installed, free |

---

## 🔧 SECTION 2: The 8 Upgrade Layers

---

## 🎙️ LAYER 1: Always-On Wake Word — "Hi Buddy"
**COST: $0 — OpenWakeWord (Apache 2.0)**

### Why OpenWakeWord Instead of Porcupine

Porcupine's free tier is limited. OpenWakeWord is 100% open-source (Apache 2.0), runs completely offline, and is used in production by Home Assistant. No account, no API key, no internet — ever.

- **GitHub:** github.com/dscripka/openWakeWord — 8,000+ stars
- **Used by:** Home Assistant (world's most popular home automation platform)
- **CPU Usage:** ~2–3% continuously — negligible
- **Custom wake words:** Train your own "hi buddy" using their free training script
- **Pre-built models:** `hey_jarvis`, `hey_mycroft` available out of the box

### Installation

```bash
pip install openwakeword pyaudio
```

### New File: `wake_word_engine.py`

```python
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
```

### Training Your Own "Hi Buddy" Wake Word (Free)

1. Record 50–100 short clips of yourself saying "hi buddy" (use Audacity — free)
2. Record 50–100 clips of background noise / NOT saying "hi buddy"
3. Run the training script from OpenWakeWord GitHub (~30 mins on CPU)
4. Save the `.tflite` model file to your JARVIS folder
5. Update: `self.model = Model(wakeword_models=['models/hi_buddy.tflite'])`

### Update `main.py`

```python
# REMOVE this:
hotkey = HotkeyListener(on_hotkey)
hotkey.start()

# ADD this (on_hotkey function stays EXACTLY the same):
from wake_word_engine import WakeWordEngine
wake_engine = WakeWordEngine(on_wake_callback=on_hotkey)
wake_engine.start()
```

---

## 🧠 LAYER 2: Intent Filter — Command vs Ambient Speech
**COST: $0 — Pure Python + Local LLM**

After wake word triggers, JARVIS must know: "are you talking TO me, or just thinking aloud?"

### New File: `intent_filter.py`

```python
import re

# Speech that directly addresses JARVIS → always a command
DIRECT_PATTERNS = [
    r'^(hey|hi|ok|okay|yo)?\s*(jarvis|buddy)[,!]?\s+\w+',
    r'.+\s+(jarvis|buddy)[.!?]?$',
    r'^(jarvis|buddy),?\s+',
]

# Obvious non-commands → ignore immediately
AMBIENT_PATTERNS = [
    r'^(haha|lol|wow|omg|oh|ah|hmm|ugh)+$',
    r'^(yes|no|yeah|nah|ok|okay|sure|fine|yep|nope)$',
    r'^\d{1,3}$',
]

class IntentFilter:
    def __init__(self, brain):
        self.brain = brain

    def is_command(self, text: str) -> bool:
        lower = text.lower().strip()
        if len(lower) < 3:
            return False

        # Tier 1: Explicit address → definitely a command
        for pat in DIRECT_PATTERNS:
            if re.search(pat, lower):
                return True

        # Tier 2: Obvious ambient → skip without LLM call
        for pat in AMBIENT_PATTERNS:
            if re.search(pat, lower):
                return False

        # Tier 3: Ask local LLM (qwen2.5:3b — fast, free)
        prompt = (
            'Is the following text a command to an AI assistant, '
            'or just someone speaking/thinking aloud?\n'
            f'Text: "{text}"\n'
            'Reply ONLY with: COMMAND or AMBIENT'
        )
        result = self.brain._call_ollama(self.brain.fast_model, prompt)
        return 'COMMAND' in result.upper()
```

### Wire into `main.py`

```python
intent_filter = IntentFilter(brain)

def on_wake_callback():
    user_input = stt.listen()
    if not user_input:
        return

    # NEW: filter check before any heavy processing
    if not intent_filter.is_command(user_input):
        print(f'[FILTER] Ambient speech ignored: {user_input}')
        return

    # Continue with existing pipeline...
    context = memory.get_context(user_input)
    routing = brain.route(user_input, context)
    response = executor.execute(routing)
```

---

## 👁️ LAYER 3: Screen Vision + UI Automation
**COST: $0 — LLaVA via Ollama + PyAutoGUI**

### The Free Vision Stack

- **LLaVA** (Large Language and Vision Assistant) runs via Ollama — completely free
- Analyzes screenshots, describes screen content, finds UI elements, reads text
- **LLaVA:7b** = ~5GB RAM. **LLaVA:13b** = ~8GB RAM, much better accuracy
- **PyAutoGUI** handles all mouse clicks, keyboard input, scrolling — free Python library

### Install

```bash
pip install mss pyautogui pillow

# Pull vision model (one-time download, then offline forever):
ollama pull llava:13b      # Best quality (8GB RAM needed)
# OR for less RAM:
ollama pull llava:7b       # Decent quality (5GB RAM needed)
```

### New File: `handlers/vision_handler.py`

```python
import mss
import pyautogui
import base64, json, io, requests
from PIL import Image
from config import OLLAMA_HOST

VISION_MODEL = 'llava:13b'  # Change to 'llava:7b' if low RAM

class VisionHandler:
    def __init__(self, brain):
        self.brain = brain
        pyautogui.FAILSAFE = True   # Move mouse to corner = emergency stop!
        pyautogui.PAUSE = 0.4       # Safety pause between actions

    def _screenshot_b64(self) -> str:
        with mss.mss() as sct:
            shot = sct.grab(sct.monitors[0])
            img = Image.frombytes('RGB', shot.size, shot.bgra, 'raw', 'BGRX')
            img.thumbnail((1280, 720))  # Resize for faster processing
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            return base64.b64encode(buf.getvalue()).decode()

    def _ask_vision(self, b64img: str, question: str) -> dict:
        """Send screenshot to local LLaVA model via Ollama API"""
        prompt = (
            f'You are a UI automation assistant.\n'
            f'Task: {question}\n'
            f'Look at the screenshot carefully.\n'
            f'Reply ONLY as JSON (no other text):\n'
            f'{{"found": true/false, "description": "what you see", '
            f'"action": "click/scroll/type/read/none", '
            f'"x": pixel_x_or_null, "y": pixel_y_or_null, '
            f'"text_to_type": "string or null", '
            f'"scroll_amount": integer_or_null}}'
        )
        try:
            resp = requests.post(
                f'{OLLAMA_HOST}/api/generate',
                json={
                    'model': VISION_MODEL,
                    'prompt': prompt,
                    'images': [b64img],
                    'stream': False,
                },
                timeout=60
            )
            raw = resp.json().get('response', '{}').strip().strip('`').replace('json', '').strip()
            return json.loads(raw)
        except Exception as e:
            return {'found': False, 'description': f'Vision error: {e}', 'action': 'none'}

    def _act(self, plan: dict) -> str:
        if not plan.get('found', False):
            return f"Couldn't find it: {plan.get('description', 'unknown')}"
        action = plan.get('action', 'none')
        x, y = plan.get('x'), plan.get('y')
        if action == 'click' and x and y:
            pyautogui.moveTo(x, y, duration=0.4)
            pyautogui.click()
            return f'Clicked at ({x}, {y})'
        elif action == 'scroll':
            amt = plan.get('scroll_amount', -3)
            pyautogui.scroll(amt)
            return f'Scrolled {"down" if amt < 0 else "up"}'
        elif action == 'type':
            pyautogui.typewrite(plan.get('text_to_type', ''), interval=0.05)
            return 'Typed text'
        elif action == 'read':
            return f"I can see: {plan.get('description', 'nothing')}"
        return plan.get('description', 'Done')

    def handle(self, user_input: str, context: str = '') -> str:
        lower = user_input.lower()
        b64 = self._screenshot_b64()
        plan = self._ask_vision(b64, user_input)
        if any(w in lower for w in ['read', 'see', 'what', 'show', 'describe']):
            return plan.get('description', 'I cannot determine what is on screen.')
        return self._act(plan)
```

### Register in `brain.py` and `executor.py`

```python
# brain.py — add to Intent enum:
VISION = 'vision'

# brain.py — add to INTENT_PATTERNS:
Intent.VISION: [
    'click ', 'press ', 'tap ', 'scroll ', 'select ',
    'what is on my screen', 'what do you see', 'read the screen',
    'like this', 'like the', 'share this', 'save this',
    'find the button', 'click the', 'open the',
],

# executor.py — add:
from handlers.vision_handler import VisionHandler
self.handlers[Intent.VISION] = VisionHandler(brain)
```

### The Instagram Like Example

When you say "click like on this reel":

1. Wake word "hey jarvis" detected → JARVIS activates
2. STT captures: "click like on this reel"
3. Intent filter: COMMAND (contains "click")
4. Brain classifies: VISION intent
5. VisionHandler takes screenshot of your screen
6. Sends to local LLaVA: "Find the like button on this Instagram reel"
7. LLaVA returns: `{"found": true, "action": "click", "x": 947, "y": 823}`
8. PyAutoGUI moves mouse to (947, 823) and clicks
9. JARVIS says: "Done, liked the reel!"

---

## 📞 LAYER 4: Phone & WhatsApp Call Control
**COST: $0 — Vision + PyAutoGUI**

LLaVA sees the WhatsApp Desktop window, finds the correct buttons, PyAutoGUI clicks them. No API. No subscription.

### New File: `handlers/phone_handler.py`

```python
import subprocess, pyautogui, time, os
from handlers.vision_handler import VisionHandler

class PhoneHandler:
    def __init__(self, brain):
        self.vision = VisionHandler(brain)

    def _open_whatsapp(self):
        try:
            os.startfile('whatsapp:')
        except Exception:
            subprocess.Popen(['explorer', 'whatsapp:'])
        time.sleep(2.5)

    def make_call(self, contact: str) -> str:
        self._open_whatsapp()
        # Find search bar
        b64 = self.vision._screenshot_b64()
        plan = self.vision._ask_vision(b64, 'Find the search contacts text box')
        self.vision._act(plan)
        time.sleep(0.5)
        pyautogui.typewrite(contact, interval=0.07)
        time.sleep(1)
        # Click the contact
        b64 = self.vision._screenshot_b64()
        plan = self.vision._ask_vision(b64, f'Find and click the contact named {contact}')
        self.vision._act(plan)
        time.sleep(1)
        # Click voice call button
        b64 = self.vision._screenshot_b64()
        plan = self.vision._ask_vision(b64, 'Find and click the voice call button (phone icon)')
        self.vision._act(plan)
        return f'Calling {contact} on WhatsApp...'

    def answer_call(self) -> str:
        b64 = self.vision._screenshot_b64()
        plan = self.vision._ask_vision(b64, 'Find and click the green accept/answer call button')
        return self.vision._act(plan)

    def end_call(self) -> str:
        b64 = self.vision._screenshot_b64()
        plan = self.vision._ask_vision(b64, 'Find and click the red end/hang up call button')
        return self.vision._act(plan)

    def handle(self, user_input: str, context: str = '') -> str:
        lower = user_input.lower()
        if any(w in lower for w in ['answer', 'attend', 'pick up', 'receive']):
            return self.answer_call()
        if any(w in lower for w in ['end call', 'hang up', 'disconnect', 'cut call']):
            return self.end_call()
        if 'call' in lower:
            name = lower
            for w in ['call', 'whatsapp', 'phone', 'dial', 'ring', 'make a', 'please']:
                name = name.replace(w, '').strip()
            return self.make_call(name.strip())
        return 'Could not understand phone command.'
```

```python
# brain.py — add to Intent enum:
PHONE = 'phone'

# brain.py — add to INTENT_PATTERNS:
Intent.PHONE: [
    'call ', 'phone ', 'dial ', 'answer the call', 'attend the call',
    'pick up', 'hang up', 'end call', 'reject call', 'decline call',
],

# executor.py — add:
from handlers.phone_handler import PhoneHandler
self.handlers[Intent.PHONE] = PhoneHandler(brain)
```

---

## 🧬 LAYER 5: LLM Brain Upgrade — Better Reasoning
**COST: $0 — Ollama Models (All Free)**

All pulled via `ollama pull` — completely free, run locally, no internet after download:

| Role | Free Model (via Ollama) |
|---|---|
| Intent Classification (fast) | `qwen2.5:3b` — keep as-is, already perfect |
| General Reasoning + Chat | `mistral-nemo:12b` — best free 12B model |
| Code Generation | `deepseek-coder-v2:16b` — best free code model |
| Vision (screen understanding) | `llava:13b` — best free vision model |
| Memory Embeddings | `nomic-embed-text` — keep as-is |
| If only 8GB RAM | `qwen2.5:7b` for all tasks |

### Pull Commands (Once, Then Offline Forever)

```bash
ollama pull mistral-nemo:12b        # 7.1GB — best free reasoning
ollama pull deepseek-coder-v2:16b  # 9.1GB — best free code model
ollama pull llava:13b              # 8.0GB — free vision model

# Low RAM alternatives:
ollama pull mistral:7b             # 4.1GB
ollama pull deepseek-coder:6.7b   # 3.8GB
ollama pull llava:7b              # 4.5GB
```

### Update `config.py`

```python
FAST_MODEL  = os.getenv('FAST_MODEL',  'qwen2.5:3b')           # Keep
SMART_MODEL = os.getenv('SMART_MODEL', 'mistral-nemo:12b')      # Upgrade
CODE_MODEL  = os.getenv('CODE_MODEL',  'deepseek-coder-v2:16b') # New
VISION_MODEL = os.getenv('VISION_MODEL', 'llava:13b')           # New
```

### Update `handlers/code_handler.py`

```python
from config import CODE_MODEL   # Add this import

# Change one line:
'model': CODE_MODEL,   # Was SMART_MODEL
```

---

## 🔊 LAYER 6: Natural JARVIS Voice — Kokoro TTS
**COST: $0 — Kokoro TTS (Apache 2.0)**

> **Kokoro TTS facts:**
> - Ranked #1 on TTS benchmarks — above ElevenLabs in some tests
> - Apache 2.0 license — free forever, commercial use allowed
> - ~82MB model, runs on CPU comfortably
> - 20+ voices including American and British accents
> - GitHub: github.com/hexgrad/kokoro — 16,000+ stars

### Installation

```bash
pip install kokoro>=0.9.2 misaki[en] soundfile sounddevice
```

### Add `KokoroTTS` class to `tts.py`

```python
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
```

### Update `TextToSpeech` class priority in `tts.py`

```python
def __init__(self):
    self.backend = None
    self.backend_name = 'none'

    # Try Kokoro first (best free option)
    kokoro = KokoroTTS()
    if kokoro.available:
        self.backend = kokoro
        self.backend_name = 'kokoro'
        return

    # Piper next (already in your project)
    piper = PiperTTS()
    if piper.available:
        self.backend = piper
        self.backend_name = 'piper'
        return

    # pyttsx3 as last resort
    py3 = Pyttsx3TTS()
    if py3.available:
        self.backend = py3
        self.backend_name = 'pyttsx3'
```

---

## ⚡ LAYER 7: Autonomy with Safety Gate
**COST: $0 — Pure Python**

JARVIS makes smart decisions but always asks before doing risky things. 3-level permission system:

- **Level AUTO:** Safe actions — just do it (open app, screenshot, search, volume)
- **Level CONFIRM:** Risky actions — ask user first (send message, make call, write file)
- **Level BLOCKED:** Destructive actions — refuse always (delete files, format, uninstall)

### New File: `autonomy.py`

```python
from enum import Enum

class Level(Enum):
    AUTO    = 'auto'      # Do immediately, tell user after
    CONFIRM = 'confirm'   # Ask user first, wait for yes/no
    BLOCKED = 'blocked'   # Refuse always, explain why

RULES = {
    Level.AUTO: [
        'open', 'close app', 'screenshot', 'volume', 'search',
        'system info', 'note', 'read', 'calculate', 'convert',
        'play', 'pause', 'resume',
    ],
    Level.CONFIRM: [
        'send', 'call', 'email', 'post', 'submit', 'create file',
        'write file', 'modify', 'edit file', 'order', 'book',
        'message', 'share', 'upload',
    ],
    Level.BLOCKED: [
        'delete file', 'format', 'uninstall', 'wipe memory',
        'remove os', 'delete system', 'rm -rf', 'factory reset',
        'delete all',
    ],
}

class AutonomyGate:
    def __init__(self, tts, stt):
        self.tts = tts
        self.stt = stt

    def classify(self, action: str) -> Level:
        lower = action.lower()
        for kw in RULES[Level.BLOCKED]:
            if kw in lower: return Level.BLOCKED
        for kw in RULES[Level.CONFIRM]:
            if kw in lower: return Level.CONFIRM
        return Level.AUTO

    def request_confirm(self, what: str) -> bool:
        self.tts.speak(f'Should I {what}? Say yes or no.')
        reply = self.stt.listen().lower()
        return any(w in reply for w in ['yes', 'yeah', 'do it', 'go', 'proceed', 'sure'])

    def gate(self, action_description: str, execute_fn) -> str:
        level = self.classify(action_description)
        if level == Level.BLOCKED:
            return f'I cannot {action_description} — this action is restricted for safety.'
        if level == Level.CONFIRM:
            if not self.request_confirm(action_description):
                return 'Understood, cancelled.'
        return execute_fn()
```

---

## ⚡ LAYER 8: Streaming Pipeline — Gemini Live Feel
**COST: $0 — Python Threading**

Start speaking sentence 1 while generating sentence 2. Eliminates the "wait for full response" delay.

### Add to `main.py`

```python
import threading, queue, re

def stream_and_speak(user_input, brain, tts):
    """Generate response sentence by sentence, speak as it generates"""
    sentence_q = queue.Queue()
    result = []

    def generate():
        full = brain.think_step_by_step(user_input)
        sentences = re.split(r'(?<=[.!?])\s+', full)
        for s in sentences:
            s = s.strip()
            if s:
                sentence_q.put(s)
                result.append(s)
        sentence_q.put(None)  # Signal done

    def speak():
        while True:
            s = sentence_q.get()
            if s is None: break
            tts.speak(s)

    t1 = threading.Thread(target=generate, daemon=True)
    t2 = threading.Thread(target=speak, daemon=True)
    t1.start(); t2.start()
    t1.join(); t2.join()
    return ' '.join(result)

# In your main pipeline, replace:
#   tts.speak(response)
# With:
#   response = stream_and_speak(user_input, brain, tts)
```

---

## 📦 SECTION 3: Complete Free `requirements.txt`

```text
# ─── EXISTING (keep all) ─────────────────────────────────────────
faster-whisper>=0.10.0
sounddevice>=0.4.6
numpy>=1.24.0
keyboard>=0.13.5
chromadb>=0.4.0
duckduckgo-search>=6.0.0
requests>=2.31.0
python-dotenv>=1.0.0
psutil>=5.9.0
pyttsx3>=2.90

# ─── LAYER 1: Wake Word ──────────────────────────────────────────
openwakeword>=0.6.0
pyaudio>=0.2.13

# ─── LAYER 3: Screen Vision + UI Automation ──────────────────────
mss>=9.0.1
pyautogui>=0.9.54
pillow>=10.0.0

# ─── LAYER 6: Natural Voice TTS ──────────────────────────────────
kokoro>=0.9.2
misaki[en]>=0.9.2
soundfile>=0.12.1

# ─── OPTIONAL: Training custom wake word ─────────────────────────
# torch>=2.0.0
# torchaudio>=2.0.0
# speechbrain>=0.5.16
```

---

## 🤖 SECTION 4: Free Ollama Models to Pull

```bash
# REQUIRED — Pull these once, then offline forever:
ollama pull llava:13b               # Vision (8GB download, 8GB RAM needed)
ollama pull mistral-nemo:12b        # Reasoning (7GB download, 12GB RAM)
ollama pull deepseek-coder-v2:16b   # Code (9GB download)

# Already have these from v1.0 — keep:
# qwen2.5:3b
# nomic-embed-text

# LOW RAM ALTERNATIVES (8GB total RAM):
ollama pull llava:7b                # 5GB download, 5GB RAM
ollama pull mistral:7b              # 4GB download, 6GB RAM
ollama pull deepseek-coder:6.7b    # 4GB download
```

> **RAM Guide:**
> - **32GB RAM** → Pull all recommended models, everything runs smoothly
> - **16GB RAM** → Pull llava:13b + mistral-nemo:12b, run one at a time
> - **8GB RAM** → Use llava:7b + mistral:7b + deepseek-coder:6.7b only

---

## ⚙️ SECTION 5: Zero-Cost `.env` Configuration

No API keys needed. This is your complete `.env`:

```env
# ─── Core LLM Models (all free via Ollama) ────────────────────────
FAST_MODEL=qwen2.5:3b
SMART_MODEL=mistral-nemo:12b
CODE_MODEL=deepseek-coder-v2:16b
VISION_MODEL=llava:13b
EMBED_MODEL=nomic-embed-text

# ─── Voice (all free) ─────────────────────────────────────────────
TTS_BACKEND=kokoro
WHISPER_MODEL_SIZE=base
WHISPER_DEVICE=cpu

# ─── Wake Word (free, no API key) ─────────────────────────────────
WAKE_WORD_MODEL=hey_jarvis
# WAKE_WORD_MODEL=models/hi_buddy.tflite  # After training custom
WAKE_WORD_THRESHOLD=0.5

# ─── UI Automation Safety ─────────────────────────────────────────
PYAUTOGUI_PAUSE=0.4
PYAUTOGUI_FAILSAFE=true

# ─── Autonomy Gate ────────────────────────────────────────────────
CONFIRM_CALLS=true
CONFIRM_MESSAGES=true
CONFIRM_FILE_WRITE=true
```

---

## 📋 SECTION 6: Build Order

Build in this exact sequence — each is independently testable:

1. **Install everything first:**
   ```bash
   pip install openwakeword mss pyautogui pillow kokoro "misaki[en]" soundfile pyaudio
   ```

2. **Pull models** (do overnight — large downloads):
   ```bash
   ollama pull llava:13b && ollama pull mistral-nemo:12b && ollama pull deepseek-coder-v2:16b
   ```

3. **Layer 2 — Intent Filter** → Create `intent_filter.py`, wire into `main.py` (20 mins, zero downloads)

4. **Layer 6 — Kokoro TTS** → Add class to `tts.py`, update priority (30 mins, massive voice improvement)

5. **Layer 1 — Wake Word** → Create `wake_word_engine.py`, replace HotkeyListener (1 hour)

6. **Layer 3 — Screen Vision** → Create `handlers/vision_handler.py`, test with "what's on my screen" first

7. **Layer 5 — LLM Upgrade** → Just update `config.py` with new model names (5 minutes)

8. **Layer 7 — Autonomy Gate** → Create `autonomy.py`, add gate to phone/message handlers

9. **Layer 4 — Phone Handler** → Create `handlers/phone_handler.py` (WhatsApp Desktop must be installed)

10. **Layer 8 — Streaming** → Add `stream_and_speak()` to `main.py` (performance polish, do last)

---

## 💰 SECTION 7: Final Cost Breakdown

| Component | Cost & License |
|---|---|
| OpenWakeWord | FREE — Apache 2.0 |
| Ollama Runtime | FREE — MIT license |
| mistral-nemo:12b | FREE — Apache 2.0 |
| deepseek-coder-v2:16b | FREE — DeepSeek (free personal use) |
| LLaVA:13b vision model | FREE — LLaVA license (free personal use) |
| qwen2.5:3b | FREE — Apache 2.0 |
| nomic-embed-text | FREE — Apache 2.0 |
| Kokoro TTS | FREE — Apache 2.0 |
| faster-whisper STT | FREE — MIT license |
| PyAutoGUI | FREE — MIT license |
| mss (screen capture) | FREE — MIT license |
| ChromaDB | FREE — Apache 2.0 |
| DuckDuckGo search | FREE — no API key needed |
| **TOTAL** | **₹0 / $0 / £0 — Forever. No subscriptions. Ever.** |

---

> ## 🚀 Start Right Now
>
> ```bash
> pip install openwakeword mss pyautogui pillow kokoro "misaki[en]" soundfile pyaudio
> ```
>
> Then start with **Layer 2 (intent_filter.py)** — pure Python, zero downloads, takes 20 minutes, and immediately transforms how intelligently JARVIS listens.
>
> The only investment: time to implement, and disk space for model files (~35GB total).
>
> **Zero rupees. Zero dollars. Zero subscriptions. Build the real Iron Man. 🔥**

---

*JARVIS 2.0 — 100% Free Edition • Generated by Claude — Anthropic • 2026*
