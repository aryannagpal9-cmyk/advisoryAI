"""
Compliance Agent
Handles compliance-related queries including recommendation history, risk discussions, and audit trails.
"""
from typing import List, Dict, Any
from datetime import datetime

from .base import BaseAgent, AgentType, QueryIntent, AgentQuery, AgentResponse
from services.logging_service import get_logger

logger = get_logger(__name__)


class ComplianceAgent(BaseAgent):
    """Agent for compliance and audit trail queries."""
    
    @property
    def agent_type(self) -> AgentType:
        return AgentType.COMPLIANCE
    
    @property
    def supported_intents(self) -> List[QueryIntent]:
        return [
            QueryIntent.RECOMMENDATION_HISTORY,
            QueryIntent.RISK_DISCUSSION,
            QueryIntent.PLATFORM_RECOMMENDATIONS,
            QueryIntent.VOLATILITY_CONCERNS,
            QueryIntent.SUSTAINABLE_INVESTING,
            QueryIntent.PENDING_DOCUMENTS,
            QueryIntent.PROMISED_ITEMS,
        ]
    
    async def process(self, query: AgentQuery) -> AgentResponse:
        """Route to specific handler based on intent."""
        handlers = {
            QueryIntent.RECOMMENDATION_HISTORY: self._handle_recommendation_history,
            QueryIntent.RISK_DISCUSSION: self._handle_risk_discussion,
            QueryIntent.VOLATILITY_CONCERNS: self._handle_volatility_concerns,
            QueryIntent.SUSTAINABLE_INVESTING: self._handle_sustainable_investing,
            QueryIntent.PENDING_DOCUMENTS: self._handle_pending_documents,
            QueryIntent.PROMISED_ITEMS: self._handle_promised_items,
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
    
    async def _handle_recommendation_history(self, query: AgentQuery) -> AgentResponse:
        """Pull all recommendations made to a specific client with rationale."""
        client_name = query.entities.get("client_name")
        
        # If no client specified, show guidance
        if not client_name:
            return AgentResponse(
                success=True,
                data=None,
                message="Please specify a client name. For example: 'Show recommendations made to David Chen'",
                agent_type=self.agent_type,
                query_type=query.intent,
                follow_up_suggestions=[
                    "Show recommendations made to David Chen",
                    "What did I recommend to Sarah Williams?"
                ]
            )
        
        # Search for client
        clients = self.supabase.table("clients").select("id, name").ilike(
            "name", f"%{client_name}%"
        ).execute().data or []
        
        if not clients:
            return AgentResponse(
                success=False,
                data=None,
                message=f"No client found matching '{client_name}'",
                agent_type=self.agent_type,
                query_type=query.intent
            )
        
        client = clients[0]
        client_id = client["id"]
        
        # Get meetings with recommendations
        meetings = self.supabase.table("meetings").select(
            "id, meeting_type, scheduled_at, recommendations_made, notes"
        ).eq("client_id", client_id).order("scheduled_at", desc=True).execute().data or []
        
        recommendations = []
        for meeting in meetings:
            recs = meeting.get("recommendations_made") or []
            if recs:
                for rec in recs:
                    recommendations.append({
                        "date": meeting.get("scheduled_at"),
                        "meeting_type": meeting.get("meeting_type"),
                        "type": rec.get("type"),
                        "detail": rec.get("detail"),
                        "notes": meeting.get("notes")
                    })
        
        message = f"**Recommendations made to {client['name']}:**\n\n"
        if recommendations:
            for rec in recommendations[:10]:
                date_str = rec["date"][:10] if rec["date"] else "Unknown date"
                message += f"📋 **{date_str}** ({rec['meeting_type']})\n"
                message += f"   → {rec['type']}: {rec['detail']}\n\n"
        else:
            message = f"No recorded recommendations found for {client['name']}."
        
        return AgentResponse(
            success=True,
            data=recommendations,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            metadata={"client_id": client_id, "client_name": client["name"]},
            follow_up_suggestions=[
                f"Show risk discussions with {client['name']}",
                f"What action items are pending for {client['name']}?"
            ]
        )
    
    async def _handle_risk_discussion(self, query: AgentQuery) -> AgentResponse:
        """Show exact wording of risk discussions with a client."""
        client_name = query.entities.get("client_name")
        
        if not client_name:
            return AgentResponse(
                success=True,
                data=None,
                message="Please specify a client name. For example: 'Show risk discussions with the Williams family'",
                agent_type=self.agent_type,
                query_type=query.intent
            )
        
        # Search for client
        clients = self.supabase.table("clients").select("id, name").ilike(
            "name", f"%{client_name}%"
        ).execute().data or []
        
        if not clients:
            return AgentResponse(
                success=False,
                data=None,
                message=f"No client found matching '{client_name}'",
                agent_type=self.agent_type,
                query_type=query.intent
            )
        
        client = clients[0]
        
        # Get meetings with risk discussions
        meetings = self.supabase.table("meetings").select(
            "id, meeting_type, scheduled_at, risk_discussions, topics_discussed"
        ).eq("client_id", client["id"]).not_.is_("risk_discussions", "null").order(
            "scheduled_at", desc=True
        ).execute().data or []
        
        message = f"**Risk discussions documented for {client['name']}:**\n\n"
        
        if meetings:
            for meeting in meetings[:5]:
                date_str = meeting["scheduled_at"][:10] if meeting["scheduled_at"] else "Unknown"
                message += f"📅 **{date_str}** ({meeting['meeting_type']})\n"
                message += f"```\n{meeting['risk_discussions']}\n```\n\n"
        else:
            message = f"No documented risk discussions found for {client['name']}."
        
        return AgentResponse(
            success=True,
            data=meetings,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            metadata={"client_name": client["name"]}
        )
    
    async def _handle_volatility_concerns(self, query: AgentQuery) -> AgentResponse:
        """Find client conversations that mentioned concerns about market volatility."""
        # Search meetings for volatility-related content
        meetings = self.supabase.table("meetings").select(
            "id, client_id, scheduled_at, notes, client_concerns, clients(name)"
        ).not_.is_("client_concerns", "null").execute().data or []
        
        results = []
        volatility_keywords = ["volatility", "volatile", "market", "crash", "drop", "fall", "worried", "nervous"]
        
        for meeting in meetings:
            concerns = meeting.get("client_concerns") or []
            notes = (meeting.get("notes") or "").lower()
            
            # Check if volatility mentioned in concerns or notes
            has_volatility = any(
                any(kw in str(concern).lower() for kw in volatility_keywords)
                for concern in concerns
            ) or any(kw in notes for kw in volatility_keywords)
            
            if has_volatility:
                client_info = meeting.get("clients", {})
                results.append({
                    "client_id": meeting.get("client_id"),
                    "client_name": client_info.get("name", "Unknown"),
                    "meeting_date": meeting.get("scheduled_at"),
                    "concerns": concerns
                })
        
        message = f"**{len(results)} meeting(s)** where volatility concerns were raised:\n\n"
        for r in results[:10]:
            date_str = r["meeting_date"][:10] if r["meeting_date"] else "Unknown"
            concerns_str = ", ".join(str(c) for c in r["concerns"][:3])
            message += f"• **{r['client_name']}** ({date_str}): {concerns_str}\n"
        
        return AgentResponse(
            success=True,
            data=results,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent
        )
    
    async def _handle_sustainable_investing(self, query: AgentQuery) -> AgentResponse:
        """Generate summary of sustainable investing discussions."""
        # Get clients with ESG preferences
        profiles = self.supabase.table("client_profiles").select(
            "client_id, preferences, clients(name)"
        ).execute().data or []
        
        esg_clients = []
        for profile in profiles:
            prefs = profile.get("preferences") or {}
            if prefs.get("sustainable") or prefs.get("ESG") or prefs.get("exclude_tobacco"):
                client_info = profile.get("clients", {})
                esg_clients.append({
                    "client_id": profile.get("client_id"),
                    "client_name": client_info.get("name", "Unknown"),
                    "preferences": prefs
                })
        
        # Get meetings discussing sustainable investing
        meetings = self.supabase.table("meetings").select(
            "client_id, topics_discussed, notes, clients(name)"
        ).execute().data or []
        
        sustainable_meetings = []
        for meeting in meetings:
            topics = meeting.get("topics_discussed") or []
            notes = (meeting.get("notes") or "").lower()
            
            if any("sustain" in str(t).lower() or "esg" in str(t).lower() for t in topics) or \
               "sustainable" in notes or "esg" in notes or "ethical" in notes:
                sustainable_meetings.append({
                    "client_name": meeting.get("clients", {}).get("name", "Unknown"),
                    "topics": topics,
                    "summary": meeting.get("notes", "")[:200]
                })
        
        message = f"**Sustainable/ESG Investing Summary:**\n\n"
        message += f"📊 **{len(esg_clients)} client(s)** have ESG preferences recorded:\n"
        for c in esg_clients[:5]:
            pref_list = [k for k, v in c["preferences"].items() if v and k != "sustainable"]
            message += f"• {c['client_name']}: {', '.join(pref_list) if pref_list else 'General ESG'}\n"
        
        message += f"\n📝 **{len(sustainable_meetings)} meeting(s)** discussed sustainable investing\n"
        
        return AgentResponse(
            success=True,
            data={"esg_clients": esg_clients, "meetings": sustainable_meetings},
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent
        )
    
    async def _handle_pending_documents(self, query: AgentQuery) -> AgentResponse:
        """Find documents still waiting from clients."""
        # Get pending requests
        requests = self.supabase.table("requests").select(
            "id, title, status, owner_type, created_at, case_id, cases(client_id, clients(name))"
        ).in_("status", ["PENDING", "WAITING"]).execute().data or []
        
        results = []
        for req in requests:
            case_info = req.get("cases", {})
            client_info = case_info.get("clients", {}) if case_info else {}
            
            results.append({
                "request_id": req.get("id"),
                "document": req.get("title"),
                "from": req.get("owner_type"),
                "client_name": client_info.get("name", "Unknown"),
                "waiting_since": req.get("created_at"),
                "status": req.get("status")
            })
        
        message = f"**{len(results)} document(s)** still waiting:\n\n"
        for r in results[:15]:
            days = 0
            if r["waiting_since"]:
                waiting_dt = datetime.fromisoformat(r["waiting_since"].replace('Z', '+00:00'))
                days = (datetime.now(waiting_dt.tzinfo) - waiting_dt).days
            
            message += f"• **{r['document']}** from {r['from']} ({r['client_name']}) - {days} days\n"
        
        return AgentResponse(
            success=True,
            data=results,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            follow_up_suggestions=[
                "Send reminders for overdue documents",
                "Which are blocking cases?"
            ]
        )
    
    async def _handle_promised_items(self, query: AgentQuery) -> AgentResponse:
        """Find items promised to clients that are pending."""
        client_name = query.entities.get("client_name")
        
        # Get action items that were promised
        query_builder = self.supabase.table("action_items").select(
            "id, title, description, due_date, status, promised_at, promise_context, client_id, clients(name)"
        ).not_.is_("promised_at", "null")
        
        if client_name:
            # Filter by client name via join
            query_builder = query_builder.ilike("clients.name", f"%{client_name}%")
        
        actions = query_builder.execute().data or []
        
        results = []
        for action in actions:
            client_info = action.get("clients", {})
            results.append({
                "action_id": action.get("id"),
                "title": action.get("title"),
                "client_name": client_info.get("name", "Unknown"),
                "promised_at": action.get("promised_at"),
                "context": action.get("promise_context"),
                "due_date": action.get("due_date"),
                "status": action.get("status")
            })
        
        # Filter to pending/overdue
        pending = [r for r in results if r["status"] in ["PENDING", "IN_PROGRESS", "OVERDUE"]]
        
        if client_name:
            message = f"**Promised items for {client_name}:**\n\n"
        else:
            message = f"**All promised items pending ({len(pending)}):**\n\n"
        
        for r in pending[:10]:
            status_emoji = "🔴" if r["status"] == "OVERDUE" else "🟡"
            message += f"{status_emoji} **{r['title']}** for {r['client_name']}\n"
            if r["context"]:
                message += f"   _\"{r['context']}\"_\n"
        
        return AgentResponse(
            success=True,
            data=pending,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent
        )
    
    async def generate_all_insights(self) -> List[Dict[str, Any]]:
        """Generate compliance-related insights."""
        insights = []
        
        # Check for overdue promised items
        overdue = self.supabase.table("action_items").select(
            "id, title, client_id, clients(name)"
        ).eq("status", "OVERDUE").not_.is_("promised_at", "null").execute().data or []
        
        for item in overdue[:3]:
            client_info = item.get("clients", {})
            insights.append({
                "category": "COMPLIANCE",
                "title": "Overdue Promised Item",
                "description": f"'{item['title']}' promised to {client_info.get('name', 'client')} is overdue.",
                "client_id": item.get("client_id"),
                "priority": "HIGH"
            })
        
        return insights
