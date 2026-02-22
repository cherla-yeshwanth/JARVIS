"""
JARVIS v1.0 — Centralized Configuration
All settings in one place. Modify this file to customize JARVIS.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ─── Paths ───────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
NOTES_DIR = DATA_DIR / "notes"
MODELS_DIR = BASE_DIR / "models"
DB_PATH = DATA_DIR / "jarvis.db"
CHROMA_DIR = str(DATA_DIR / "chroma_store")

DATA_DIR.mkdir(exist_ok=True)
NOTES_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# ─── Ollama ──────────────────────────────────────────────
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
FAST_MODEL   = os.getenv("FAST_MODEL",   "qwen2.5:3b")          # Intent + simple chat
SMART_MODEL  = os.getenv("SMART_MODEL",  "mistral:7b")           # Reasoning (what you have)
CODE_MODEL   = os.getenv("CODE_MODEL",   "deepseek-coder:6.7b")  # Code (what you have)
VISION_MODEL = os.getenv("VISION_MODEL", "llava:7b")             # Vision (what you have)
EMBED_MODEL  = os.getenv("EMBED_MODEL",  "nomic-embed-text")     # Embeddings

# ─── Voice / Audio ───────────────────────────────────────
HOTKEY = os.getenv("HOTKEY", "ctrl+shift+j")
WHISPER_MODEL_SIZE   = os.getenv("WHISPER_MODEL_SIZE", "tiny")
WHISPER_DEVICE       = "cpu"
WHISPER_COMPUTE_TYPE = "int8"

SILENCE_THRESHOLD = float(os.getenv("SILENCE_THRESHOLD", "0.01"))
SILENCE_DURATION  = float(os.getenv("SILENCE_DURATION",  "1.5"))
SAMPLE_RATE       = 16000

# ─── TTS ─────────────────────────────────────────────────
PIPER_EXE   = os.getenv("PIPER_EXE",   str(MODELS_DIR / "piper.exe"))
PIPER_MODEL = os.getenv("PIPER_MODEL", str(MODELS_DIR / "en_US-lessac-medium.onnx"))
TTS_BACKEND = os.getenv("TTS_BACKEND", "kokoro")

# ─── Memory ──────────────────────────────────────────────
MAX_SHORT_TERM      = 10
MAX_SEMANTIC_RESULTS = 3
PRIVACY_MODE        = False

# ─── Brain ───────────────────────────────────────────────
COMPLEXITY_WORD_THRESHOLD = 20
MAX_REFLECTION_RETRIES    = 1
OLLAMA_TIMEOUT            = 60

# ─── Safety & Restrictions ──────────────────────────────
PROTECTED_PATHS = [
    "C:\\Windows",
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    "C:\\ProgramData",
    "C:\\Users\\Default",
    "C:\\System Volume Information",
    "C:\\$Recycle.Bin",
    "C:\\Recovery",
    "C:\\Boot",
    os.path.expanduser("~\\AppData"),
    os.path.expanduser("~\\NTUSER.DAT"),
]

PROTECTED_EXTENSIONS = [
    ".sys", ".dll", ".exe", ".msi", ".bat", ".cmd", ".ps1",
    ".reg", ".inf", ".drv", ".ocx", ".cpl",
]

BLOCKED_COMMANDS = [
    "format", "del /s", "rd /s", "rmdir /s", "rm -rf",
    "shutdown", "restart",
    "taskkill /f /im explorer", "taskkill /f /im csrss",
    "taskkill /f /im winlogon", "taskkill /f /im svchost",
    "reg delete", "reg add", "bcdedit", "diskpart",
    "cipher /w", "sfc", "dism", "net user", "net localgroup",
    "icacls", "takeown", "powershell -encodedcommand",
    "powershell -e ", "invoke-expression", "set-executionpolicy",
    "disable-computerrestore", "clear-recyclebin",
    "stop-computer", "restart-computer"
]

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

ALLOWED_WORK_DIRS = [
    os.path.expanduser("~\\Desktop"),
    os.path.expanduser("~\\Documents"),
    os.path.expanduser("~\\Downloads"),
    str(BASE_DIR),
]

# ─── Proactive Engine ───────────────────────────────────
PROACTIVE_CHECK_INTERVAL = 300
MORNING_HOUR             = 8

# ─── Personality ─────────────────────────────────────────
ASSISTANT_NAME = "JARVIS"
SYSTEM_PROMPT = f"""You are {ASSISTANT_NAME}, a highly capable personal AI assistant.
You are concise, helpful, and intelligent. You think step-by-step for complex problems.
You remember the user's preferences and past conversations.
You never execute dangerous system commands or touch protected files.
When unsure, you ask for clarification rather than guessing.
Adapt your tone: brief and focused in the morning, relaxed and conversational in the evening."""

# Maximum file size JARVIS can create (10 MB)
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

# Directories JARVIS is allowed to work in (empty = allow all non-protected)
ALLOWED_WORK_DIRS = [
    os.path.expanduser("~\\Desktop"),
    os.path.expanduser("~\\Documents"),
    os.path.expanduser("~\\Downloads"),
    str(BASE_DIR),
]

# ─── Proactive Engine ───────────────────────────────────
PROACTIVE_CHECK_INTERVAL = 300  # seconds between proactive checks
MORNING_HOUR = 8                # Hour to trigger morning brief (24h format)

# ─── Personality ─────────────────────────────────────────
ASSISTANT_NAME = "JARVIS"
SYSTEM_PROMPT = f"""You are {ASSISTANT_NAME}, a highly capable personal AI assistant. 
You are concise, helpful, and intelligent. You think step-by-step for complex problems.
You remember the user's preferences and past conversations.
You never execute dangerous system commands or touch protected files.
When unsure, you ask for clarification rather than guessing.
Adapt your tone: brief and focused in the morning, relaxed and conversational in the evening."""