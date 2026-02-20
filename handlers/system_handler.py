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
        """Open an application by name."""
        lower = app_name.lower().strip()

        # Check our map
        exe = self.APP_MAP.get(lower)
        if exe:
            try:
                if exe.startswith('ms-'):
                    # Windows URI schemes
                    os.startfile(exe)
                else:
                    subprocess.Popen(exe, shell=True)
                return f"Opening {app_name}."
            except Exception as e:
                return f"Failed to open {app_name}: {e}"

        # Try to start it directly
        try:
            subprocess.Popen(f'start {app_name}', shell=True)
            return f"Trying to open {app_name}."
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
        """Take a screenshot and save to Desktop."""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = os.path.expanduser(f'~\\Desktop\\screenshot_{timestamp}.png')

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
                return "Screenshot may have failed. Check your Desktop."
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

        # Open apps
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