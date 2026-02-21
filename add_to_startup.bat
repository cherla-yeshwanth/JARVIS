@echo off
REM Add jarvis_launcher.py to Windows Startup
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set JARVIS_DIR=%~dp0
set PYTHON_EXE=pythonw.exe

REM Create a shortcut to run jarvis_launcher.py with pythonw.exe (no console window)
set SHORTCUT_PATH=%STARTUP_DIR%\Jarvis Launcher.lnk
set TARGET_PATH=%PYTHON_EXE% "%JARVIS_DIR%jarvis_launcher.py"

REM Use PowerShell to create the shortcut
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); $Shortcut.TargetPath = '%PYTHON_EXE%'; $Shortcut.Arguments = '"%JARVIS_DIR%jarvis_launcher.py"'; $Shortcut.WorkingDirectory = '%JARVIS_DIR%'; $Shortcut.Save()"

echo Jarvis Launcher added to Windows Startup.
pause
