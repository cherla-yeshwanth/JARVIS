"""
JARVIS v1.0 — Proactive Engine
Background pattern detection, morning briefs, and context-aware suggestions.
Runs as a daemon thread — does not block the main service.
"""

import threading
import time
import sqlite3
from datetime import datetime
from config import PROACTIVE_CHECK_INTERVAL, MORNING_HOUR, DB_PATH

class ProactiveEngine:
    """Background engine that detects patterns and provides proactive insights."""

    def __init__(self, memory, tts):
        self.memory = memory
        self.tts = tts
        self.check_interval = PROACTIVE_CHECK_INTERVAL
        self.running = False
        self._thread = None
        self._morning_brief_given = False
        self._last_check_date = None

    def get_daily_patterns(self) -> list:
        """What does the user usually do at this time of day?"""
        hour = datetime.now().hour
        return self.memory.get_patterns(hour)

    def generate_morning_brief(self) -> str:
        """Create a personalized morning briefing."""
        patterns = self.get_daily_patterns()
        facts = self.memory.get_facts()
        analytics = self.memory.get_conversation_analytics()

        parts = [f"Good morning!"]

        # Total interaction count
        total = analytics.get('total_conversations', 0)
        if total > 0:
            parts.append(f"We've had {total} conversations so far.")

        # Top patterns
        if patterns:
            top_task = patterns[0][0]
            parts.append(f"You usually start with {top_task} tasks around this time.")

        # User facts for personalization
        name_fact = None
        for cat, key, value in facts:
            if 'name' in key.lower():
                name_fact = value
                break
        if name_fact:
            parts[0] = f"Good morning, {name_fact}!"

        return " ".join(parts) if len(parts) > 1 else ""

    def _check_cycle(self):
        """Single check cycle — called periodically."""
        now = datetime.now()
        today = now.date()

        # Morning brief (once per day)
        if (now.hour == MORNING_HOUR and
            not self._morning_brief_given and
            self._last_check_date != today):
            brief = self.generate_morning_brief()
            if brief:
                print(f"[PROACTIVE] Morning brief: {brief}")
                self.tts.speak(brief)
                self._morning_brief_given = True
                self._last_check_date = today

        # Reset morning brief flag for next day
        if self._last_check_date != today:
            self._morning_brief_given = False
            self._last_check_date = today

    def _loop(self):
        """Background loop."""
        while self.running:
            try:
                self._check_cycle()
            except Exception as e:
                print(f"[PROACTIVE] Error: {e}")
            time.sleep(self.check_interval)

    def start(self):
        """Start the proactive engine in a background thread."""
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print("[PROACTIVE] Engine started.")

    def stop(self):
        """Stop the proactive engine."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("[PROACTIVE] Engine stopped.")