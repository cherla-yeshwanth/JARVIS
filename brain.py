"""
JARVIS v1.0 — AGI Brain Module
Intent classification, chain-of-thought reasoning, self-reflection,
smart model selection, and multi-step task planning.
"""

import requests
import json
import time
from enum import Enum
from datetime import datetime
from config import (
    OLLAMA_HOST,
    FAST_MODEL,
    SMART_MODEL,
    OLLAMA_TIMEOUT,
    COMPLEXITY_WORD_THRESHOLD,
    MAX_REFLECTION_RETRIES,
    SYSTEM_PROMPT,
    ASSISTANT_NAME,
)

class Intent(Enum):
    CODE     = 'code'
    SEARCH   = 'search'
    SYSTEM   = 'system'
    MEMORY   = 'memory'
    NOTES    = 'notes'
    UTILITY  = 'utility'
    CHAT     = 'chat'
    VISION   = 'vision'
    AUTONOMY = 'autonomy'
    PHONE    = 'phone'

    # ─── Quick-match patterns (skip LLM for obvious intents) ──
INTENT_PATTERNS = {
    Intent.AUTONOMY: [
        'remind me', 'reminder', 'proactive', 'suggest', 'autonomy', 'self-initiate', 'self initiated', 'self-initiated', 'daily brief', 'morning brief', 'agenda', 'routine', 'habit', 'motivate', 'motivation', 'check in', 'check-in', 'periodic', 'interval', 'habit tracker', 'goal', 'goals', 'self improvement', 'self-improvement', 'self help', 'self-help',
    ],
    Intent.PHONE: [
        'call', 'phone', 'dial', 'sms', 'text', 'send message', 'whatsapp', 'notification', 'missed call', 'incoming call', 'outgoing call', 'contact', 'contacts', 'mobile', 'cell', 'ring', 'voicemail', 'caller', 'hang up', 'answer', 'mute call', 'unmute call',
    ],
    Intent.UTILITY: [
        'calculate', 'convert', 'password', 'generate password',
        'what is', 'how much is', 'math', 'uppercase', 'lowercase',
        'word count', 'character count', 'random',
    ],
    Intent.NOTES: [
        'take a note', 'save a note', 'note that', 'my notes',
        'show notes', 'search notes', 'delete note',
    ],
    Intent.MEMORY: [
        'remember that', 'do you remember', 'what did i say',
        'what do you know about me', 'forget', 'my name is',
        'i prefer', 'i like', 'i hate', 'i work at', 'i live in',
        'privacy mode', 'go private', 'export memory', 'wipe memory',
    ],
    Intent.SYSTEM: [
        'open ', 'close ', 'launch ', 'start ', 'kill ',
        'volume', 'mute', 'unmute', 'screenshot', 'battery',
        'cpu usage', 'disk space', 'system info', 'ip address',
        'wifi', 'process', 'coding setup',
    ],
    Intent.SEARCH: [
        'search for', 'look up', 'google', 'find information',
        'what is the latest', 'news about', 'search the web',
        'who is', 'when did', 'where is',
    ],
    Intent.CODE: [
        'write code', 'write a script', 'debug', 'fix this code',
        'explain this code', 'python script', 'javascript',
        'function that', 'program', 'algorithm',
    ],
    Intent.VISION: [
        'see on screen', 'what do you see', 'read screen', 'describe screen',
        'find button', 'click button', 'where is', 'screenshot', 'vision',
        'scroll', 'type on screen', 'ui automation', 'look at', 'show me',
        'highlight', 'select', 'detect', 'screen', 'window', 'image',
    ],
}

