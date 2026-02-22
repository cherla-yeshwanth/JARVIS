"""
JARVIS v1.0 — Utility Handler
Calculator, unit converter, password generator, text manipulation.
All computed locally — no LLM needed for these.
"""

import math
import re
import string
import secrets

class UtilityHandler:
    """Local utility tools — fast, no LLM required."""

    def handle(self, user_input: str, context: str = '') -> str:
        """Route utility commands."""
        # Input validation
        if not isinstance(user_input, str) or not user_input.strip():
            return "Sorry, I didn't receive any input."
        try:
            lower = user_input.lower().strip()

            # Password generation
            if 'password' in lower or 'passphrase' in lower:
                return self._generate_password(lower)

            # Unit conversion
            if 'convert' in lower:
                return self._convert_units(lower)

            # Text manipulation
            if any(w in lower for w in ['uppercase', 'lowercase', 'word count',
                                         'character count', 'char count', 'reverse']):
                return self._text_manipulation(user_input)

            # Calculator (default for utility)
            return self._calculate(user_input)
        except Exception as e:
            return f"Sorry, an error occurred: {e}"

    # ─── Calculator ──────────────────────────────────────

    def _calculate(self, expression: str) -> str:
        """Evaluate a math expression safely."""
        # Clean the input
        expr = expression.lower()
        for word in ['calculate', 'what is', 'how much is', 'compute', 'math', 'eval']:
            expr = expr.replace(word, '')
        expr = expr.strip().rstrip('?')

        # Replace word operators
        expr = expr.replace('plus', '+').replace('minus', '-')
        expr = expr.replace('times', '*').replace('multiplied by', '*')
        expr = expr.replace('divided by', '/').replace('over', '/')
        expr = expr.replace('to the power of', '**').replace('power', '**')
        expr = expr.replace('mod', '%').replace('modulo', '%')
        expr = expr.replace('percent of', '* 0.01 *')
        expr = expr.replace('%', '* 0.01')
        expr = expr.replace('x', '*')
        expr = expr.replace('^', '**')

        # Only allow safe characters
        allowed = set('0123456789+-*/.() ')
        clean = ''.join(c for c in expr if c in allowed)
        clean = clean.strip()

        if not clean:
            return "I couldn't understand that math expression. Try something like 'calculate 15 + 27'."

        try:
            # Safe eval with only math builtins
            safe_dict = {
                'abs': abs, 'round': round, 'min': min, 'max': max,
                'sqrt': math.sqrt, 'pi': math.pi, 'e': math.e,
                'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                'log': math.log, 'log10': math.log10,
                'ceil': math.ceil, 'floor': math.floor,
                '__builtins__': {},
            }
            result = eval(clean, safe_dict)

            # Format nicely
            if isinstance(result, float):
                if result == int(result):
                    result = int(result)
                else:
                    result = round(result, 6)

            return f"🧮 {clean} = {result}"
        except ZeroDivisionError:
            return "Cannot divide by zero."
        except Exception as e:
            return f"Math error: {e}. Try a simpler expression."

    # ─── Unit Converter ──────────────────────────────────

    CONVERSIONS = {
        # Length
        ('km', 'miles'): 0.621371,
        ('miles', 'km'): 1.60934,
        ('m', 'feet'): 3.28084,
        ('feet', 'm'): 0.3048,
        ('cm', 'inches'): 0.393701,
        ('inches', 'cm'): 2.54,
        ('m', 'yards'): 1.09361,
        ('yards', 'm'): 0.9144,
        # Weight
        ('kg', 'lbs'): 2.20462,
        ('lbs', 'kg'): 0.453592,
        ('kg', 'pounds'): 2.20462,
        ('pounds', 'kg'): 0.453592,
        ('g', 'oz'): 0.035274,
        ('oz', 'g'): 28.3495,
        # Temperature (handled separately)
        # Volume
        ('liters', 'gallons'): 0.264172,
        ('gallons', 'liters'): 3.78541,
        ('ml', 'cups'): 0.00422675,
        ('cups', 'ml'): 236.588,
        # Speed
        ('kmh', 'mph'): 0.621371,
        ('mph', 'kmh'): 1.60934,
        # Data
        ('gb', 'mb'): 1024,
        ('mb', 'gb'): 1 / 1024,
        ('tb', 'gb'): 1024,
        ('gb', 'tb'): 1 / 1024,
    }

    def _convert_units(self, text: str) -> str:
        """Convert between units."""
        # Try to parse: "convert X from_unit to to_unit"
        pattern = r'(\d+\.?\d*)\s*([a-zA-Z°]+)\s+(?:to|in)\s+([a-zA-Z°]+)'
        match = re.search(pattern, text)
        if not match:
            return "Format: 'convert 100 km to miles'. I support length, weight, temperature, volume, speed, and data units."

        value = float(match.group(1))
        from_unit_raw = match.group(2).lower()
        to_unit_raw = match.group(3).lower()

        # Only strip 's' for non-temperature units
        temp_units = ['celsius', 'fahrenheit', 'centigrade', 'kelvin']
        if from_unit_raw not in temp_units:
            from_unit = from_unit_raw.rstrip('s')
        else:
            from_unit = from_unit_raw
        if to_unit_raw not in temp_units:
            to_unit = to_unit_raw.rstrip('s')
        else:
            to_unit = to_unit_raw

        # Normalize common synonyms
        synonyms = {
            "kilometer": "km", "kilometre": "km", "kilometers": "km", "kilometres": "km",
            "mile": "miles", "miles": "miles",
            "celsius": "c", "centigrade": "c", "fahrenheit": "f", "kelvin": "k",
            "kg": "kg", "kilogram": "kg", "kilograms": "kg",
            "lb": "lbs", "lbs": "lbs", "pound": "lbs", "pounds": "lbs"
        }
        from_unit = synonyms.get(from_unit, from_unit)
        to_unit = synonyms.get(to_unit, to_unit)

        # Accept more variations for temperature units
        c_variants = ('c', '°c', 'celsius', 'centigrade')
        f_variants = ('f', '°f', 'fahrenheit')
        k_variants = ('k', 'kelvin')

        # Temperature special case
        if from_unit in c_variants and to_unit in f_variants:
            result = (value * 9 / 5) + 32
            return f"🌡️ {value}°C = {result:.1f}°F"
        if from_unit in f_variants and to_unit in c_variants:
            result = (value - 32) * 5 / 9
            return f"🌡️ {value}°F = {result:.1f}°C"
        if from_unit in c_variants and to_unit in k_variants:
            result = value + 273.15
            return f"🌡️ {value}°C = {result:.1f}K"

        # Lookup conversion factor
        factor = self.CONVERSIONS.get((from_unit, to_unit))
        if factor is None:
            # Try with 's' suffix
            factor = self.CONVERSIONS.get((from_unit + 's', to_unit + 's'))
        if factor is None:
            factor = self.CONVERSIONS.get((from_unit, to_unit + 's'))
        if factor is None:
            factor = self.CONVERSIONS.get((from_unit + 's', to_unit))

        if factor is None:
            return f"I don't know how to convert {from_unit} to {to_unit}. Supported: km↔miles, kg↔lbs, °C↔°F, liters↔gallons, and more."

        result = value * factor
        if result == int(result):
            result = int(result)
        else:
            result = round(result, 4)

        return f"📐 {value} {from_unit} = {result} {to_unit}"

    # ─── Password Generator ─────────────────────────────

    def _generate_password(self, text: str) -> str:
        """Generate a secure random password."""
        # Try to extract length
        length_match = re.search(r'(\d+)', text)
        length = int(length_match.group(1)) if length_match else 16
        length = max(8, min(128, length))  # Clamp between 8-128

        # Generate using secrets (cryptographically secure)
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for _ in range(length))

        # Ensure at least one of each type
        if length >= 12:
            chars = list(password)
            chars[0] = secrets.choice(string.ascii_uppercase)
            chars[1] = secrets.choice(string.ascii_lowercase)
            chars[2] = secrets.choice(string.digits)
            chars[3] = secrets.choice(string.punctuation)
            secrets.SystemRandom().shuffle(chars)
            password = ''.join(chars)

        return f"🔐 Generated password ({length} chars):\n{password}"

    # ─── Text Manipulation ───────────────────────────────

    def _text_manipulation(self, text: str) -> str:
        """Text tools: uppercase, lowercase, word count, etc."""
        lower = text.lower()

        if 'uppercase' in lower:
            content = text.split('uppercase', 1)[-1].strip()
            if not content:
                return "Provide text after 'uppercase'. Example: 'uppercase hello world'"
            return f"📝 {content.upper()}"

        if 'lowercase' in lower:
            content = text.split('lowercase', 1)[-1].strip()
            if not content:
                return "Provide text after 'lowercase'. Example: 'lowercase HELLO WORLD'"
            return f"📝 {content.lower()}"

        if 'word count' in lower:
            content = lower.replace('word count', '').replace('of', '').strip()
            if not content:
                return "Provide text to count words."
            count = len(content.split())
            return f"📝 Word count: {count}"

        if 'character count' in lower or 'char count' in lower:
            content = lower.replace('character count', '').replace('char count', '').replace('of', '').strip()
            if not content:
                return "Provide text to count characters."
            return f"📝 Character count: {len(content)} (without spaces: {len(content.replace(' ', ''))})"

        if 'reverse' in lower:
            content = text.split('reverse', 1)[-1].strip()
            if not content:
                return "Provide text to reverse."
            return f"📝 Reversed: {content[::-1]}"

        return "Available text tools: uppercase, lowercase, word count, character count, reverse"