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
        # Input validation
        if not isinstance(user_input, str) or not user_input.strip():
            return "Sorry, I didn't receive any input."
        try:
            return self.brain.generate_response(user_input, context)
        except Exception as e:
            return f"Sorry, an error occurred: {e}"
