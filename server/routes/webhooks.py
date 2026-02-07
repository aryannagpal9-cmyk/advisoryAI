from fastapi import APIRouter, Request, Form
from services.websocket_manager import manager
from services.llm_service import GroqService
from db.supabase import get_supabase
import logging

router = APIRouter(prefix="/webhooks")
logger = logging.getLogger(__name__)
groq_service = GroqService()
supabase = get_supabase()

async def _broadcast_inbound_email(*, sender: str | None, subject: str | None, text_body: str | None) -> None:
    intent = groq_service.classify_chat_intent(f"Subject: {subject}\nBody: {text_body}")
    event_payload = {
        "type": "NEW_EMAIL",
        "data": {
            "from": sender,
            "subject": subject,
            "summary": ((text_body or "")[:100] + "...") if text_body else "",
            "intent": intent,
            "timestamp": "Just now",
        },
    }
    await manager.broadcast(event_payload)


@router.post("/postmark/inbound")
async def handle_postmark_inbound(request: Request):
    """
    Handle incoming email from Postmark inbound webhook.
    Postmark sends JSON.
    """
    payload = await request.json()

    sender = payload.get("From") or payload.get("FromFull", {}).get("Email")
    subject = payload.get("Subject")
    text_body = payload.get("TextBody") or payload.get("StrippedTextReply") or ""

    logger.info(f"Received Postmark email from {sender}: {subject}")

    await _broadcast_inbound_email(sender=sender, subject=subject, text_body=text_body)

    return {"status": "received"}
