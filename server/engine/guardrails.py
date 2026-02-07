from typing import Tuple

class Guardrails:
    def __init__(self):
        # Allow-list of topics or regex could be here
        self.banned_keywords = ["ignore previous instructions", "system prompt", "password", "secret key"]

    def validate_input(self, message: str) -> Tuple[bool, str]:
        """
        Check if input is safe.
        Returns (is_safe, reason).
        """
        msg_lower = message.lower()
        for kw in self.banned_keywords:
            if kw in msg_lower:
                return False, f"Blocked keyword detection: {kw}"
        
        if len(message) > 1000:
            return False, "Message too long."
            
        return True, "Safe"

    def validate_output(self, output: str) -> str:
        """
        Sanitize output if needed.
        """
        # Simple PII redaction mock
        # In production, use Presidio or similar
        return output

guardrails = Guardrails()
