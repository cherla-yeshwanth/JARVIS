import subprocess
import sys
import os
import time
import psutil

try:
    import keyboard
except ImportError:
    print("[LAUNCHER] Please install the 'keyboard' package: pip install keyboard")
    sys.exit(1)

JARVIS_PROCESS_NAME = "main.py"
JARVIS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")


def is_jarvis_running():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and any(JARVIS_PROCESS_NAME in arg for arg in cmdline):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False


def launch_jarvis():
    if is_jarvis_running():
        print("[LAUNCHER] JARVIS is already running.")
        return
    print("[LAUNCHER] Launching JARVIS...")
    subprocess.Popen([sys.executable, JARVIS_PATH])


def main():
    print("[LAUNCHER] Listening for Ctrl+Space to launch JARVIS.")
    keyboard.add_hotkey('ctrl+space', launch_jarvis)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[LAUNCHER] Exiting.")

if __name__ == '__main__':
    main()
