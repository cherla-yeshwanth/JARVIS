"""
JARVIS v1.0 — Chat Handler
Handles general conversation, Q&A, opinions, and advice.
Uses the AGI brain's chain-of-thought + self-reflection pipeline.
"""

from brain import Brain

class ChatHandler:
    """General conversation handler."""

    def __init__(self, brain: Brain):
        self.brain = brain

    def handle(self, user_input: str, context: str = '') -> str:
        """Generate a conversational response with full AGI pipeline."""
        return self.brain.generate_response(user_input, context)