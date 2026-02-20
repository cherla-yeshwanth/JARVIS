"""
JARVIS v1.0 — Memory Handler
Handles memory-related requests: recall, search, privacy, export, wipe.
"""

import os
from datetime import datetime
from memory import Memory
from config import DATA_DIR

class MemoryHandler:
    """Memory management handler."""

    def __init__(self, memory: Memory):
        self.memory = memory

    def handle(self, user_input: str, context: str = '') -> str:
        """Route memory commands."""
        lower = user_input.lower().strip()

        # Privacy mode
        if 'privacy mode' in lower or 'go private' in lower:
            if 'off' in lower or 'disable' in lower or 'stop' in lower:
                self.memory.set_privacy_mode(False)
                return "Privacy mode disabled. I'll remember our conversations again."
            else:
                self.memory.set_privacy_mode(True)
                return "Privacy mode enabled. I won't store any new memories until you turn it off."

        # Export memories
        if 'export' in lower:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = str(DATA_DIR / f'jarvis_export_{timestamp}.json')
            return self.memory.export_memories(filepath)

        # Wipe all memories
        if 'wipe memory' in lower or 'wipe all' in lower or 'delete all memories' in lower:
            confirm = 'confirm' in lower
            return self.memory.wipe_memories(confirm=confirm)

        # Forget about specific topic
        if 'forget' in lower:
            topic = lower.replace('forget about', '').replace('forget', '').strip()
            if topic:
                return self.memory.forget_about(topic)
            return "What should I forget? Say 'forget about [topic]'."

        # Conversation analytics
        if 'analytics' in lower or 'statistics' in lower or 'stats' in lower:
            analytics = self.memory.get_conversation_analytics()
            lines = [
                f"📊 Conversation Analytics:",
                f"  Total conversations: {analytics['total_conversations']}",
                f"  Recent sessions: {analytics['recent_sessions']}",
            ]
            if analytics['by_intent']:
                lines.append("  By type:")
                for intent, count in analytics['by_intent'].items():
                    lines.append(f"    • {intent}: {count}")
            if analytics['most_active_hours']:
                lines.append("  Most active hours:")
                for hour, count in list(analytics['most_active_hours'].items())[:3]:
                    lines.append(f"    • {hour}:00 — {count} conversations")
            return "\n".join(lines)

        # What do you know about me?
        if 'know about me' in lower or 'my profile' in lower or 'my facts' in lower:
            facts = self.memory.get_facts()
            if not facts:
                return "I don't have any stored facts about you yet. Tell me about yourself!"
            lines = ["Here's what I know about you:"]
            for category, key, value in facts:
                lines.append(f"  • [{category}] {key}: {value}")
            return "\n".join(lines)

        # Search past conversations
        if 'what did i say' in lower or 'what did we' in lower or 'do you remember' in lower:
            query = lower.replace('what did i say about', '').replace('what did we talk about', '')
            query = query.replace('do you remember', '').strip()
            if not query:
                # Show recent conversations
                recent = self.memory.get_recent_conversations(5)
                if not recent:
                    return "We haven't had any conversations yet."
                lines = ["Recent conversations:"]
                for user_in, resp, intent, ts in recent:
                    lines.append(f"  [{ts}] You: {user_in[:80]}")
                    lines.append(f"           Me: {resp[:80]}")
                return "\n".join(lines)

            episodes = self.memory.search_episodes(query, n_results=3)
            if episodes:
                return "Here's what I found:\n\n" + "\n---\n".join(episodes)
            return f"I don't remember any conversations about '{query}'."

        # Remember explicit facts
        if any(w in lower for w in ['remember that', 'my name is', 'i prefer', 'i like', 'i hate',
                                      'i work at', 'i live in', 'call me']):
            # LLM extraction handles this in add_exchange, but we confirm here
            return f"Got it, I'll remember that."

        # Default: search memory
        episodes = self.memory.search_episodes(user_input, n_results=3)
        if episodes:
            return "Here's what I found in my memory:\n\n" + "\n---\n".join(episodes)
        return "I don't have any relevant memories about that yet."