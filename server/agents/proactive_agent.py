"""
Proactive Agent
Generates proactive insights about client opportunities, life events, and relationship management.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random

from .base import BaseAgent, AgentType, QueryIntent, AgentQuery, AgentResponse
from services.logging_service import get_logger

logger = get_logger(__name__)


class ProactiveAgent(BaseAgent):
    """Agent for proactive client insights and opportunity identification."""
    
    @property
    def agent_type(self) -> AgentType:
        return AgentType.PROACTIVE
    
    @property
    def supported_intents(self) -> List[QueryIntent]:
        return [
            QueryIntent.OVERDUE_REVIEW,
            QueryIntent.BUSINESS_OPPORTUNITY,
            QueryIntent.EDUCATION_PLANNING,
            QueryIntent.SIMILAR_PROFILES,
            QueryIntent.ESTATE_PLANNING,
            QueryIntent.CASHFLOW_SERVICE,
            QueryIntent.NO_PROTECTION,
            QueryIntent.EXIT_PLANNING,
            QueryIntent.BIRTHDAYS,
            QueryIntent.CREATE_CASE
        ]
    
    async def process(self, query: AgentQuery) -> AgentResponse:
        """Route to specific handler based on intent."""
        handlers = {
            QueryIntent.OVERDUE_REVIEW: self._handle_overdue_reviews,
            QueryIntent.BUSINESS_OPPORTUNITY: self._handle_business_opportunities,
            QueryIntent.EDUCATION_PLANNING: self._handle_education_planning,
            QueryIntent.SIMILAR_PROFILES: self._handle_similar_profiles,
            QueryIntent.ESTATE_PLANNING: self._handle_estate_planning,
            QueryIntent.CASHFLOW_SERVICE: self._handle_cashflow_service,
            QueryIntent.NO_PROTECTION: self._handle_no_protection,
            QueryIntent.EXIT_PLANNING: self._handle_exit_planning,
            QueryIntent.BIRTHDAYS: self._handle_birthdays,
            QueryIntent.CREATE_CASE: self._handle_create_case
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
    
    async def _handle_overdue_reviews(self, query: AgentQuery) -> AgentResponse:
        """Find clients who haven't had a review in over 12 months."""
        now = query.context.get("simulated_now") or datetime.now()
        cutoff_date = now - timedelta(days=365)
        
        profiles = self.supabase.table("client_profiles").select(
            "client_id, last_review_date, next_review_due, review_frequency_months, clients(name, email)"
        ).execute().data or []
        
        overdue = []
        for profile in profiles:
            last_review = profile.get("last_review_date")
            next_due = profile.get("next_review_due")
            
            if last_review:
                last_review_dt = datetime.fromisoformat(last_review.replace('Z', '+00:00'))
                if last_review_dt.replace(tzinfo=None) < cutoff_date.replace(tzinfo=None):
                    months_overdue = (now.replace(tzinfo=None) - last_review_dt.replace(tzinfo=None)).days // 30
                    client_info = profile.get("clients", {})
                    overdue.append({
                        "client_id": profile.get("client_id"),
                        "client_name": client_info.get("name", "Unknown"),
                        "email": client_info.get("email"),
                        "last_review_date": last_review,
                        "months_since_review": months_overdue,
                        "next_review_due": next_due
                    })
        
        # Sort by most overdue first
        overdue.sort(key=lambda x: x["months_since_review"], reverse=True)
        
        message = f"**{len(overdue)} client(s)** haven't had a review in over 12 months:\n\n"
        for client in overdue[:10]:
            message += f"• **{client['client_name']}**: {client['months_since_review']} months since last review\n"
        
        if overdue:
            message += "\n⚠️ *Compliance requires annual reviews. Consider prioritizing these clients.*"
        
        return AgentResponse(
            success=True,
            data=overdue,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            metadata={"overdue_count": len(overdue)},
            follow_up_suggestions=[
                "Schedule reviews for these clients",
                "Draft review reminder emails",
                "Which have the most complex portfolios?"
            ]
        )
    
    async def _handle_business_opportunities(self, query: AgentQuery) -> AgentResponse:
        """Find business owners who might benefit from R&D tax credits or other opportunities."""
        profiles = self.supabase.table("client_profiles").select(
            "client_id, business_type, has_exit_plan, annual_income, clients(name)"
        ).eq("is_business_owner", True).execute().data or []
        
        opportunities = []
        for profile in profiles:
            client_info = profile.get("clients", {})
            business_type = profile.get("business_type", "Unknown")
            
            opp_list = []
            
            # R&D tax credit eligible businesses
            tech_keywords = ["tech", "software", "engineering", "research", "development", "innovation"]
            if any(kw in (business_type or "").lower() for kw in tech_keywords):
                opp_list.append("R&D Tax Credits")
            
            # Exit planning
            if not profile.get("has_exit_plan"):
                opp_list.append("Exit Planning")
            
            # High income - pension opportunities
            if (profile.get("annual_income") or 0) > 100000:
                opp_list.append("Salary Sacrifice / Pension Planning")
            
            if opp_list:
                opportunities.append({
                    "client_id": profile.get("client_id"),
                    "client_name": client_info.get("name", "Unknown"),
                    "business_type": business_type,
                    "opportunities": opp_list
                })
        
        message = f"**{len(opportunities)} business owner(s)** with potential opportunities:\n\n"
        for opp in opportunities[:10]:
            opps_str = ", ".join(opp["opportunities"])
            message += f"• **{opp['client_name']}** ({opp['business_type']}): {opps_str}\n"
        
        return AgentResponse(
            success=True,
            data=opportunities,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            follow_up_suggestions=[
                "Tell me more about R&D tax credits",
                "Which need exit planning urgently?"
            ]
        )
    
    async def _handle_education_planning(self, query: AgentQuery) -> AgentResponse:
        """Find clients with children approaching university age but no education planning."""
        profiles = self.supabase.table("client_profiles").select(
            "client_id, children_ages, clients(name)"
        ).eq("has_children", True).execute().data or []
        
        results = []
        for profile in profiles:
            children_ages = profile.get("children_ages") or []
            
            # Children between 14-18 (approaching university)
            approaching_uni = [age for age in children_ages if 14 <= age <= 18]
            
            if approaching_uni:
                client_info = profile.get("clients", {})
                results.append({
                    "client_id": profile.get("client_id"),
                    "client_name": client_info.get("name", "Unknown"),
                    "children_ages": children_ages,
                    "children_approaching_uni": approaching_uni,
                    "years_to_university": [18 - age for age in approaching_uni]
                })
        
        # Sort by nearest to university
        results.sort(key=lambda x: min(x["years_to_university"]))
        
        message = f"**{len(results)} client(s)** have children approaching university age:\n\n"
        for r in results[:10]:
            ages_str = ", ".join(str(a) for a in r["children_approaching_uni"])
            message += f"• **{r['client_name']}**: Children aged {ages_str}\n"
        
        return AgentResponse(
            success=True,
            data=results,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            follow_up_suggestions=[
                "What education funding options exist?",
                "Do any have Junior ISAs?"
            ]
        )
    
    async def _handle_estate_planning(self, query: AgentQuery) -> AgentResponse:
        """Find high-net-worth clients without estate planning."""
        HNW_THRESHOLD = 500000
        
        # Get all investments aggregated by client
        investments = self.supabase.table("investments").select(
            "client_id, current_value"
        ).execute().data or []
        
        # Aggregate by client
        client_values = {}
        for inv in investments:
            client_id = inv.get("client_id")
            if client_id not in client_values:
                client_values[client_id] = 0
            client_values[client_id] += inv.get("current_value", 0) or 0
        
        # Find HNW clients
        hnw_clients = [cid for cid, val in client_values.items() if val >= HNW_THRESHOLD]
        
        if not hnw_clients:
            return AgentResponse(
                success=True,
                data=[],
                message="No high-net-worth clients found above the threshold.",
                agent_type=self.agent_type,
                query_type=query.intent
            )
        
        # Get their profiles
        profiles = self.supabase.table("client_profiles").select(
            "client_id, preferences, clients(name)"
        ).in_("client_id", hnw_clients).execute().data or []
        
        # Check for estate planning (simplified - check if mentioned in preferences/notes)
        results = []
        for profile in profiles:
            client_id = profile.get("client_id")
            prefs = profile.get("preferences") or {}
            
            # Assume no estate planning if not explicitly noted
            has_estate_plan = prefs.get("has_estate_plan", False)
            
            if not has_estate_plan:
                # Calculate potential IHT
                total_value = client_values.get(client_id, 0)
                nil_rate = 325000
                residence_nil_rate = 175000  # Simplified
                iht_threshold = nil_rate + residence_nil_rate
                potential_iht = max(0, (total_value - iht_threshold) * 0.4)
                
                client_info = profile.get("clients", {})
                results.append({
                    "client_id": client_id,
                    "client_name": client_info.get("name", "Unknown"),
                    "total_assets": total_value,
                    "potential_iht": potential_iht
                })
        
        results.sort(key=lambda x: x["potential_iht"], reverse=True)
        
        message = f"**{len(results)} high-net-worth client(s)** without estate planning:\n\n"
        for r in results[:10]:
            message += f"• **{r['client_name']}**: £{r['total_assets']:,.0f} assets, ~£{r['potential_iht']:,.0f} potential IHT\n"
        
        total_iht = sum(r["potential_iht"] for r in results)
        
        return AgentResponse(
            success=True,
            data=results,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            metadata={"total_potential_iht": total_iht},
            follow_up_suggestions=[
                "What trust options are available?",
                "Which have children who could receive gifts?"
            ]
        )
    
    async def _handle_exit_planning(self, query: AgentQuery) -> AgentResponse:
        """Find business owner clients who haven't discussed exit planning."""
        profiles = self.supabase.table("client_profiles").select(
            "client_id, business_type, has_exit_plan, clients(name)"
        ).eq("is_business_owner", True).eq("has_exit_plan", False).execute().data or []
        
        results = []
        for profile in profiles:
            client_info = profile.get("clients", {})
            results.append({
                "client_id": profile.get("client_id"),
                "client_name": client_info.get("name", "Unknown"),
                "business_type": profile.get("business_type", "Unknown")
            })
        
        message = f"**{len(results)} business owner(s)** haven't discussed exit planning:\n\n"
        for r in results[:10]:
            message += f"• **{r['client_name']}** ({r['business_type']})\n"
        
        return AgentResponse(
            success=True,
            data=results,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            follow_up_suggestions=[
                "What are the exit planning options?",
                "Which have the highest business value?"
            ]
        )
    
    async def _handle_birthdays(self, query: AgentQuery) -> AgentResponse:
        """Find clients with birthdays this month."""
        # Use simulated now if available in context
        now = query.context.get("simulated_now") or datetime.now()
        current_month = now.strftime("%B")
        current_day = now.day
        
        # Mock response - in production, query clients.date_of_birth
        return AgentResponse(
            success=True,
            data=[
                {
                    "client_id": "11111111-1111-1111-1111-111111111109",
                    "client_name": "Jennifer Brown",
                    "birthday": f"8 {current_month}"
                }
            ],
            message=f"**Client birthdays in {current_month}:**\n\n• **Jennifer Brown**: 15th {current_month}\n\n🎂 *Consider sending a birthday message or small gift!*",
            agent_type=self.agent_type,
            query_type=query.intent,
            follow_up_suggestions=[
                "Draft a birthday email for Jennifer",
                "Set a reminder for next week"
            ]
        )
    
    async def generate_all_insights(self, simulated_now: Optional[datetime] = None, persist: bool = False) -> List[Dict[str, Any]]:
        """Generate proactive insights for all clients."""
        insights = []
        now = simulated_now or datetime.now()
        
        # Overdue reviews
        dummy_query = AgentQuery(raw_query="", intent=QueryIntent.OVERDUE_REVIEW, entities={}, context={"simulated_now": now})
        response = await self._handle_overdue_reviews(dummy_query)
        for client in (response.data or [])[:3]:
            insight = {
                "category": "COMPLIANCE",
                "title": "Annual Review Overdue",
                "description": f"{client['client_name']} hasn't had a review in {client['months_since_review']} months.",
                "client_id": client["client_id"],
                "priority": "CRITICAL" if client["months_since_review"] > 14 else "HIGH",
                "metrics": {"months_overdue": client["months_since_review"] - 12}
            }
            insights.append(insight)
            if persist:
                await self._ensure_insight_exists(insight, now)
        
        # Education planning
        dummy_query.intent = QueryIntent.EDUCATION_PLANNING
        response = await self._handle_education_planning(dummy_query)
        for client in (response.data or [])[:2]:
            min_years = min(client["years_to_university"])
            insight = {
                "category": "RELATIONSHIP",
                "title": "Education Planning Needed",
                "description": f"{client['client_name']} has children approaching university in {min_years} year(s).",
                "client_id": client["client_id"],
                "priority": "MEDIUM" if min_years > 2 else "HIGH",
                "metrics": {"years_to_uni": min_years}
            }
            insights.append(insight)
            if persist:
                await self._ensure_insight_exists(insight, now)
        
        return insights

    async def _handle_create_case(self, query: AgentQuery) -> AgentResponse:
        """Create a new business case."""
        client_name = query.entities.get("client_name")
        title = query.entities.get("case_title") or query.raw_query
        
        if not client_name:
            return AgentResponse(success=False, data=None, message="I need to know which client this case is for.", agent_type=self.agent_type, query_type=query.intent)

        # Find client
        client = self.supabase.table("clients").select("id").ilike("name", f"%{client_name}%").execute().data
        if not client:
            return AgentResponse(success=False, data=None, message=f"Client '{client_name}' not found.", agent_type=self.agent_type, query_type=query.intent)
        
        client_id = client[0]["id"]
        
        # Create Case
        res = self.supabase.table("cases").insert({
            "client_id": client_id,
            "title": title if len(title) < 100 else title[:97] + "...",
            "status": "ACTIVE",
            "priority": "MEDIUM",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }).execute()

        # Log action
        self.supabase.table("audit_logs").insert({
            "action": "CASE_CREATED",
            "reason": f"New case created: {title} for {client_name}",
            "actor": "AGENT"
        }).execute()

        return AgentResponse(
            success=True,
            data=res.data[0] if res.data else None,
            message=f"📁 Created new case: **{title}** for {client_name}.",
            agent_type=self.agent_type,
            query_type=query.intent
        )

    async def _ensure_insight_exists(self, insight_data: Dict[str, Any], now: datetime):
        """Save insight to DB if not already exists with same title/client within 30 days."""
        try:
            # Check for existing similar insight in last 30 days
            cutoff = now - timedelta(days=30)
            existing = self.supabase.table("insights").select("id").eq("client_id", insight_data["client_id"]).eq("title", insight_data["title"]).gte("created_at", cutoff.isoformat()).execute()
            
            if not existing.data:
                self.supabase.table("insights").insert({
                    "client_id": insight_data["client_id"],
                    "category": insight_data["category"],
                    "title": insight_data["title"],
                    "description": insight_data["description"],
                    "priority": insight_data["priority"],
                    "metrics": insight_data["metrics"],
                    "created_at": now.isoformat()
                }).execute()
        except Exception as e:
            logger.error(f"Failed to persist insight: {e}")

    async def evaluate_and_act(self, simulated_now: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Autonomous Loop: Evaluate current state and take actions.
        """
        actions_taken = []
        now = simulated_now or datetime.now()
        logger.info(f"ProactiveAgent evaluating state for autonomous actions (SimDate: {now})...")
        
        # 1. Check Birthdays (Send Email)
        # Mock query for birthdays with context
        dummy_query = AgentQuery(raw_query="", intent=QueryIntent.BIRTHDAYS, entities={}, context={"simulated_now": now})
        birthday_resp = await self._handle_birthdays(dummy_query)
        
        if birthday_resp.success and birthday_resp.data:
            for bday in birthday_resp.data:
                # Check if we already sent an email today (deduplication)
                # In a real app, check DB. Here we assume simulation runs once per day.
                
                subject = f"Happy Birthday {bday['client_name']}!"
                body = f"Dear {bday['client_name']},\n\nWishing you a wonderful birthday!\n\nBest regards,\nYour Financial Advisor"
                
                # Take action
                await self._send_email(bday["client_name"], bday.get("email", "client@example.com"), subject, body, bday.get("client_id"), simulated_now=now)
                
                actions_taken.append({
                    "action": "EMAIL_SENT",
                    "description": f"Sent birthday email to {bday['client_name']}",
                    "client_id": bday.get("client_id")
                })

        # 2. Check Critical Insights (Create Action Items)
        insights = await self.generate_all_insights(simulated_now=now, persist=True)
        for insight in insights:
            if insight.get("priority") == "CRITICAL" and insight.get("title") == "Annual Review Overdue":
                # Create Task
                task_title = f"Schedule Annual Review for {insight.get('description', '').split(' ')[0]}"
                
                # Check duplication first
                existing = self.supabase.table("action_items").select("id").eq("title", task_title).eq("status", "PENDING").execute()
                if not existing.data:
                    await self._create_action(task_title, insight.get("client_id"), "HIGH", simulated_now=now)
                    actions_taken.append({
                        "action": "TASK_CREATED",
                        "description": f"Created task: {task_title}",
                        "client_id": insight.get("client_id")
                    })
        
        # 3. Check Business Opportunities (Create Cases)
        # 10% chance per day to keep it realistic but visible
        if random.random() < 0.1:
            dummy_query.intent = QueryIntent.BUSINESS_OPPORTUNITY
            biz_resp = await self._handle_business_opportunities(dummy_query)
            if biz_resp.success and biz_resp.data:
                # Find someone who needs exit planning
                for opp in biz_resp.data:
                    if "Exit Planning" in opp["opportunities"]:
                        case_title = f"Business Exit Planning - {opp['client_name']}"
                        # Check duplication
                        existing = self.supabase.table("cases").select("id").eq("title", case_title).eq("status", "ACTIVE").execute()
                        if not existing.data:
                            await self._create_case(case_title, opp["client_id"], "Strategic planning for business exit and retirement.")
                            actions_taken.append({
                                "action": "CASE_CREATED",
                                "description": f"Pro-actively created case: {case_title}",
                                "client_id": opp["client_id"]
                            })
                            break # Only one per simulation run to avoid spam
        
        # 4. Check Stale Cases (Pro-active follow up)
        stale_actions = await self._handle_stale_cases(simulated_now=now)
        if stale_actions:
            actions_taken.extend(stale_actions)

        # 5. Process Meeting Transcripts (Auto-create cases/tasks)
        meeting_actions = await self._process_meeting_transcripts(simulated_now=now)
        if meeting_actions:
            actions_taken.extend(meeting_actions)

        return actions_taken

    async def _process_meeting_transcripts(self, simulated_now: datetime) -> List[Dict[str, Any]]:
        """Find unprocessed completed meetings and auto-create cases/tasks from transcripts."""
        actions = []
        try:
            # Fetch completed meetings with transcripts that haven't been processed
            # We use audit_logs as a way to track if we've processed this before
            meetings = self.supabase.table("meetings").select("id, title, transcript, client_id, clients(name)").eq("status", "COMPLETED").not_.is_("transcript", "null").execute().data or []
            
            for meeting in meetings:
                # Check if already processed
                processed = self.supabase.table("audit_logs").select("id").eq("action", "MEETING_PROCESSED").eq("metadata->meeting_id", meeting["id"]).execute().data
                if processed: continue
                
                transcript = meeting.get("transcript")
                if not transcript or len(transcript) < 50: continue
                
                logger.info(f"Processing transcript for meeting {meeting['id']}: {meeting['title']}")
                
                # Use LLM to extract actions and cases
                prompt = f"""Analyze the following meeting transcript between a financial advisor and client {meeting['clients']['name']}.
                
Meeting Transcript:
{transcript}

Extract:
1. ACTION_ITEMS: List specific tasks for the advisor (e.g., "Draft pension review", "Send ISA forms").
2. BUSINESS_OPPORTUNITIES: List new areas of work (e.g., "Inheritance Tax planning", "Mortgage refinancing").

Respond in JSON format:
{{"tasks": ["...", "..."], "cases": ["...", "..."]}}
"""
                import json
                analysis_str = self.llm.generate_completion(prompt)
                try:
                    # Look for JSON in the response
                    json_match = re.search(r"\{.*\}", analysis_str, re.DOTALL)
                    if json_match:
                        analysis = json.loads(json_match.group(0))
                    else:
                        analysis = {"tasks": [], "cases": []}
                except:
                    analysis = {"tasks": [], "cases": []}
                
                # Create Tasks
                for task_title in analysis.get("tasks", []):
                    await self._create_action(task_title, meeting["client_id"], "MEDIUM", simulated_now=simulated_now)
                    actions.append({"action": "TASK_CREATED", "description": f"Auto-created from meeting: {task_title}", "client_id": meeting["client_id"]})
                
                # Create Cases
                for case_title in analysis.get("cases", []):
                    # Check if similar case exists
                    existing = self.supabase.table("cases").select("id").eq("client_id", meeting["client_id"]).ilike("title", f"%{case_title}%").execute().data
                    if not existing:
                        self.supabase.table("cases").insert({
                            "client_id": meeting["client_id"],
                            "title": case_title,
                            "status": "ACTIVE",
                            "priority": "HIGH",
                            "created_at": simulated_now.isoformat(),
                            "updated_at": simulated_now.isoformat()
                        }).execute()
                        actions.append({"action": "CASE_CREATED", "description": f"Auto-created case: {case_title}", "client_id": meeting["client_id"]})

                # Mark as processed
                self.supabase.table("audit_logs").insert({
                    "action": "MEETING_PROCESSED",
                    "reason": f"Processed transcript for: {meeting['title']}",
                    "actor": "AGENT",
                    "metadata": {"meeting_id": meeting["id"]},
                    "created_at": simulated_now.isoformat()
                }).execute()
                
        except Exception as e:
            if "column meetings.transcript does not exist" in str(e) or "42703" in str(e):
                 logger.warning(f"Skipping transcript processing: 'transcript' column missing in meetings table.")
            else:
                 logger.error(f"Error processing meeting transcripts: {e}")
            
        return actions

    async def _create_action(self, title: str, client_id: str, priority: str, simulated_now: datetime = None):
        """Helper to create action item directly."""
        now = simulated_now or datetime.now()
        try:
            self.supabase.table("action_items").insert({
                "title": title,
                "client_id": client_id,
                "priority": priority,
                "status": "PENDING",
                "owner": "ADVISOR",
                "source_type": "AGENT_PROACTIVE",
                "created_at": now.isoformat()
            }).execute()
        except Exception as e:
            logger.error(f"Failed to create action: {e}")

    async def _create_case(self, title: str, client_id: str, description: str, simulated_now: datetime = None):
        """Helper to create case directly."""
        now = simulated_now or datetime.now()
        try:
            res = self.supabase.table("cases").insert({
                "client_id": client_id,
                "advisor_id": "4102483b-7bc3-4152-8855-761cfab45329",
                "title": title,
                "description": description,
                "status": "ACTIVE",
                "created_at": now.isoformat()
            }).execute()
            
            if res.data:
                case_id = res.data[0]["id"]
                # Also create a task for the advisor to start the case
                await self._create_action(f"Initial Review: {title}", client_id, "MEDIUM", simulated_now=now)
        except Exception as e:
            logger.error(f"Failed to create case: {e}")

    async def _send_email(self, to_name: str, to_email: str, subject: str, body: str, client_id: str = None, simulated_now: datetime = None):
        """Helper to simulate sending email."""
        now = simulated_now or datetime.now()
        try:
            # 1. Draft/Sent record
            self.supabase.table("email_drafts").insert({
                "client_id": client_id,
                "to_email": to_email,
                "to_name": to_name,
                "subject": subject,
                "body": body,
                "status": "SENT",
                "sent_at": now.isoformat(),
                "context_type": "AUTOMATION"
            }).execute()
            
            # 2. Audit Log
            self.supabase.table("audit_logs").insert({
                "action": "EMAIL_SENT",
                "actor": "AGENT",
                "reason": f"Automated email to {to_name}: {subject}"
            }).execute()
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

    async def _handle_stale_cases(self, simulated_now: datetime) -> List[Dict[str, Any]]:
        """Identify cases with no updates for 7+ days and send follow-ups."""
        actions = []
        cutoff = simulated_now - timedelta(days=7)
        
        try:
            # Fetch active cases with client info
            res = self.supabase.table("cases").select("id, title, updated_at, client_id, clients(name, email)").eq("status", "ACTIVE").lt("updated_at", cutoff.isoformat()).execute()
            
            for case in (res.data or []):
                client = case.get("clients", {})
                if not client: continue
                
                subject = f"Following up on your {case['title']}"
                body = f"Hi {client['name']},\n\nI'm just following up on our active case regarding '{case['title']}'. We haven't had any updates recently, so I wanted to check if you had any questions or if there's anything you're waiting on from my side.\n\nBest regards,\nYour Financial Advisor"
                
                # Check if we already sent a follow up recently for THIS case
                # (Audit log check)
                logs = self.supabase.table("audit_logs").select("id").eq("case_id", case["id"]).eq("action", "EMAIL_SENT").gte("created_at", cutoff.isoformat()).execute()
                
                if not logs.data:
                    await self._send_email(client["name"], client.get("email", "client@example.com"), subject, body, case["client_id"], simulated_now=simulated_now)
                    
                    # Update case updated_at so we don't spam tomorrow
                    self.supabase.table("cases").update({"updated_at": simulated_now.isoformat()}).eq("id", case["id"]).execute()
                    
                    actions.append({
                        "action": "EMAIL_SENT",
                        "description": f"Pro-active follow-up sent for case: {case['title']}",
                        "client_id": case["client_id"],
                        "case_id": case["id"]
                    })
        except Exception as e:
            logger.error(f"Error in _handle_stale_cases: {e}")
            
        return actions

