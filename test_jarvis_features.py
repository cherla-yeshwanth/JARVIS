import sys
sys.path.append('.')

from brain import Brain
from handlers.chat_handler import ChatHandler
from handlers.system_handler import SystemHandler
from handlers.search_handler import SearchHandler
from handlers.code_handler import CodeHandler
from handlers.memory_handler import MemoryHandler
from handlers.notes_handler import NotesHandler
from handlers.utility_handler import UtilityHandler
from memory import Memory

def print_result(title, result):
    print(f"\n=== {title} ===\n{result}\n")

def main():
    brain = Brain()
    memory = Memory()
    chat = ChatHandler(brain)
    system = SystemHandler(brain)
    search = SearchHandler(brain)
    code = CodeHandler(brain)
    memory_handler = MemoryHandler(memory)
    notes = NotesHandler(memory)
    utility = UtilityHandler()

    print_result("Chat", chat.handle("Hello, how are you?"))
    print_result("System Control (Open Notepad)", system.handle("open notepad"))
    print_result("System Control (System Info)", system.handle("system info"))
    print_result("System Control (Take Screenshot)", system.handle("take screenshot"))
    print_result("Web Search", search.handle("search for Python programming"))
    print_result("Code Assistant", code.handle("Write a Python function to add two numbers"))
    print_result("Memory (Recall)", memory_handler.handle("recall my name"))
    print_result("Notes (Save)", notes.handle("take a note: Buy groceries tomorrow"))
    print_result("Notes (List)", notes.handle("show my notes"))
    print_result("Notes (Search)", notes.handle("search notes for groceries"))
    print_result("Utilities (Calculator)", utility.handle("calculate 2 + 2 * 5"))
    print_result("Utilities (Convert Units)", utility.handle("convert 10 kilometers to miles"))
    print_result("Utilities (Password Generator)", utility.handle("generate a strong password"))

if __name__ == "__main__":
    main()