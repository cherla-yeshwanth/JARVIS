"""
JARVIS v1.0 — Notes Handler
Voice notes: save, search, list, and delete timestamped notes.
"""

import os
from datetime import datetime
from pathlib import Path
from config import NOTES_DIR

class NotesHandler:
    """Voice notes management handler."""

    def __init__(self, memory):
        self.memory = memory
        self.notes_dir = Path(NOTES_DIR)
        self.notes_dir.mkdir(parents=True, exist_ok=True)

    def _save_note(self, content: str) -> str:
        """Save a timestamped note."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        filename = f"note_{timestamp}.md"
        filepath = self.notes_dir / filename

        note_content = f"# Note — {date_str}\n\n{content}\n"
        filepath.write_text(note_content, encoding='utf-8')
        return f"Note saved: {filename}"

    def _list_notes(self, limit: int = 10) -> str:
        """List recent notes."""
        notes = sorted(self.notes_dir.glob('note_*.md'), reverse=True)
        if not notes:
            return "You don't have any notes yet."

        lines = [f"📝 Your notes ({len(notes)} total):"]
        for note in notes[:limit]:
            try:
                first_line = note.read_text(encoding='utf-8').split('\n')[0]
                # Remove markdown header
                first_line = first_line.lstrip('# ').strip()
                lines.append(f"  • {note.stem}: {first_line}")
            except Exception:
                lines.append(f"  • {note.stem}")

        if len(notes) > limit:
            lines.append(f"  ... and {len(notes) - limit} more")
        return "\n".join(lines)

    def _search_notes(self, query: str) -> str:
        """Search notes by content."""
        notes = sorted(self.notes_dir.glob('note_*.md'), reverse=True)
        if not notes:
            return "No notes to search."

        matches = []
        query_lower = query.lower()
        for note in notes:
            try:
                content = note.read_text(encoding='utf-8')
                if query_lower in content.lower():
                    # Get first 100 chars of match context
                    idx = content.lower().index(query_lower)
                    start = max(0, idx - 30)
                    end = min(len(content), idx + len(query) + 70)
                    snippet = content[start:end].replace('\n', ' ').strip()
                    matches.append(f"  • {note.stem}: ...{snippet}...")
            except Exception:
                pass

        if not matches:
            return f"No notes found matching '{query}'."

        lines = [f"Found {len(matches)} notes matching '{query}':"] + matches[:10]
        return "\n".join(lines)

    def _read_note(self, identifier: str) -> str:
        """Read a specific note."""
        # Try to find by partial name match
        notes = list(self.notes_dir.glob(f'*{identifier}*.md'))
        if not notes:
            return f"No note found matching '{identifier}'."
        
        note = notes[0]
        content = note.read_text(encoding='utf-8')
        return f"📄 {note.name}:\n{content}"

    def _delete_note(self, identifier: str) -> str:
        """Delete a specific note."""
        notes = list(self.notes_dir.glob(f'*{identifier}*.md'))
        if not notes:
            return f"No note found matching '{identifier}'."
        
        note = notes[0]
        note.unlink()
        return f"Deleted note: {note.name}"

    def handle(self, user_input: str, context: str = '') -> str:
        """Route notes commands."""
        # Input validation
        if not isinstance(user_input, str) or not user_input.strip():
            return "Sorry, I didn't receive any input."
        try:
            lower = user_input.lower().strip()

            # Save a note
            if any(lower.startswith(w) for w in ['take a note', 'save a note', 'note that', 'note:']):
                # Extract the note content
                for prefix in ['take a note:', 'take a note', 'save a note:', 'save a note',
                              'note that', 'note:']:
                    if lower.startswith(prefix):
                        content = user_input[len(prefix):].strip()
                        break
                else:
                    content = user_input

                if not content:
                    return "What should I note down?"
                return self._save_note(content)

            # List notes
            if any(w in lower for w in ['my notes', 'show notes', 'list notes', 'all notes']):
                return self._list_notes()

            # Search notes
            if 'search notes' in lower or 'find note' in lower:
                query = lower.replace('search notes', '').replace('find note', '').replace('for', '').strip()
                if not query:
                    return "What should I search for in your notes?"
                return self._search_notes(query)

            # Delete note
            if 'delete note' in lower or 'remove note' in lower:
                identifier = lower.replace('delete note', '').replace('remove note', '').strip()
                if not identifier:
                    return "Which note should I delete? Provide the note name or part of it."
                return self._delete_note(identifier)

            # Default: treat as a note to save
            content = user_input
            for prefix in ['take a note', 'save a note', 'note that', 'note']:
                if lower.startswith(prefix):
                    content = user_input[len(prefix):].strip()
                    break
            if content:
                return self._save_note(content)
            return "I can take notes, search them, or list them. What would you like?"
        except Exception as e:
            return f"Sorry, an error occurred: {e}"
