"""
JARVIS v1.0 — Execution Handlers
Each handler is responsible for one type of task.
"""

from handlers.chat_handler import ChatHandler
from handlers.search_handler import SearchHandler
from handlers.system_handler import SystemHandler
from handlers.code_handler import CodeHandler
from handlers.memory_handler import MemoryHandler
from handlers.notes_handler import NotesHandler
from handlers.utility_handler import UtilityHandler

__all__ = [
    'ChatHandler',
    'SearchHandler',
    'SystemHandler',
    'CodeHandler',
    'MemoryHandler',
    'NotesHandler',
    'UtilityHandler',
]