# 🤖 JARVIS v1.0 — Personal AI Assistant

A fully offline, zero-cost personal AI assistant for Windows. Built with Python, powered by Ollama local LLMs, with voice control, long-term memory, and system automation.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 💬 **Smart Chat** | Chain-of-thought reasoning with self-reflection |
| 🎤 **Voice Control** | Hotkey-activated voice input (faster-whisper STT) |
| 🔊 **Text-to-Speech** | Piper TTS or Windows SAPI voices |
| 🧠 **Long-Term Memory** | SQLite facts + ChromaDB semantic search |
| 🔍 **Web Search** | DuckDuckGo (no API key needed) |
| 🖥️ **System Control** | Open/close apps, volume, screenshots |
| 💻 **Code Assistant** | Write, debug, and explain code |
| 📝 **Voice Notes** | Save, search, and manage notes |
| 🧮 **Utilities** | Calculator, unit converter, password generator |
| 🛡️ **Safety System** | Protected paths, blocked commands, safe execution |
| 🔮 **Proactive Engine** | Morning briefs, pattern detection |
| 🔒 **Privacy Mode** | Disable memory storage on demand |

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** — [python.org](https://www.python.org/downloads/)
- **Ollama** — [ollama.com](https://ollama.com/download)

### Setup (one-time)
```batch
:: 1. Run the setup script
setup.bat

:: 2. Pull the required Ollama models
ollama pull qwen2.5:3b
ollama pull nomic-embed-text

:: 3. (Optional) Pull the smart model for complex tasks
ollama pull llama3.1:8b
```

### Run
```batch
:: Text mode (type commands)
start.bat

:: Voice mode (press Ctrl+Shift+J to talk)
start.bat --voice

:: Without proactive engine
start.bat --no-proactive
```

## 🏗️ Architecture

```
User Input (Voice/Text)
        │
        ▼
   ┌─────────┐
   │  Brain   │  ← Intent classification + model selection
   │ (Ollama) │  ← Chain-of-thought reasoning
   │          │  ← Self-reflection loop
   └────┬─────┘
        │
        ▼
   ┌──────────┐     ┌──────────┐
   │ Executor  │────▶│ Handlers │
   │ (Router)  │     │ (7 types)│
   └────┬──────┘     └──────────┘
        │
        ▼
   ┌──────────┐
   │  Memory   │  ← Short-term (RAM)
   │  System   │  ← Facts (SQLite)
   │           │  ← Episodes (ChromaDB)
   └──────────┘
```

### File Structure
```
JARVIS/
├── main.py              # Entry point
├── config.py            # All settings
├── brain.py             # AGI brain (intent, CoT, reflection)
├── memory.py            # Memory system (SQLite + ChromaDB)
├── executor.py          # Task dispatcher
├── voice_layer.py       # STT + hotkey listener
├── tts.py               # Text-to-speech
├── safety.py            # Safety restrictions
├── proactive.py         # Background proactive engine
├── handlers/
│   ├── chat_handler.py     # General conversation
│   ├── search_handler.py   # Web search + summarization
│   ├── system_handler.py   # Windows system control
│   ├── code_handler.py     # Code generation
│   ├── memory_handler.py   # Memory management
│   ├── notes_handler.py    # Voice notes
│   └── utility_handler.py  # Calculator, converter, etc.
├── data/                # SQLite DB, ChromaDB, exports
├── models/              # Piper TTS models (optional)
├── setup.bat            # One-time setup
├── start.bat            # Launch script
├── requirements.txt     # Python dependencies
└── .env                 # User configuration overrides
```

## 💡 Usage Examples

### Chat
```
You: What's the difference between a list and a tuple in Python?
You: Give me 3 tips for better sleep
You: Explain quantum computing simply
```

### System Control
```
You: Open Chrome
You: Take a screenshot
You: System info
You: Volume up
You: Close notepad
```

### Search
```
You: Search for latest news about AI
You: Who is the president of France?
You: Look up Python 3.12 new features
```

### Code
```
You: Write a Python function to find prime numbers
You: Debug this code: def add(a, b): return a - b
You: Explain this regex: ^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$
```

### Memory
```
You: My name is Yeshwanth
You: I prefer dark mode
You: What do you know about me?
You: Privacy mode on
You: Export memory
```

### Notes
```
You: Take a note: Buy groceries tomorrow
You: Show my notes
You: Search notes for groceries
```

### Utilities
```
You: Calculate 15 * 27 + 3
You: Convert 100 km to miles
You: Generate a 20 character password
You: Uppercase hello world
```

## ⚙️ Configuration

Edit `.env` or `config.py` to customize:

| Setting | Default | Description |
|---------|---------|-------------|
| `FAST_MODEL` | `qwen2.5:3b` | Quick tasks & intent classification |
| `SMART_MODEL` | `llama3.1:8b` | Complex reasoning |
| `HOTKEY` | `ctrl+shift+j` | Voice activation hotkey |
| `TTS_BACKEND` | `pyttsx3` | TTS engine (`piper` or `pyttsx3`) |
| `WHISPER_MODEL_SIZE` | `tiny` | STT model size |
| `PRIVACY_MODE` | `False` | Disable memory storage |

## 🛡️ Safety

JARVIS has a comprehensive safety system:
- **Protected directories**: Windows system folders are off-limits
- **Protected extensions**: Cannot modify `.exe`, `.dll`, `.sys`, etc.
- **Blocked commands**: Dangerous commands like `format`, `del /s`, `shutdown` are blocked
- **File size limits**: Cannot create files larger than 10 MB
- **No recursive deletion**: Directory deletion is always blocked
- **Allowed work dirs**: Only Desktop, Documents, Downloads, and JARVIS folder

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Ollama not running" | Run `ollama serve` in a terminal |
| "Model not found" | Run `ollama pull qwen2.5:3b` |
| No sound from TTS | Check Windows audio settings |
| Voice not working | Install `faster-whisper` and check microphone |
| Slow responses | Use `tiny` whisper model, use `qwen2.5:3b` only |

## 📄 License

MIT License — Free for personal use.

---
*Built with ❤️ — 100% free, 100% offline, 100% yours.*