import re

# Speech that directly addresses JARVIS → always a command
DIRECT_PATTERNS = [
    r'^(hey|hi|ok|okay|yo)?\s*(jarvis|buddy)[,!]?\s+\w+',
    r'.+\s+(jarvis|buddy)[.!?]?$',
    r'^(jarvis|buddy),?\s+',
]

# Obvious non-commands → ignore immediately
AMBIENT_PATTERNS = [
    r'^(haha|lol|wow|omg|oh|ah|hmm|ugh)+$',
    r'^(yes|no|yeah|nah|ok|okay|sure|fine|yep|nope)$',
    r'^\d{1,3}$',
]

class IntentFilter:
    def __init__(self, brain):
        self.brain = brain

    def is_command(self, text: str) -> bool:
        lower = text.lower().strip()
        if len(lower) < 3:
            return False

        # Tier 1: Explicit address → definitely a command
        for pat in DIRECT_PATTERNS:
            if re.search(pat, lower):
                return True

        # Tier 2: Obvious ambient → skip without LLM call
        for pat in AMBIENT_PATTERNS:
            if re.search(pat, lower):
                return False

        # Tier 3: Ask local LLM (qwen2.5:3b — fast, free)
        prompt = (
            'Is the following text a command to an AI assistant, '
            'or just someone speaking/thinking aloud?\n'
            f'Text: "{text}"\n'
            'Reply ONLY with: COMMAND or AMBIENT'
        )
        result = self.brain._call_ollama(self.brain.fast_model, prompt)
        return 'COMMAND' in result.upper()
