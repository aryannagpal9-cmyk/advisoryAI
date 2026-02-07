"""
Follow-up Agent
Handles action items, email drafts, and follow-up tracking.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta

from .base import BaseAgent, AgentType, QueryIntent, AgentQuery, AgentResponse
from services.logging_service import get_logger

logger = get_logger(__name__)


class FollowupAgent(BaseAgent):
    """Agent for follow-up and action management queries."""
    
    @property
    def agent_type(self) -> AgentType:
        return AgentType.FOLLOWUP
    
    @property
    def supported_intents(self) -> List[QueryIntent]:
        return [
            QueryIntent.DRAFT_EMAIL,
            QueryIntent.SEND_EMAIL,
            QueryIntent.CREATE_TASK,
            QueryIntent.SCHEDULE_MEETING,
            QueryIntent.WAITING_INFO,
            QueryIntent.OPEN_ACTIONS,
            QueryIntent.OVERDUE_FOLLOWUPS,
        ]
    
    async def process(self, query: AgentQuery) -> AgentResponse:
        """Route to specific handler based on intent."""
        handlers = {
            QueryIntent.DRAFT_EMAIL: self._handle_draft_email,
            QueryIntent.SEND_EMAIL: self._handle_send_email,
            QueryIntent.CREATE_TASK: self._handle_create_task,
            QueryIntent.SCHEDULE_MEETING: self._handle_schedule_meeting,
            QueryIntent.WAITING_INFO: self._handle_waiting_info,
            QueryIntent.OPEN_ACTIONS: self._handle_open_actions,
            QueryIntent.OVERDUE_FOLLOWUPS: self._handle_overdue_followups,
        }
        
        handler = handlers.get(query.intent)
        if handler:
            return await handler(query)
        
        return AgentResponse(
            success=False,
            data=None,
            message=f"Handler not implemented for {query.intent.value}",
            agent_type=self.agent_type,
            query_type=query.intent
        )
    
    async def _handle_draft_email(self, query: AgentQuery) -> AgentResponse:
        """Generate an email draft based on context."""
        client_name = query.entities.get("client_name")
        
        # First, try to get context from recent meeting
        context = None
        client_id = None
        
        if client_name:
            # Find client
            clients = self.supabase.table("clients").select("id, name, email").ilike(
                "name", f"%{client_name}%"
            ).execute().data or []
            
            if clients:
                client = clients[0]
                client_id = client["id"]
                
                # Get most recent meeting
                meetings = self.supabase.table("meetings").select(
                    "id, title, notes, recommendations_made, follow_up_notes, scheduled_at"
                ).eq("client_id", client_id).order("scheduled_at", desc=True).limit(1).execute().data
                
                if meetings:
                    context = meetings[0]
        
        if not context:
            # Get the most recent meeting overall
            meetings = self.supabase.table("meetings").select(
                "id, title, notes, recommendations_made, follow_up_notes, scheduled_at, client_id, clients(name, email)"
            ).eq("status", "COMPLETED").order("scheduled_at", desc=True).limit(1).execute().data
            
            if meetings:
                context = meetings[0]
                client_name = context.get("clients", {}).get("name", "the client")
                client_id = context.get("client_id")
        
        if not context:
            return AgentResponse(
                success=False,
                data=None,
                message="No recent meeting found to generate follow-up email. Please specify which client or meeting.",
                agent_type=self.agent_type,
                query_type=query.intent,
                follow_up_suggestions=[
                    "Draft email to David Chen",
                    "Show recent meetings"
                ]
            )
        
        # Generate email using LLM
        recommendations = context.get("recommendations_made") or []
        recs_text = "\n".join([f"- {r.get('type', '')}: {r.get('detail', '')}" for r in recommendations])
        
        prompt = f"""Draft a professional follow-up email after a financial advisory meeting.

Client: {client_name}
Meeting: {context.get('title', 'Recent meeting')}
Date: {context.get('scheduled_at', 'Recently')[:10] if context.get('scheduled_at') else 'Recently'}