class Brain:
    """
    AGI-style brain: classifies intent, selects model complexity,
    reasons step-by-step, and self-reflects on answer quality.
    """

    def __init__(self):
        self.ollama = OLLAMA_HOST
        self.fast_model = FAST_MODEL
        self.smart_model = SMART_MODEL
        self._check_ollama()

    def _check_ollama(self):
        """Verify Ollama is running."""
        try:
            resp = requests.get(f'{self.ollama}/api/tags', timeout=5)
            if resp.status_code == 200:
                models = [m['name'] for m in resp.json().get('models', [])]
                print(f"[BRAIN] Ollama connected. Models: {', '.join(models[:5])}")
            else:
                print("[BRAIN] ⚠️ Ollama responded but with unexpected status.")
        except requests.ConnectionError:
            print("[BRAIN] ⚠️ Ollama not running! Start it with: ollama serve")
        except Exception as e:
            print(f"[BRAIN] ⚠️ Ollama check failed: {e}")

    def _call_ollama(self, model: str, prompt: str, system: str = '') -> str:
        """Make a request to Ollama's generate API."""
        try:
            payload = {
                'model': model,
                'prompt': prompt,
                'stream': False,
            }
            if system:
                payload['system'] = system

            resp = requests.post(
                f'{self.ollama}/api/generate',
                json=payload,
                timeout=OLLAMA_TIMEOUT,
            )
            if resp.status_code == 200:
                return resp.json().get('response', '').strip()
            else:
                return f"Error: Ollama returned status {resp.status_code}"
        except requests.Timeout:
            return "I'm taking too long to respond. Let me try with a simpler approach."
        except requests.ConnectionError:
            return "I can't reach my language model. Make sure Ollama is running."
        except Exception as e:
            return f"Error communicating with Ollama: {e}"

    def _pattern_match_intent(self, user_input: str) -> Intent | None:
        """Try to match intent using keyword patterns (no LLM call needed)."""
        lower = user_input.lower().strip()
        for intent, patterns in INTENT_PATTERNS.items():
            for pattern in patterns:
                if pattern in lower:
                    return intent
        return None

    def classify_intent(self, user_input: str) -> Intent:
        """
        Classify user intent. Uses pattern matching first (instant),
        falls back to LLM classification if no pattern matches.
        """
        # Step 1: Fast pattern matching
        matched = self._pattern_match_intent(user_input)
        if matched:
            print(f"[BRAIN] Intent (pattern): {matched.value}")
            return matched

        # Step 2: LLM classification (only when patterns don't match)
        prompt = f"""Classify this user request into exactly ONE category.

Categories:
- code: writing, debugging, explaining code or programming
- search: finding information online, current events, web lookup
- system: open/close apps, system control, file operations, volume, screenshots
- memory: recall past conversations, remember facts, user preferences
- notes: taking notes, saving notes, searching notes
- utility: math calculations, unit conversions, password generation, text tools
- chat: general conversation, questions, opinions, advice

User request: "{user_input}"

Reply with ONLY the category word. Nothing else."""

        result = self._call_ollama(self.fast_model, prompt).lower().strip()

        for intent in Intent:
            if intent.value in result:
                print(f"[BRAIN] Intent (LLM): {intent.value}")
                return intent

        print(f"[BRAIN] Intent (fallback): chat")
        return Intent.CHAT

    def assess_complexity(self, user_input: str) -> str:
        """
        Decide which model to use based on input complexity.
        Returns model name.
        """
        word_count = len(user_input.split())

        # Simple heuristics first
        if word_count <= COMPLEXITY_WORD_THRESHOLD:
            return self.fast_model

        # Check for complexity indicators
        complex_indicators = [
            'explain in detail', 'step by step', 'compare',
            'analyze', 'write a long', 'essay', 'comprehensive',
            'pros and cons', 'in depth', 'elaborate', 'thorough',
            'multi-step', 'complex', 'advanced',
        ]
        lower = user_input.lower()
        if any(indicator in lower for indicator in complex_indicators):
            return self.smart_model

        return self.fast_model

    def think_step_by_step(self, user_input: str, context: str = '') -> str:
        """
        Chain-of-thought reasoning: asks the model to think
        step by step before answering.
        """
        model = self.assess_complexity(user_input)
        print(f"[BRAIN] Using model: {model}")

        # Build the time-aware system prompt
        hour = datetime.now().hour
        time_context = ""
        if 5 <= hour < 12:
            time_context = "It's morning. Be concise and focused."
        elif 12 <= hour < 17:
            time_context = "It's afternoon. Be balanced and helpful."
        elif 17 <= hour < 21:
            time_context = "It's evening. Be relaxed and conversational."
        else:
            time_context = "It's late night. Be brief unless asked for detail."

        system = f"{SYSTEM_PROMPT}\n{time_context}"
        if context:
            system += f"\n\nRelevant context from memory:\n{context}"

        prompt = f"""User: {user_input}

Think through this step by step, then provide a clear, helpful response.
If the question is simple, just answer directly — don't overthink it.

{ASSISTANT_NAME}:"""

        response = self._call_ollama(model, prompt, system)
        return response

    def self_reflect(self, user_input: str, response: str, context: str = '') -> str:
        """
        Self-reflection: evaluate the response quality and retry if needed.
        Only triggers for complex queries to save time on simple ones.
        """
        # Skip reflection for simple queries
        if len(user_input.split()) <= COMPLEXITY_WORD_THRESHOLD:
            return response

        if MAX_REFLECTION_RETRIES <= 0:
            return response

        # Ask the fast model to evaluate
        eval_prompt = f"""Rate this response quality from 1-10.

User question: "{user_input}"
Response: "{response[:500]}"

Consider:
- Does it actually answer the question?
- Is it accurate and helpful?
- Is it concise enough?

Reply with ONLY a number 1-10."""

        score_str = self._call_ollama(self.fast_model, eval_prompt)
        try:
            score = int(''.join(c for c in score_str if c.isdigit())[:2])
        except (ValueError, IndexError):
            score = 7  # Assume decent if we can't parse

        print(f"[BRAIN] Self-reflection score: {score}/10")

        if score >= 6:
            return response

        # Retry with the smart model
        print("[BRAIN] Score too low, retrying with smart model...")
        system = SYSTEM_PROMPT
        if context:
            system += f"\n\nContext:\n{context}"

        retry_prompt = f"""The previous answer to this question was not good enough.
Please provide a better, more accurate answer.

User: {user_input}

{ASSISTANT_NAME}:"""

        return self._call_ollama(self.smart_model, retry_prompt, system)

    def plan_multi_step(self, user_input: str) -> list[str] | None:
        """
        Detect if a request requires multiple steps.
        Returns a list of steps, or None if it's a simple single-step request.
        """
        multi_step_indicators = [
            ' then ', ' and then ', ' after that ',
            ' also ', ' first ', ' next ',
            ' finally ', ' step 1', ' step 2',
        ]
        lower = user_input.lower()
        if not any(ind in lower for ind in multi_step_indicators):
            return None

        prompt = f"""Break this request into individual steps (max 5 steps).
If it's actually just one task, reply with "SINGLE".

Request: "{user_input}"

Reply as a JSON array of strings, like: ["step 1", "step 2"]
Or reply: SINGLE"""

        result = self._call_ollama(self.fast_model, prompt)
        if 'SINGLE' in result.upper():
            return None

        try:
            # Try to extract JSON array
            start = result.find('[')
            end = result.rfind(']') + 1
            if start >= 0 and end > start:
                steps = json.loads(result[start:end])
                if isinstance(steps, list) and len(steps) > 1:
                    print(f"[BRAIN] Multi-step plan: {len(steps)} steps")
                    return steps
        except (json.JSONDecodeError, ValueError):
            pass

        return None

    def generate_response(self, user_input: str, context: str = '') -> str:
        """
        Full AGI response pipeline:
        1. Think step-by-step
        2. Self-reflect and retry if needed
        """
        response = self.think_step_by_step(user_input, context)
        response = self.self_reflect(user_input, response, context)
        return response

    def route(self, user_input: str, memory_context: str = '') -> dict:
        """
        Main routing function. Classifies intent and returns routing info.
        """
        intent = self.classify_intent(user_input)
        model = self.assess_complexity(user_input)
        steps = self.plan_multi_step(user_input)

        return {
            'intent': intent,
            'user_input': user_input,
            'memory_context': memory_context,
            'model': model,
            'multi_step': steps,
        }