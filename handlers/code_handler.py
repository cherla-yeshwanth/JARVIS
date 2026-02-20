"""
JARVIS v1.0 — Code Handler
Code generation, explanation, and debugging using Ollama models.
"""

import requests
from config import OLLAMA_HOST, SMART_MODEL, OLLAMA_TIMEOUT, SYSTEM_PROMPT

class CodeHandler:
    """Code generation and assistance handler."""

    def __init__(self, brain):
        self.brain = brain

    def handle(self, user_input: str, context: str = '') -> str:
        """Handle code-related requests."""
        system = f"""{SYSTEM_PROMPT}
You are an expert software developer. When writing code:
- Include clear comments
- Use best practices
- Handle edge cases
- Keep it concise but complete
If explaining code, be clear and educational."""

        if context:
            system += f"\n\nRelevant context:\n{context}"

        prompt = f"User: {user_input}\n\nAssistant:"

        try:
            resp = requests.post(
                f'{OLLAMA_HOST}/api/generate',
                json={
                    'model': SMART_MODEL,  # Always use smart model for code
                    'prompt': prompt,
                    'system': system,
                    'stream': False,
                },
                timeout=OLLAMA_TIMEOUT,
            )
            if resp.status_code == 200:
                return resp.json().get('response', '').strip()
            else:
                return f"Error generating code: status {resp.status_code}"
        except requests.Timeout:
            return "Code generation timed out. Try a simpler request."
        except requests.ConnectionError:
            return "Can't reach Ollama. Make sure it's running."
        except Exception as e:
            return f"Code generation error: {e}"