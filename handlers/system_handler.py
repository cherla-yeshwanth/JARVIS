"""
JARVIS v1.0 — System Handler
Windows-native system control: open/close apps, volume, screenshots,
system info, file operations. All with safety checks.
"""

import subprocess
import os
import platform
import json
from pathlib import Path
from safety import validate_command, validate_file_operation
from brain import Brain
import shutil
import webbrowser
import re
from urllib.parse import quote_plus
import fnmatch
import time
import ctypes
try:
    import win32gui
    import win32con
except ImportError:
    win32gui = None
    win32con = None
try:
    import requests
except ImportError:
    requests = None

class SystemHandler:
    """Windows system control handler with safety restrictions."""

    def __init__(self, brain: Brain):
        self.brain = brain
        self._psutil_available = False
        try:
            import psutil
            self._psutil_available = True
        except ImportError:
            print("[SYSTEM] psutil not installed. Some system info unavailable.")

    # ─── App Control ─────────────────────────────────────

    # Common Windows app mappings
    APP_MAP = {
        'whatsapp': 'WhatsApp.exe',
        'chrome': 'chrome.exe',
        'google chrome': 'chrome.exe',
        'firefox': 'firefox.exe',
        'edge': 'msedge.exe',
        'microsoft edge': 'msedge.exe',
        'notepad': 'notepad.exe',
        'calculator': 'calc.exe',
        'calc': 'calc.exe',
        'explorer': 'explorer.exe',
        'file explorer': 'explorer.exe',
        'files': 'explorer.exe',
        'cmd': 'cmd.exe',
        'terminal': 'wt.exe',
        'windows terminal': 'wt.exe',
        'vscode': 'code',
        'vs code': 'code',
        'visual studio code': 'code',
        'spotify': 'spotify.exe',
        'discord': 'discord.exe',
        'slack': 'slack.exe',
        'word': 'winword.exe',
        'excel': 'excel.exe',
        'powerpoint': 'powerpnt.exe',
        'paint': 'mspaint.exe',
        'snipping tool': 'snippingtool.exe',
        'task manager': 'taskmgr.exe',
        'settings': 'ms-settings:',
        'control panel': 'control.exe',
    }


    def _open_app(self, app_name: str) -> str:
        """Open an application or website using Gemini-style strategy."""
        lower = app_name.lower().strip()

        # --- Handle web/YouTube/sectional logic FIRST ---
        known_sites = {
            "youtube": "https://www.youtube.com",
            "gmail": "https://mail.google.com",
            "google": "https://www.google.com",
            "facebook": "https://www.facebook.com",
            "twitter": "https://twitter.com",
            "reddit": "https://www.reddit.com",
            "github": "https://github.com",
            "instagram": "https://www.instagram.com"
        }
        section_map = {
            # Instagram
            "reels on instagram": "https://www.instagram.com/reels/",
            "explore on instagram": "https://www.instagram.com/explore/",
            "profile on instagram": "https://www.instagram.com/accounts/edit/",
            "edit profile on instagram": "https://www.instagram.com/accounts/edit/",
            "messages on instagram": "https://www.instagram.com/direct/inbox/",
            "direct on instagram": "https://www.instagram.com/direct/inbox/",
            "story on instagram": "https://www.instagram.com/stories/",
            "stories on instagram": "https://www.instagram.com/stories/",
            "saved on instagram": "https://www.instagram.com/saved/",
            "notifications on instagram": "https://www.instagram.com/accounts/activity/",
            "posts on instagram": "https://www.instagram.com/",
            "followers on instagram": "https://www.instagram.com/accounts/access_tool/current_followers_and_following",
            "following on instagram": "https://www.instagram.com/accounts/access_tool/current_followers_and_following",
            # Gmail
            "inbox on gmail": "https://mail.google.com/mail/u/0/#inbox",
            "sent on gmail": "https://mail.google.com/mail/u/0/#sent",
            "drafts on gmail": "https://mail.google.com/mail/u/0/#drafts",
            "spam on gmail": "https://mail.google.com/mail/u/0/#spam",
            "starred on gmail": "https://mail.google.com/mail/u/0/#starred",
            "important on gmail": "https://mail.google.com/mail/u/0/#important",
            "snoozed on gmail": "https://mail.google.com/mail/u/0/#snoozed",
            "all mail on gmail": "https://mail.google.com/mail/u/0/#all",
            # Facebook
            "marketplace on facebook": "https://www.facebook.com/marketplace/",
            "groups on facebook": "https://www.facebook.com/groups/",
            "watch on facebook": "https://www.facebook.com/watch/",
            "messages on facebook": "https://www.facebook.com/messages/",
            "notifications on facebook": "https://www.facebook.com/notifications/",
            "profile on facebook": "https://www.facebook.com/me/",
            # Twitter/X
            "explore on twitter": "https://twitter.com/explore",
            "messages on twitter": "https://twitter.com/messages",
            "notifications on twitter": "https://twitter.com/notifications",
            "profile on twitter": "https://twitter.com/home",
            # Reddit
            "popular on reddit": "https://www.reddit.com/r/popular/",
            "all on reddit": "https://www.reddit.com/r/all/",
            "messages on reddit": "https://www.reddit.com/message/inbox/",
            "notifications on reddit": "https://www.reddit.com/notifications/",
            "profile on reddit": "https://www.reddit.com/user/me/",
            # YouTube
            "shorts on youtube": "https://www.youtube.com/shorts/",
            "subscriptions on youtube": "https://www.youtube.com/feed/subscriptions",
            "history on youtube": "https://www.youtube.com/feed/history",
            "library on youtube": "https://www.youtube.com/feed/library",
            "trending on youtube": "https://www.youtube.com/feed/trending",
            "notifications on youtube": "https://www.youtube.com/feed/notifications",
            # Discord
            "messages on discord": "https://discord.com/channels/@me",
            "servers on discord": "https://discord.com/channels/@me",
            "profile on discord": "https://discord.com/channels/@me",
            # Slack
            "messages on slack": "https://slack.com/app",
            "channels on slack": "https://slack.com/app",
            # LinkedIn
            "jobs on linkedin": "https://www.linkedin.com/jobs/",
            "messages on linkedin": "https://www.linkedin.com/messaging/",
            "notifications on linkedin": "https://www.linkedin.com/notifications/",
            "profile on linkedin": "https://www.linkedin.com/in/me/",
        }
        key = lower.replace(" ", "")

        # Sectional commands
        for phrase, url in section_map.items():
            if phrase in lower:
                if 'whatsapp' in phrase:
                    try:
                        os.startfile("whatsapp:")
                        return "Opened WhatsApp Desktop using URI scheme."
                    except Exception:
                        return "Could not open WhatsApp Desktop via URI scheme. Is it installed?"
                else:
                    webbrowser.open(url)
                    return f"Opened {phrase} in your browser."

        # YouTube search/play
        if ("youtube" in lower and ("play " in lower or "search " in lower)):
            user_input = lower
            query = ""
            if "play " in user_input:
                query = user_input.split("play ", 1)[1]
            elif "search " in user_input:
                query = user_input.split("search ", 1)[1]
            if "on youtube" in query:
                query = query.split("on youtube", 1)[0]
            query = query.strip()
            if query:
                encoded_query = quote_plus(query)
                try:
                    import requests, re
                    search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                    resp = requests.get(search_url, headers=headers, timeout=7)
                    match = re.search(r'"videoId":"([^"]+)"', resp.text)
                    if match:
                        video_id = match.group(1)
                        video_url = f"https://www.youtube.com/watch?v={video_id}&autoplay=1"
                        webbrowser.open(video_url)
                        return f"Searched YouTube for '{query}' and played the first result in your browser (auto-play enabled)."
                    else:
                        webbrowser.open(search_url)
                        return f"Searched YouTube for '{query}' in your browser (could not auto-play)."
                except Exception as e:
                    webbrowser.open(f"https://www.youtube.com/results?search_query={encoded_query}")
                    return f"Searched YouTube for '{query}' in your browser (auto-play failed: {e})."
            else:
                try:
                    webbrowser.open(known_sites["youtube"])
                except Exception:
                    subprocess.Popen(['start', known_sites["youtube"]], shell=True)
                return "Opened YouTube in your browser."

        if key in known_sites:
            webbrowser.open(known_sites[key])
            return f"Opened {app_name} in your browser."

        # --- Folder/File search ONLY if ends with 'folder' or 'file' ---
        if lower.endswith(" folder") or lower.endswith(" file"):
            # Fuzzy file/folder search logic (unchanged, moved up)
            fuzzy_lower = lower
            is_folder = False
            is_file = False
            if fuzzy_lower.endswith(" folder"):
                fuzzy_lower = fuzzy_lower[:-7].strip()
                is_folder = True
            elif fuzzy_lower.endswith(" file"):
                fuzzy_lower = fuzzy_lower[:-5].strip()
                is_file = True
            fuzzy_lower = fuzzy_lower.lower()
            search_dirs = [os.getcwd(), str(Path.home() / "Desktop")]
            matches = []
            for base in search_dirs:
                try:
                    for entry in os.listdir(base):
                        entry_path = os.path.join(base, entry)
                        entry_name, entry_ext = os.path.splitext(entry)
                        entry_lc = entry.lower().strip()
                        entry_name_lc = entry_name.lower().strip()
                        if is_folder and os.path.isdir(entry_path) and fuzzy_lower in entry_lc:
                            matches.append(entry_path)
                        elif is_file and os.path.isfile(entry_path) and fuzzy_lower in entry_name_lc:
                            matches.append(entry_path)
                    for root, dirs, files in os.walk(base):
                        for d in dirs:
                            d_lc = d.lower().strip()
                            if is_folder and fuzzy_lower in d_lc:
                                matches.append(os.path.join(root, d))
                        for f in files:
                            name, _ = os.path.splitext(f)
                            name_lc = name.lower().strip()
                            if is_file and fuzzy_lower in name_lc:
                                matches.append(os.path.join(root, f))
                except Exception:
                    pass
            if matches:
                matches = list(dict.fromkeys(matches))
                exact_match = None
                for m in matches:
                    base_name = os.path.basename(m).lower()
                    if base_name == fuzzy_lower:
                        exact_match = m
                        break
                if exact_match:
                    try:
                        os.startfile(exact_match)
                        if os.path.isdir(exact_match):
                            return f"Opened folder: {exact_match}"
                        else:
                            return f"Opened file: {exact_match}"
                    except Exception as e:
                        return f"Could not open {exact_match}: {e}"
                elif len(matches) == 1:
                    try:
                        os.startfile(matches[0])
                        if os.path.isdir(matches[0]):
                            return f"Opened folder: {matches[0]}"
                        else:
                            return f"Opened file: {matches[0]}"
                    except Exception as e:
                        return f"Could not open {matches[0]}: {e}"
                else:
                    msg = [f"Found multiple matches for '{fuzzy_lower}':"]
                    for m in matches[:10]:
                        msg.append(f"  - {m}")
                    if len(matches) > 10:
                        msg.append(f"  ...and {len(matches)-10} more")
                    msg.append("Please specify a more precise name.")
                    return "\n".join(msg)
            else:
                return f"No file or folder found containing '{fuzzy_lower}'."
        else:
            # --- App keyword check: trigger app open logic ---
            app_keywords = [
                "vscode", "vs code", "visual studio code", "chrome", "google chrome", "firefox", "edge", "microsoft edge", "notepad", "calculator", "calc", "explorer", "file explorer", "files", "cmd", "terminal", "windows terminal", "spotify", "discord", "slack", "word", "excel", "powerpoint", "paint", "snipping tool", "task manager", "settings", "control panel", "whatsapp"
            ]
            if lower in app_keywords:
                exe = self.APP_MAP.get(lower)
                if exe:
                    # VS Code special handling
                    if lower in ["vscode", "vs code", "visual studio code"]:
                        try:
                            os.startfile("vscode:")
                            return "Opened VS Code using URI scheme."
                        except Exception:
                            pass
                        try:
                            os.startfile("code")
                            return "Opened VS Code using executable (os.startfile)."
                        except Exception:
                            pass
                        try:
                            subprocess.Popen("code", shell=True)
                            return "Opened VS Code using executable (subprocess)."
                        except Exception:
                            pass
                        user = os.environ.get("USERNAME") or os.environ.get("USER") or ""
                        possible_paths = [
                            rf"C:\Users\{user}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
                            r"C:\Program Files\Microsoft VS Code\Code.exe",
                            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe"
                        ]
                        for path in possible_paths:
                            if os.path.exists(path):
                                try:
                                    subprocess.Popen(f'"{path}"', shell=True)
                                    return f"Opened VS Code from {path}."
                                except Exception:
                                    pass
                        return "Could not open VS Code. Please ensure it is installed and 'code' is in your PATH."
                    if shutil.which(exe):
                        try:
                            subprocess.Popen(exe, shell=True)
                            return f"Opening {lower}."
                        except Exception as e:
                            return f"Failed to open {lower}: {e}"
                    return f"{lower} not found in PATH or standard locations."
            # Fallback: fuzzy file/folder search if not an app
            # ...existing fuzzy search logic below...

        # --- Fuzzy file/folder search logic (unchanged, moved below) ---
        # ...existing code...
        fuzzy_lower = lower.strip().replace("  ", " ")
        for prefix in ["open ", "start ", "launch "]:
            if fuzzy_lower.startswith(prefix):
                fuzzy_lower = fuzzy_lower[len(prefix):].strip()
        for prefix in ["the ", "my "]:
            if fuzzy_lower.startswith(prefix):
                fuzzy_lower = fuzzy_lower[len(prefix):].strip()
        is_folder = False
        is_file = False
        if fuzzy_lower.endswith(" folder"):
            fuzzy_lower = fuzzy_lower[:-7].strip()
            is_folder = True
        elif fuzzy_lower.endswith(" file"):
            fuzzy_lower = fuzzy_lower[:-5].strip()
            is_file = True
        fuzzy_lower = fuzzy_lower.lower()
        search_dirs = [os.getcwd(), str(Path.home() / "Desktop")]
        matches = []
        if fuzzy_lower:
            for base in search_dirs:
                try:
                    for entry in os.listdir(base):
                        entry_path = os.path.join(base, entry)
                        entry_name, entry_ext = os.path.splitext(entry)
                        entry_lc = entry.lower().strip()
                        entry_name_lc = entry_name.lower().strip()
                        if is_folder and os.path.isdir(entry_path) and fuzzy_lower in entry_lc:
                            matches.append(entry_path)
                        elif is_file and os.path.isfile(entry_path) and fuzzy_lower in entry_name_lc:
                            matches.append(entry_path)
                        elif not is_folder and not is_file:
                            if os.path.isdir(entry_path) and fuzzy_lower in entry_lc:
                                matches.append(entry_path)
                            if os.path.isfile(entry_path) and fuzzy_lower in entry_name_lc:
                                matches.append(entry_path)
                    for root, dirs, files in os.walk(base):
                        for d in dirs:
                            d_lc = d.lower().strip()
                            if is_folder and fuzzy_lower in d_lc:
                                matches.append(os.path.join(root, d))
                            elif not is_folder and not is_file and fuzzy_lower in d_lc:
                                matches.append(os.path.join(root, d))
                        for f in files:
                            name, _ = os.path.splitext(f)
                            name_lc = name.lower().strip()
                            if is_file and fuzzy_lower in name_lc:
                                matches.append(os.path.join(root, f))
                            elif not is_folder and not is_file and fuzzy_lower in name_lc:
                                matches.append(os.path.join(root, f))
                except Exception:
                    pass
        if matches:
            matches = list(dict.fromkeys(matches))
            exact_match = None
            for m in matches:
                base_name = os.path.basename(m).lower()
                if base_name == fuzzy_lower:
                    exact_match = m
                    break
            if exact_match:
                try:
                    os.startfile(exact_match)
                    if os.path.isdir(exact_match):
                        return f"Opened folder: {exact_match}"
                    else:
                        return f"Opened file: {exact_match}"
                except Exception as e:
                    return f"Could not open {exact_match}: {e}"
            elif len(matches) == 1:
                try:
                    os.startfile(matches[0])
                    if os.path.isdir(matches[0]):
                        return f"Opened folder: {matches[0]}"
                    else:
                        return f"Opened file: {matches[0]}"
                except Exception as e:
                    return f"Could not open {matches[0]}: {e}"
            else:
                msg = [f"Found multiple matches for '{fuzzy_lower}':"]
                for m in matches[:10]:
                    msg.append(f"  - {m}")
                if len(matches) > 10:
                    msg.append(f"  ...and {len(matches)-10} more")
                msg.append("Please specify a more precise name.")
                return "\n".join(msg)
        elif fuzzy_lower:
            return f"No file or folder found containing '{fuzzy_lower}'."
        path_candidate = Path(app_name).expanduser().resolve()
        if path_candidate.exists():
            try:
                os.startfile(str(path_candidate))
                if path_candidate.is_dir():
                    return f"Opened folder: {path_candidate}"
                else:
                    return f"Opened file: {path_candidate}"
            except Exception as e:
                return f"Could not open {path_candidate}: {e}"

        # WhatsApp Desktop: open using URI scheme if available (no fallback to web)
        if lower in ["whatsapp", "open whatsapp", "start whatsapp", "launch whatsapp"]:
            try:
                os.startfile("whatsapp:")
                return "Opened WhatsApp Desktop using URI scheme."
            except Exception:
                return "Could not open WhatsApp Desktop via URI scheme. Is it installed?"

        # VS Code: open using URI scheme if available, else try executable, else try common install locations
        if lower in ["vscode", "open vscode", "start vscode", "launch vscode", "vs code", "open vs code", "start vs code", "launch vs code", "visual studio code", "open visual studio code", "start visual studio code", "launch visual studio code"]:
            # Try URI scheme
            try:
                os.startfile("vscode:")
                return "Opened VS Code using URI scheme."
            except Exception:
                pass
            # Try os.startfile("code")
            try:
                os.startfile("code")
                return "Opened VS Code using executable (os.startfile)."
            except Exception:
                pass
            # Try subprocess.Popen("code")
            try:
                subprocess.Popen("code", shell=True)
                return "Opened VS Code using executable (subprocess)."
            except Exception:
                pass
            # Try common install locations
            user = os.environ.get("USERNAME") or os.environ.get("USER") or ""
            possible_paths = [
                rf"C:\Users\{user}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
                r"C:\Program Files\Microsoft VS Code\Code.exe",
                r"C:\Program Files (x86)\Microsoft VS Code\Code.exe"
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    try:
                        subprocess.Popen(f'"{path}"', shell=True)
                        return f"Opened VS Code from {path}."
                    except Exception:
                        pass
            return "Could not open VS Code. Please ensure it is installed and 'code' is in your PATH."

        # File Explorer: open using URI scheme if available
        if lower in ["explorer", "open explorer", "start explorer", "launch explorer", "file explorer", "open file explorer", "start file explorer", "launch file explorer", "files", "open files", "start files", "launch files"]:
            try:
                import subprocess
                home_dir = str(Path.home())
                subprocess.Popen(["explorer", home_dir])
                try:
                    import time
                    import ctypes
                    import win32gui
                    import win32con
                    time.sleep(0.5)
                    def enumHandler(hwnd, lParam):
                        if win32gui.IsWindowVisible(hwnd):
                            title = win32gui.GetWindowText(hwnd)
                            if title and "explorer" in title.lower():
                                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                                win32gui.SetForegroundWindow(hwnd)
                    win32gui.EnumWindows(enumHandler, None)
                except Exception:
                    pass
                return "Opened File Explorer and brought it to the foreground."
            except Exception:
                pass

        # Try to open as a desktop app (check PATH and common install locations)
        exe = self.APP_MAP.get(lower)
        if exe:
            if shutil.which(exe):
                try:
                    subprocess.Popen(exe, shell=True)
                    return f"Opening {app_name}."
                except Exception as e:
                    return f"Failed to open {app_name}: {e}"
            browser_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            ]
            for path in browser_paths:
                if exe in path and os.path.exists(path):
                    try:
                        subprocess.Popen(f'"{path}"', shell=True)
                        return f"Opening {app_name} from {path}."
                    except Exception as e:
                        return f"Failed to open {app_name} from {path}: {e}"
            if exe.startswith('ms-'):
                try:
                    os.startfile(exe)
                    return f"Opening {app_name}."
                except Exception as e:
                    return f"Failed to open {app_name} (URI): {e}"
            return f"{app_name} not found in PATH or standard locations."

        # Try to open as a website (if it looks like a URL or has a file extension)
        if app_name.startswith("http") or ("." in app_name and not os.path.exists(app_name)):
            url = app_name if app_name.startswith("http") else f"https://{app_name}"
            webbrowser.open(url)
            return f"Opened {url} in your browser."

        # Fallback: Google search for the app name
        try:
            search_url = f"https://www.google.com/search?q={app_name.replace(' ', '+')}"
            webbrowser.open(search_url)
            return f"Couldn't find a desktop app named '{app_name}'. Searched on Google."
        except Exception as e:
            return f"I couldn't find or open '{app_name}': {e}"

    def _close_app(self, app_name: str) -> str:
        """Close an application by name."""
        lower = app_name.lower().strip()
        exe = self.APP_MAP.get(lower, f'{lower}.exe')

        # Safety: don't kill critical processes
        critical = ['explorer.exe', 'csrss.exe', 'winlogon.exe', 'svchost.exe',
                     'dwm.exe', 'system', 'smss.exe', 'lsass.exe']
        if exe.lower() in critical:
            return f"I can't close {app_name} — it's a critical system process."

        cmd = f'taskkill /im {exe}'
        is_safe, reason = validate_command(cmd)
        if not is_safe:
            return reason

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return f"Closed {app_name}."
            else:
                return f"Couldn't close {app_name}. It may not be running."
        except Exception as e:
            return f"Error closing {app_name}: {e}"

    def _open_coding_setup(self) -> str:
        """Open a typical coding setup: VS Code + Terminal."""
        results = []
        for app in ['vscode', 'terminal']:
            results.append(self._open_app(app))
        return " ".join(results)

    # ─── Volume Control ──────────────────────────────────

    def _set_volume(self, action: str) -> str:
        """Control system volume using PowerShell + nircmd alternative."""
        try:
            if action == 'mute':
                # Use PowerShell with audio management
                ps_cmd = '''
                $wshell = New-Object -ComObject WScript.Shell
                $wshell.SendKeys([char]173)
                '''
                subprocess.run(['powershell', '-c', ps_cmd], capture_output=True, timeout=5)
                return "Volume muted."
            elif action == 'unmute':
                ps_cmd = '''
                $wshell = New-Object -ComObject WScript.Shell
                $wshell.SendKeys([char]173)
                '''
                subprocess.run(['powershell', '-c', ps_cmd], capture_output=True, timeout=5)
                return "Volume toggled."
            elif action == 'up':
                ps_cmd = '''
                $wshell = New-Object -ComObject WScript.Shell
                for ($i = 0; $i -lt 5; $i++) { $wshell.SendKeys([char]175) }
                '''
                subprocess.run(['powershell', '-c', ps_cmd], capture_output=True, timeout=5)
                return "Volume increased."
            elif action == 'down':
                ps_cmd = '''
                $wshell = New-Object -ComObject WScript.Shell
                for ($i = 0; $i -lt 5; $i++) { $wshell.SendKeys([char]174) }
                '''
                subprocess.run(['powershell', '-c', ps_cmd], capture_output=True, timeout=5)
                return "Volume decreased."
            else:
                return f"Unknown volume action: {action}"
        except Exception as e:
            return f"Volume control error: {e}"

    # ─── Screenshot ──────────────────────────────────────

    def _take_screenshot(self) -> str:
        """Take a screenshot and save to JARVIS data/screenshots folder."""
        try:
            from datetime import datetime
            jarvis_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "screenshots")
            os.makedirs(jarvis_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = os.path.join(jarvis_dir, f'screenshot_{timestamp}.png')

            # Use PowerShell to take screenshot
            ps_cmd = f'''
            Add-Type -AssemblyName System.Windows.Forms
            $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
            $bitmap = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
            $bitmap.Save("{filepath}")
            $graphics.Dispose()
            $bitmap.Dispose()
            '''
            subprocess.run(['powershell', '-c', ps_cmd], capture_output=True, timeout=10)

            if os.path.exists(filepath):
                return f"Screenshot saved to {filepath}"
            else:
                return "Screenshot may have failed. Check the JARVIS screenshots folder."
        except Exception as e:
            return f"Screenshot error: {e}"

    # ─── System Info ─────────────────────────────────────

    def _get_system_info(self) -> str:
        """Get system information."""
        info = [f"OS: {platform.system()} {platform.release()}"]

        if self._psutil_available:
            import psutil
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            info.append(f"CPU Usage: {cpu_percent}%")

            # Memory
            mem = psutil.virtual_memory()
            info.append(f"RAM: {mem.used // (1024**3):.1f} GB / {mem.total // (1024**3):.1f} GB ({mem.percent}%)")

            # Disk
            disk = psutil.disk_usage('C:\\')
            info.append(f"Disk (C:): {disk.used // (1024**3):.0f} GB / {disk.total // (1024**3):.0f} GB ({disk.percent}%)")

            # Battery
            battery = psutil.sensors_battery()
            if battery:
                plug = "plugged in" if battery.power_plugged else "on battery"
                info.append(f"Battery: {battery.percent}% ({plug})")

        return "\n".join(info)

    def _get_top_processes(self, n: int = 5) -> str:
        """Get top CPU-consuming processes."""
        if not self._psutil_available:
            return "psutil not installed. Can't show processes."
        import psutil
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                procs.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        procs.sort(key=lambda x: x.get('cpu_percent', 0) or 0, reverse=True)
        lines = [f"Top {n} processes by CPU:"]
        for p in procs[:n]:
            name = p.get('name', 'Unknown')
            cpu = p.get('cpu_percent', 0) or 0
            mem = p.get('memory_percent', 0) or 0
            lines.append(f"  • {name}: CPU {cpu:.1f}%, RAM {mem:.1f}%")
        return "\n".join(lines)

    def _get_ip_address(self) -> str:
        """Get local IP address."""
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return f"Your local IP address is: {ip}"
        except Exception:
            return "Could not determine IP address."

    # ─── File Operations ─────────────────────────────────

    def _list_files(self, directory: str) -> str:
        """List files in a directory."""
        try:
            path = Path(directory).expanduser().resolve()
            if not path.exists():
                return f"Directory not found: {directory}"
            if not path.is_dir():
                return f"Not a directory: {directory}"

            items = list(path.iterdir())
            if not items:
                return f"Directory is empty: {directory}"

            dirs = sorted([i.name for i in items if i.is_dir()])
            files = sorted([i.name for i in items if i.is_file()])

            lines = [f"Contents of {path}:"]
            for d in dirs[:20]:
                lines.append(f"  📁 {d}")
            for f in files[:20]:
                lines.append(f"  📄 {f}")
            if len(items) > 40:
                lines.append(f"  ... and {len(items) - 40} more items")
            return "\n".join(lines)
        except Exception as e:
            return f"Error listing files: {e}"

    def _read_file(self, filepath: str) -> str:
        """Read a text file's contents."""
        try:
            path = Path(filepath).expanduser().resolve()
            if not path.exists():
                return f"File not found: {filepath}"
            if not path.is_file():
                return f"Not a file: {filepath}"
            if path.stat().st_size > 1024 * 1024:  # 1MB limit for reading
                return "File is too large to read (>1MB)."

            content = path.read_text(encoding='utf-8', errors='replace')
            return f"Contents of {path.name}:\n{content[:3000]}"
        except Exception as e:
            return f"Error reading file: {e}"

    def _create_file(self, filepath: str, content: str) -> str:
        """Create a file with content."""
        is_safe, reason = validate_file_operation('create', filepath)
        if not is_safe:
            return reason
        try:
            path = Path(filepath).expanduser().resolve()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            return f"File created: {path}"
        except Exception as e:
            return f"Error creating file: {e}"

    def _delete_file(self, filepath: str) -> str:
        """Delete a single file (never directories)."""
        is_safe, reason = validate_file_operation('delete', filepath)
        if not is_safe:
            return reason
        try:
            path = Path(filepath).expanduser().resolve()
            if not path.exists():
                return f"File not found: {filepath}"
            if path.is_dir():
                return "I can't delete directories for safety. Delete files individually."
            path.unlink()
            return f"Deleted: {path}"
        except Exception as e:
            return f"Error deleting file: {e}"

    # ─── Main Handler ────────────────────────────────────

    def handle(self, user_input: str, context: str = '') -> str:
        """Route system commands to appropriate handler."""
        lower = user_input.lower().strip()

        # Always perform a web search for 'search' commands
        if lower.startswith('search '):
            import webbrowser
            query = user_input[7:].strip()
            if not query:
                return "Please specify what you want to search for."
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            try:
                webbrowser.open(search_url)
                return f"Searched Google for '{query}'."
            except Exception as e:
                return f"Failed to search Google: {e}"

        # WhatsApp Web: only open main page for WhatsApp-related commands
        if lower in ["whatsapp", "open whatsapp", "start whatsapp", "launch whatsapp"]:
            return self._open_app(user_input)

        # YouTube search/play direct handling
        if ("youtube" in lower and ("play " in lower or "search " in lower)):
            return self._open_app(user_input)

        # Open apps/files/folders for 'open', 'launch', 'start' commands
        if any(lower.startswith(w) for w in ['open ', 'launch ', 'start ']):
            app = lower.split(maxsplit=1)[1] if ' ' in lower else ''
            if 'coding setup' in lower or 'dev setup' in lower:
                return self._open_coding_setup()
            return self._open_app(app)

        # Close apps
        if any(lower.startswith(w) for w in ['close ', 'kill ', 'stop ']):
            app = lower.split(maxsplit=1)[1] if ' ' in lower else ''
            return self._close_app(app)

        # Volume
        if 'volume' in lower or 'mute' in lower or 'unmute' in lower:
            if 'up' in lower or 'increase' in lower or 'raise' in lower:
                return self._set_volume('up')
            elif 'down' in lower or 'decrease' in lower or 'lower' in lower:
                return self._set_volume('down')
            elif 'unmute' in lower:
                return self._set_volume('unmute')
            elif 'mute' in lower:
                return self._set_volume('mute')
            return self._set_volume('up')

        # Screenshot
        if 'screenshot' in lower or 'screen capture' in lower:
            return self._take_screenshot()

        # System info
        if any(w in lower for w in ['system info', 'system status', 'battery', 'cpu usage', 'disk space', 'ram']):
            return self._get_system_info()

        # IP address
        if 'ip address' in lower or 'my ip' in lower:
            return self._get_ip_address()

        # Processes
        if 'process' in lower or 'what is eating' in lower or 'top process' in lower:
            return self._get_top_processes()

        # File operations
        if 'list files' in lower or 'show files' in lower:
            parts = lower.replace('list files', '').replace('show files', '').replace('in ', '').strip()
            directory = parts if parts else os.path.expanduser('~\\Desktop')
            return self._list_files(directory)

        if 'read file' in lower:
            filepath = lower.replace('read file', '').strip()
            return self._read_file(filepath)

        # Fallback: ask LLM to interpret the system command
        return self.brain.generate_response(
            f"The user wants to perform a system action: {user_input}. "
            f"Describe what they likely want done, but note that I can only open/close apps, "
            f"control volume, take screenshots, and manage files.",
            context
        )