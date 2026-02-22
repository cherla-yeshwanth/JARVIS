"""
JARVIS v1.0 — Executor
Task dispatcher: routes classified intents to the correct handler.
Supports multi-step task execution.
"""

from brain import Brain, Intent
from memory import Memory
from handlers.chat_handler import ChatHandler
from handlers.search_handler import SearchHandler
from handlers.system_handler import SystemHandler
from handlers.code_handler import CodeHandler
from handlers.memory_handler import MemoryHandler
from handlers.notes_handler import NotesHandler

from handlers.utility_handler import UtilityHandler
from handlers.vision_handler import VisionHandler
from handlers.autonomy import AutonomyHandler
from handlers.phone_handler import PhoneHandler

class Executor:
    """Routes tasks to specialized handlers based on intent classification."""

    def __init__(self, brain: Brain, memory: Memory):
        self.brain = brain
        self.memory = memory

        # Initialize all handlers
        self.handlers = {
            Intent.CHAT:    ChatHandler(brain),
            Intent.SEARCH:  SearchHandler(brain),
            Intent.SYSTEM:  SystemHandler(brain),
            Intent.CODE:    CodeHandler(brain),
            Intent.MEMORY:  MemoryHandler(memory),
            Intent.NOTES:   NotesHandler(memory),
            Intent.UTILITY: UtilityHandler(),
            Intent.VISION:  VisionHandler(brain),
            Intent.AUTONOMY: AutonomyHandler(brain, memory),
            Intent.PHONE:   PhoneHandler(brain),
        }
        print(f"[EXECUTOR] Initialized {len(self.handlers)} handlers.")

    def execute(self, routing_result: dict) -> str:
        """
        Execute a routed task. Handles both single and multi-step requests.
        """
        intent = routing_result['intent']
        user_input = routing_result['user_input']
        context = routing_result.get('memory_context', '')
        multi_step = routing_result.get('multi_step')

        # Multi-step execution
        if multi_step and len(multi_step) > 1:
            return self._execute_multi_step(multi_step, context)

        # Single-step execution
        return self._execute_single(intent, user_input, context)

    def _execute_single(self, intent: Intent, user_input: str, context: str) -> str:
        """Execute a single task."""
        handler = self.handlers.get(intent, self.handlers[Intent.CHAT])
        print(f"[EXECUTOR] Routing to: {intent.value}")

        try:
            return handler.handle(user_input, context)
        except Exception as e:
            print(f"[EXECUTOR] Handler error: {e}")
            # Fall back to chat handler
            return self.handlers[Intent.CHAT].handle(
                f"I encountered an error trying to {intent.value}: {e}. "
                f"The original request was: {user_input}",
                context
            )

    def _execute_multi_step(self, steps: list[str], context: str) -> str:
        """Execute multiple steps sequentially."""
        results = []
        print(f"[EXECUTOR] Executing {len(steps)} steps...")

        for i, step in enumerate(steps, 1):
            print(f"[EXECUTOR] Step {i}/{len(steps)}: {step}")

            # Classify each step independently
            intent = self.brain.classify_intent(step)
            try:
                result = self._execute_single(intent, step, context)
                results.append(f"Step {i}: {result}")
                # Add result to context for next step
                context += f"\nPrevious step result: {result}"
            except Exception as e:
                results.append(f"Step {i} failed: {e}")

        return "\n\n".join(results)