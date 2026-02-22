# JARVIS Feature List

This file enumerates every action and capability JARVIS can perform, based on all handlers, modules, and workflows. No feature is omitted.

---

## Core Actions

- **Smart Chat**: General conversation, chain-of-thought reasoning, explanations, tips, and self-reflection
- **Voice Control**: Hotkey-activated voice input, speech-to-text (faster-whisper, SpeechRecognition)
- **Text-to-Speech**: Speak responses using Piper TTS, Windows SAPI, Kokoro, Misaki, gTTS
- **Wake Word Detection**: ONNX-based wake word engine, start/stop listening

---

## System Control

- Open applications (e.g., Chrome, Notepad, VS Code, Discord, Slack, LinkedIn, WhatsApp)
- Close applications by name
- Open websites and URI schemes (e.g., WhatsApp Desktop)
- Open coding setup (VS Code + Terminal)
- Run shell/system commands
- List files, folders, and directories
- Read files
- Take screenshots
- Get system info (CPU, RAM, disk space, battery, IP address, WiFi)
- Control system volume (increase, decrease, mute, unmute)
- Safety checks for commands and file operations

---

## Web Search

- Search the web (DuckDuckGo, Google)
- Summarize web results
- Search for news
- Look up facts, people, events

---

## Code Assistant

- Write code in Python, JavaScript, and other languages
- Debug code
- Fix code
- Explain code and regex
- Generate scripts, functions, algorithms

---

## Memory Management

- Save facts and preferences (e.g., name, likes, dislikes)
- Recall facts ("What do you know about me?")
- Privacy mode (clear memory)
- Export memory to markdown
- Fuzzy search memory
- Delete memory entries

---

## Notes

- Take voice/text notes
- List notes
- Search notes
- Delete notes
- Export notes to markdown

---

## Utilities

- Calculator (math operations)
- Unit conversion (e.g., km to miles)
- Password generation (custom length, strong passwords)
- Uppercase/lowercase conversion
- Word/character count
- Random number generation

---

## Vision & UI Automation

- Take screen capture
- Describe screen contents (via llava:7b)
- Click at coordinates
- Scroll up/down
- Type text
- Read/see/describe what is on screen

---

## Phone & WhatsApp Control

- Open WhatsApp Desktop
- Find contacts and search bar
- Type contact name
- Simulate phone calls (call, dial, ring, hang up, answer, reject)
- Simulate SMS/text sending
- Simulate phone notifications

---

## Proactive Engine

- Morning briefs
- Pattern detection
- Reminders (e.g., "Remind me to drink water")
- Background task scheduling

---

## Safety & Protection

- Blocked commands and protected paths
- Safe execution of system actions

---

## Integration & Extensibility

- Handler-based modular architecture
- Intent classification and routing
- Support for new models and TTS layers
- Extensible workflows (n8n, JSON)

---

## Other Actions

- Export memory and notes
- Privacy mode
- Intent filtering
- Hotkey listener
- Semantic search (ChromaDB)

---

## Model Support

- Ollama models: llava:7b, mistral:7b, deepseek-coder:6.7b, qwen2.5:3b, nomic-embed-text

---

**This list is exhaustive and covers every action JARVIS can perform as of February 22, 2026.**
