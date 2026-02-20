"""
JARVIS v1.0 — Safety & Restrictions Module
Prevents JARVIS from executing dangerous operations.
This module is checked BEFORE any system command or file operation.
"""

import os
import re
from pathlib import Path
from config import (
    PROTECTED_PATHS,
    PROTECTED_EXTENSIONS,
    BLOCKED_COMMANDS,
    MAX_FILE_SIZE_BYTES,
    ALLOWED_WORK_DIRS,
)


def is_path_protected(filepath: str) -> bool:
    """Check if a file path is in a protected directory."""
    try:
        resolved = str(Path(filepath).resolve()).lower()
        for protected in PROTECTED_PATHS:
            if resolved.startswith(protected.lower()):
                return True
        return False
    except Exception:
        return True  # If we can't resolve the path, treat it as protected


def is_extension_protected(filepath: str) -> bool:
    """Check if a file has a protected extension."""
    ext = Path(filepath).suffix.lower()
    return ext in [e.lower() for e in PROTECTED_EXTENSIONS]


def is_path_in_allowed_dirs(filepath: str) -> bool:
    """Check if a path is within allowed working directories."""
    if not ALLOWED_WORK_DIRS:
        return not is_path_protected(filepath)
    try:
        resolved = str(Path(filepath).resolve()).lower()
        for allowed in ALLOWED_WORK_DIRS:
            if resolved.startswith(allowed.lower()):
                return True
        return False
    except Exception:
        return False


def is_command_blocked(command: str) -> bool:
    """Check if a command contains any blocked patterns."""
    cmd_lower = command.lower().strip()
    for blocked in BLOCKED_COMMANDS:
        if blocked.lower() in cmd_lower:
            return True
    # Additional pattern checks
    dangerous_patterns = [
        r'del\s+/[sfq]',           # del with force/quiet/subdirectory flags
        r'rmdir\s+/[sq]',          # rmdir with force flags
        r'format\s+[a-z]:',        # format any drive
        r'>\s*\\\\',               # redirect to network paths
        r'net\s+share',            # network share manipulation
        r'wmic\s+os\s+delete',     # WMI OS deletion
        r'powershell.*-enc',       # encoded PowerShell commands
        r'cmd.*\/c.*del\s',        # nested cmd delete
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, cmd_lower):
            return True
    return False


def validate_file_operation(operation: str, filepath: str) -> tuple[bool, str]:
    """
    Validate a file operation before executing it.
    Returns (is_safe, reason).
    """
    if is_path_protected(filepath):
        return False, f"BLOCKED: '{filepath}' is in a protected system directory."

    if operation in ("delete", "modify", "write"):
        if is_extension_protected(filepath):
            return False, f"BLOCKED: Cannot {operation} files with extension '{Path(filepath).suffix}'."

    if operation in ("write", "create", "modify"):
        if not is_path_in_allowed_dirs(filepath):
            return False, f"BLOCKED: '{filepath}' is outside allowed working directories."

    if operation == "delete":
        if not is_path_in_allowed_dirs(filepath):
            return False, f"BLOCKED: Cannot delete files outside allowed directories."
        # Never allow deleting directories recursively
        if os.path.isdir(filepath):
            return False, "BLOCKED: Recursive directory deletion is not allowed. Delete files individually."

    return True, "OK"


def validate_command(command: str) -> tuple[bool, str]:
    """
    Validate a system command before executing it.
    Returns (is_safe, reason).
    """
    if is_command_blocked(command):
        return False, f"BLOCKED: Command contains a restricted operation. Command: '{command}'"

    # Check if command tries to access protected paths
    cmd_lower = command.lower()
    for protected in PROTECTED_PATHS:
        if protected.lower() in cmd_lower:
            # Allow read-only operations on protected paths
            read_only_cmds = ["dir", "type", "echo", "findstr", "where", "systeminfo"]
            if not any(cmd_lower.strip().startswith(c) for c in read_only_cmds):
                return False, f"BLOCKED: Command accesses protected path '{protected}'."

    return True, "OK"


def validate_file_size(content: str) -> tuple[bool, str]:
    """Check if content exceeds maximum file size."""
    size = len(content.encode('utf-8'))
    if size > MAX_FILE_SIZE_BYTES:
        return False, f"BLOCKED: Content size ({size} bytes) exceeds maximum ({MAX_FILE_SIZE_BYTES} bytes)."
    return True, "OK"


def get_safety_summary() -> str:
    """Return a human-readable summary of safety restrictions."""
    return f"""
🛡️ JARVIS Safety Restrictions:
• Protected directories: {len(PROTECTED_PATHS)} system paths are off-limits
• Protected extensions: {', '.join(PROTECTED_EXTENSIONS[:5])}... ({len(PROTECTED_EXTENSIONS)} total)
• Blocked commands: {len(BLOCKED_COMMANDS)} dangerous command patterns
• Max file size: {MAX_FILE_SIZE_BYTES // (1024*1024)} MB
• Allowed work dirs: {', '.join(os.path.basename(d) for d in ALLOWED_WORK_DIRS)}
• Recursive deletion: ALWAYS blocked
"""