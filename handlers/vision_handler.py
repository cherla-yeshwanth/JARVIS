import mss
import pyautogui
import base64, json, io, requests
from PIL import Image
from config import OLLAMA_HOST

VISION_MODEL = 'llava:7b'  # Use llava:7b for low RAM

class VisionHandler:
    def __init__(self, brain):
        self.brain = brain
        pyautogui.FAILSAFE = True   # Move mouse to corner = emergency stop!
        pyautogui.PAUSE = 0.4       # Safety pause between actions

    def _screenshot_b64(self) -> str:
        with mss.mss() as sct:
            shot = sct.grab(sct.monitors[0])
            img = Image.frombytes('RGB', shot.size, shot.bgra, 'raw', 'BGRX')
            img.thumbnail((1280, 720))  # Resize for faster processing
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            return base64.b64encode(buf.getvalue()).decode()

    def _ask_vision(self, b64img: str, question: str) -> dict:
        """Send screenshot to local LLaVA model via Ollama API"""
        prompt = (
            f'You are a UI automation assistant.\n'
            f'Task: {question}\n'
            f'Look at the screenshot carefully.\n'
            f'Reply ONLY as JSON (no other text):\n'
            f'{{"found": true/false, "description": "what you see", '
            f'"action": "click/scroll/type/read/none", '
            f'"x": pixel_x_or_null, "y": pixel_y_or_null, '
            f'"text_to_type": "string or null", '
            f'"scroll_amount": integer_or_null}}'
        )
        try:
            resp = requests.post(
                f'{OLLAMA_HOST}/api/generate',
                json={
                    'model': VISION_MODEL,
                    'prompt': prompt,
                    'images': [b64img],
                    'stream': False,
                },
                timeout=60
            )
            raw = resp.json().get('response', '{}').strip().strip('`').replace('json', '').strip()
            return json.loads(raw)
        except requests.Timeout:
            return {'found': False, 'description': 'Vision request timed out.', 'action': 'none'}
        except Exception as e:
            return {'found': False, 'description': f'Vision error: {e}', 'action': 'none'}

    def _act(self, plan: dict) -> str:
        if not plan.get('found', False):
            return f"Couldn't find it: {plan.get('description', 'unknown')}"
        action = plan.get('action', 'none')
        x, y = plan.get('x'), plan.get('y')
        if action == 'click' and x and y:
            pyautogui.moveTo(x, y, duration=0.4)
            pyautogui.click()
            return f'Clicked at ({x}, {y})'
        elif action == 'scroll':
            amt = plan.get('scroll_amount', -3)
            pyautogui.scroll(amt)
            return f'Scrolled {"down" if amt < 0 else "up"}'
        elif action == 'type':
            pyautogui.typewrite(plan.get('text_to_type', ''), interval=0.05)
            return 'Typed text'
        elif action == 'read':
            return f"I can see: {plan.get('description', 'nothing')}"
        return plan.get('description', 'Done')

    def handle(self, user_input: str, context: str = '') -> str:
        # Input validation
        if not isinstance(user_input, str) or not user_input.strip():
            return "Sorry, I didn't receive any input."
        try:
            lower = user_input.lower()
            b64 = self._screenshot_b64()
            plan = self._ask_vision(b64, user_input)
            if any(w in lower for w in ['read', 'see', 'what', 'show', 'describe']):
                return plan.get('description', 'I cannot determine what is on screen.')
            return self._act(plan)
        except Exception as e:
            return f"Sorry, an error occurred: {e}"
