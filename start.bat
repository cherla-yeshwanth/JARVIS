@echo off
title JARVIS v1.0
echo Starting JARVIS...

:: Activate venv
call venv\Scripts\activate.bat

:: Start Ollama if not running
tasklist /fi "imagename eq ollama.exe" | find "ollama.exe" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Starting Ollama...
    start /min "" ollama serve
    timeout /t 3 /nobreak >nul
)

:: Run JARVIS
python main.py %*