Meeting Notes:
{context.get('notes', 'No notes available')}

Recommendations Made:
{recs_text if recs_text else 'None recorded'}

Follow-up notes:
{context.get('follow_up_notes', 'None')}

Write a warm, professional email that:
1. Thanks them for the meeting
2. Summarizes key discussion points
3. Lists agreed action items
4. Mentions next steps
5. Ends with a friendly sign-off

Do not include subject line - just the email body."""

        email_content = self.llm.generate_completion(prompt)
        
        # Generate subject line
        subject_prompt = f"Write a short, professional email subject line for a follow-up email after a meeting about '{context.get('title', 'financial planning')}' with {client_name}. Just the subject line, nothing else."
        subject = self.llm.generate_completion(subject_prompt).strip()
        
        # Store draft
        try:
            self.supabase.table("email_drafts").insert({
                "client_id": client_id,
                "meeting_id": context.get("id"),
                "subject": subject,
                "body": email_content,
                "to_email": context.get("clients", {}).get("email", ""),
                "to_name": client_name,
                "context_type": "FOLLOW_UP",
                "context_summary": f"Follow-up from {context.get('title', 'meeting')}",
                "created_at": datetime.now().isoformat()
            }).execute()
        except Exception as e:
            logger.warning(f"Failed to save email draft: {e}")
        
        message = f"**Draft Follow-up Email to {client_name}:**\n\n"
        message += f"**Subject:** {subject}\n\n"
        message += f"---\n\n{email_content}\n\n---\n\n"
        message += "*This draft has been saved. You can edit it before sending.*"
        
        return AgentResponse(
            success=True,
            data={
                "subject": subject,
                "body": email_content,
                "client_name": client_name,
                "meeting_id": context.get("id")
            },
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            follow_up_suggestions=[
                "Make it more formal",
                "Add a reminder about pension review",
                "Send this email"
            ]
        )

    async def _handle_send_email(self, query: AgentQuery) -> AgentResponse:
        """Actually 'send' (save as sent) an email."""
        client_name = query.entities.get("client_name")
        subject = query.entities.get("subject", "Follow up from our meeting")
        body = query.entities.get("body")
        
        if not body:
            # If no body provided, draft it first
            draft_res = await self._handle_draft_email(query)
            if not draft_res.success:
                return draft_res
            body = draft_res.data.get("body")
            subject = draft_res.data.get("subject")
            client_name = draft_res.data.get("client_name")

        # Find client email
        client = self.supabase.table("clients").select("id, email").ilike("name", f"%{client_name}%").execute().data
        client_id = client[0]["id"] if client else None
        to_email = client[0]["email"] if client else "client@example.com"

        # Record in activity log
        self.supabase.table("audit_logs").insert({
            "action": "EMAIL_SENT",
            "reason": f"Email sent to {client_name}: {subject}",
            "actor": "AGENT_CHAT",
            "metadata": {"subject": subject}
        }).execute()

        # Save to drafts table as SENT
        self.supabase.table("email_drafts").insert({
            "client_id": client_id,
            "subject": subject,
            "body": body,
            "sent_at": datetime.now().isoformat(),
            "to_email": to_email,
            "to_name": client_name
        }).execute()

        return AgentResponse(
            success=True,
            data={"status": "SENT"},
            message=f"✅ Email has been sent to {client_name}.\n\n**Subject:** {subject}",
            agent_type=self.agent_type,
            query_type=query.intent
        )

    async def _handle_create_task(self, query: AgentQuery) -> AgentResponse:
        """Create a new action item."""
        title = query.entities.get("task_title") or query.raw_query
        client_name = query.entities.get("client_name")
        priority = query.entities.get("priority", "MEDIUM")
        
        client_id = None
        if client_name:
            client = self.supabase.table("clients").select("id").ilike("name", f"%{client_name}%").execute().data
            if client:
                client_id = client[0]["id"]

        res = self.supabase.table("action_items").insert({
            "title": title,
            "client_id": client_id,
            "priority": priority,
            "status": "PENDING",
            "owner": "ADVISOR",
            "created_at": datetime.now().isoformat()
        }).execute()

        # Log it
        self.supabase.table("audit_logs").insert({
            "action": "TASK_CREATED",
            "reason": f"Task created: {title}",
            "actor": "AGENT_CHAT"
        }).execute()

        return AgentResponse(
            success=True,
            data=res.data[0] if res.data else None,
            message=f"✅ Task created: **{title}**" + (f" for {client_name}" if client_name else ""),
            agent_type=self.agent_type,
            query_type=query.intent
        )

    async def _handle_schedule_meeting(self, query: AgentQuery) -> AgentResponse:
        """Schedule a new meeting."""
        client_name = query.entities.get("client_name")
        title = query.entities.get("meeting_title", f"Meeting with {client_name}")
        
        if not client_name:
            return AgentResponse(
                success=False,
                data=None,
                message="I need to know which client to schedule the meeting with.",
                agent_type=self.agent_type,
                query_type=query.intent
            )

        client = self.supabase.table("clients").select("id").ilike("name", f"%{client_name}%").execute().data
        if not client:
            return AgentResponse(success=False, data=None, message=f"Client '{client_name}' not found.", agent_type=self.agent_type, query_type=query.intent)
        
        client_id = client[0]["id"]
        
        # Simple default: next Monday at 10am
        next_date = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
        scheduled_at = next_date.replace(hour=10, minute=0, second=0, microsecond=0).isoformat()

        res = self.supabase.table("meetings").insert({
            "client_id": client_id,
            "title": title,
            "scheduled_at": scheduled_at,
            "status": "SCHEDULED",
            "meeting_type": "VIDEO_CALL"
        }).execute()

        # Log it
        self.supabase.table("audit_logs").insert({
            "action": "MEETING_SCHEDULED",
            "reason": f"Meeting scheduled with {client_name}: {title}",
            "actor": "AGENT_CHAT"
        }).execute()

        return AgentResponse(
            success=True,
            data=res.data[0] if res.data else None,
            message=f"🗓️ Meeting scheduled with **{client_name}** for {next_date.strftime('%A, %d %b')} at 10:00 AM.",
            agent_type=self.agent_type,
            query_type=query.intent
        )
    
    async def _handle_waiting_info(self, query: AgentQuery) -> AgentResponse:
        """Find clients we're waiting on for information or decisions."""
        # Get pending action items where owner is CLIENT
        actions = self.supabase.table("action_items").select(
            "id, title, description, due_date, status, client_id, clients(name)"
        ).eq("owner", "CLIENT").in_("status", ["PENDING", "IN_PROGRESS"]).execute().data or []
        
        # Also get pending requests from clients
        requests = self.supabase.table("requests").select(
            "id, title, status, created_at, cases(client_id, clients(name))"
        ).eq("owner_type", "CLIENT").in_("status", ["PENDING", "WAITING"]).execute().data or []
        
        results = []
        
        for action in actions:
            client_info = action.get("clients", {})
            results.append({
                "type": "action_item",
                "id": action.get("id"),
                "title": action.get("title"),
                "client_name": client_info.get("name", "Unknown"),
                "due_date": action.get("due_date"),
                "status": action.get("status")
            })
        
        for req in requests:
            case_info = req.get("cases", {})
            client_info = case_info.get("clients", {}) if case_info else {}
            results.append({
                "type": "document_request",
                "id": req.get("id"),
                "title": req.get("title"),
                "client_name": client_info.get("name", "Unknown"),
                "since": req.get("created_at"),
                "status": req.get("status")
            })
        
        message = f"**Waiting on clients for {len(results)} item(s):**\n\n"
        
        # Group by client
        by_client = {}
        for r in results:
            name = r["client_name"]
            if name not in by_client:
                by_client[name] = []
            by_client[name].append(r)
        
        for client_name, items in by_client.items():
            message += f"**{client_name}:**\n"
            for item in items:
                message += f"  • {item['title']} ({item['type'].replace('_', ' ')})\n"
        
        return AgentResponse(
            success=True,
            data=results,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            follow_up_suggestions=[
                "Send reminder emails",
                "Which are most urgent?"
            ]
        )
    
    async def _handle_open_actions(self, query: AgentQuery) -> AgentResponse:
        """Show all open action items across client base."""
        actions = self.supabase.table("action_items").select(
            "id, title, description, due_date, status, priority, owner, category, client_id, clients(name)"
        ).in_("status", ["PENDING", "IN_PROGRESS", "OVERDUE"]).order(
            "due_date"
        ).execute().data or []
        
        # Group by status
        by_status = {
            "OVERDUE": [],
            "PENDING": [],
            "IN_PROGRESS": []
        }
        
        for action in actions:
            status = action.get("status", "PENDING")
            if status in by_status:
                client_info = action.get("clients", {})
                by_status[status].append({
                    "id": action.get("id"),
                    "title": action.get("title"),
                    "client_name": client_info.get("name", "Unknown"),
                    "due_date": action.get("due_date"),
                    "priority": action.get("priority", "MEDIUM"),
                    "owner": action.get("owner")
                })
        
        message = f"**Open Action Items ({len(actions)} total):**\n\n"
        
        if by_status["OVERDUE"]:
            message += f"🔴 **OVERDUE ({len(by_status['OVERDUE'])}):**\n"
            for a in by_status["OVERDUE"][:5]:
                message += f"  • {a['title']} ({a['client_name']})\n"
        
        if by_status["IN_PROGRESS"]:
            message += f"\n🟡 **IN PROGRESS ({len(by_status['IN_PROGRESS'])}):**\n"
            for a in by_status["IN_PROGRESS"][:5]:
                message += f"  • {a['title']} ({a['client_name']})\n"
        
        if by_status["PENDING"]:
            message += f"\n⚪ **PENDING ({len(by_status['PENDING'])}):**\n"
            for a in by_status["PENDING"][:5]:
                due = a['due_date'][:10] if a['due_date'] else "No due date"
                message += f"  • {a['title']} ({a['client_name']}) - Due: {due}\n"
        
        return AgentResponse(
            success=True,
            data=by_status,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            metadata={
                "overdue_count": len(by_status["OVERDUE"]),
                "in_progress_count": len(by_status["IN_PROGRESS"]),
                "pending_count": len(by_status["PENDING"])
            },
            follow_up_suggestions=[
                "Show only my high priority items",
                "What's overdue for this week?"
            ]
        )
    
    async def _handle_overdue_followups(self, query: AgentQuery) -> AgentResponse:
        """Find follow-ups that are now overdue."""
        overdue = self.supabase.table("action_items").select(
            "id, title, description, due_date, promised_at, promise_context, client_id, clients(name)"
        ).eq("status", "OVERDUE").order("due_date").execute().data or []
        
        message = f"**{len(overdue)} overdue follow-up(s):**\n\n"
        
        for item in overdue[:10]:
            client_info = item.get("clients", {})
            due = item['due_date'][:10] if item.get('due_date') else "Unknown"
            days_overdue = 0
            if item.get('due_date'):
                due_dt = datetime.fromisoformat(item['due_date'].replace('Z', '+00:00'))
                days_overdue = (datetime.now(due_dt.tzinfo) - due_dt).days
            
            message += f"🔴 **{item['title']}** ({client_info.get('name', 'Unknown')})\n"
            message += f"   Due: {due} ({days_overdue} days overdue)\n"
            if item.get("promise_context"):
                message += f"   _\"{item['promise_context']}\"_\n"
            message += "\n"
        
        return AgentResponse(
            success=True,
            data=overdue,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            metadata={"overdue_count": len(overdue)},
            follow_up_suggestions=[
                "Complete the top overdue item",
                "Send apology emails for these"
            ]
        )
