import os
import logging
from groq import AsyncGroq

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroqService:
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found. LLM features will be disabled/mocked.")
            self.client = None
        else:
            self.client = AsyncGroq(api_key=self.api_key)

    async def classify_chat_intent(self, user_message: str) -> str:
        if not self.client:
            return "MOCK_INTENT"

        system_prompt = """
        You are the 'Brain' of an autonomous financial advisor agent.
        Your job is to CLASSIFY the user's intent into one of the following categories.
        
        CATEGORIES:
        1. SUMMARIZE_CASE: User wants an update on a specific client or case.
        2. LIST_EXCEPTIONS: User wants to see blocked items.
        3. PAUSE_CHASE: User wants to stop chasing a specific item.
        4. FORCE_ESCALATE: User wants to force an escalation.
        5. DRAFT_EMAIL: User wants to write an email.
        6. UNKNOWN: If the request is unclear.

        Output ONLY the category name.
        """

        try:
            completion = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.0
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq API Error: {e}")
            return "ERROR"
            
    async def generate_completion(self, prompt: str) -> str:
        """
        Generic completion method for generating content (e.g. emails).
        """
        if not self.client:
            return "[Mock LLM Output]: This is a simulated email draft."
            
        try:
            completion = await self.client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7 # Slight creativity for emails
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq API Error: {e}")
            return "Error generating content."
