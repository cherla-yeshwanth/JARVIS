@echo off
title JARVIS Setup
echo ======================================
echo  JARVIS v1.0 — Setup Script
echo ======================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Install Python 3.10+ from python.org
    pause
    exit /b 1
)

:: Create venv if it doesn't exist
if not exist "venv" (
    echo [1/4] Creating virtual environment...
    python -m venv venv
) else (
    echo [1/4] Virtual environment already exists.
)

:: Activate venv and install packages
echo [2/4] Installing Python packages...
call venv\Scripts\activate.bat
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

:: Check Ollama
echo.
echo [3/4] Checking Ollama...
where ollama >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Ollama not found! 
    echo Download from: https://ollama.com/download
    echo After installing, run:
    echo   ollama pull qwen2.5:3b
    echo   ollama pull llama3.1:8b
    echo   ollama pull nomic-embed-text
) else (
    echo Ollama found. Pulling required models...
    ollama pull qwen2.5:3b
    ollama pull nomic-embed-text
    echo.
    echo [Optional] For better reasoning, also run:
    echo   ollama pull llama3.1:8b
)

:: Create .env if needed
if not exist ".env" (
    echo [4/4] Creating default .env file...
    echo # JARVIS Configuration > .env
    echo # Uncomment and modify as needed >> .env
    echo. >> .env
    echo # OLLAMA_HOST=http://localhost:11434 >> .env
    echo # FAST_MODEL=qwen2.5:3b >> .env
    echo # SMART_MODEL=llama3.1:8b >> .env
    echo # HOTKEY=ctrl+shift+j >> .env
    echo # TTS_BACKEND=pyttsx3 >> .env
    echo # WHISPER_MODEL_SIZE=tiny >> .env
) else (
    echo [4/4] .env file already exists.
)

echo.
echo ======================================
echo  Setup complete!
echo ======================================
echo.
echo To start JARVIS:
echo   start.bat           (text mode)
echo   start.bat --voice   (voice mode)
echo.
echo Make sure Ollama is running: ollama serve
echo.
pause