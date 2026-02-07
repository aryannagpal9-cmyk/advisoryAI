import os
from pydantic import BaseModel
from typing import Optional
import requests
from services.llm_service import GroqService

class EmailRequest(BaseModel):
    to_email: str
    subject: str
    content: str
    request_id: Optional[str] = None # For embedding in metadata

class EmailService:
    def __init__(self):
        self.postmark_token = os.environ.get("POSTMARK_SERVER_TOKEN")
        self.from_email = os.environ.get("POSTMARK_FROM_EMAIL", "advisory-ai@example.com")
        self.message_stream = os.environ.get("POSTMARK_MESSAGE_STREAM")  # optional
        self.llm = GroqService()
        if not self.postmark_token:
            print("WARNING: No POSTMARK_SERVER_TOKEN found. Running in MOCK mode.")

    def send_email(self, to_email: str, subject: str, content: str, use_llm: bool = False, context: str = None):
        """
        Sends an email. If use_llm is True, generates content based on context first.
        """
        final_content = content
        if use_llm and context:
            # Delegate prompting to the LLM Service for consistency
            generated = self.llm.draft_email(to_email, context, content)
            
            # Fallback if LLM fails (checks if result is just the base content or error)
            if generated and generated != content:
                final_content = generated
            
        if not self.postmark_token:
            print(f"[MOCK EMAIL] To: {to_email} | Subject: {subject} | Body: {final_content}")
            return True

        payload = {
            "From": self.from_email,
            "To": to_email,
            "Subject": subject,
            "TextBody": final_content,
            "HtmlBody": f"<p>{final_content}</p>",
        }
        if self.message_stream:
            payload["MessageStream"] = self.message_stream

        try:
            resp = requests.post(
                "https://api.postmarkapp.com/email",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "X-Postmark-Server-Token": self.postmark_token,
                },
                json=payload,
                timeout=15,
            )
            return 200 <= resp.status_code < 300
        except Exception as e:
            print(f"Postmark Error: {e}")
            return False

email_service = EmailService()
