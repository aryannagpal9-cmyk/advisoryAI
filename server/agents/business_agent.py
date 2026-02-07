"""
Business Agent
Handles business analytics queries about practice management and client insights.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import Counter

from .base import BaseAgent, AgentType, QueryIntent, AgentQuery, AgentResponse
from services.logging_service import get_logger

logger = get_logger(__name__)


class BusinessAgent(BaseAgent):
    """Agent for business analytics and practice management queries."""
    
    @property
    def agent_type(self) -> AgentType:
        return AgentType.BUSINESS
    
    @property
    def supported_intents(self) -> List[QueryIntent]:
        return [
            QueryIntent.CLIENT_CONCERNS,
            QueryIntent.SERVICE_UTILIZATION,
            QueryIntent.CONVERSION_RATES,
            QueryIntent.RETIREMENT_BOOK,
            QueryIntent.REVENUE_ANALYSIS,
            QueryIntent.SATISFIED_CLIENTS,
            QueryIntent.RECOMMENDATION_PUSHBACK,
            QueryIntent.VALUE_ADDED,
            QueryIntent.LIFE_EVENT_TRIGGERS,
        ]
    
    async def process(self, query: AgentQuery) -> AgentResponse:
        """Route to specific handler based on intent."""
        handlers = {
            QueryIntent.CLIENT_CONCERNS: self._handle_client_concerns,
            QueryIntent.RETIREMENT_BOOK: self._handle_retirement_book,
            QueryIntent.REVENUE_ANALYSIS: self._handle_revenue_analysis,
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
    
    async def _handle_client_concerns(self, query: AgentQuery) -> AgentResponse:
        """Aggregate concerns raised by clients in meetings this month."""
        # Get meetings from this month
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        meetings = self.supabase.table("meetings").select(
            "id, client_concerns, notes, clients(name)"
        ).gte("scheduled_at", start_of_month.isoformat()).execute().data or []
        
        # Aggregate concerns
        all_concerns = []
        for meeting in meetings:
            concerns = meeting.get("client_concerns") or []
            client_name = meeting.get("clients", {}).get("name", "Unknown")
            for concern in concerns:
                all_concerns.append({
                    "concern": str(concern),
                    "client": client_name
                })
        
        # Count and categorize
        concern_counter = Counter(c["concern"].lower() for c in all_concerns)
        
        message = f"**Client concerns this month ({len(all_concerns)} total):**\n\n"
        
        if concern_counter:
            for concern, count in concern_counter.most_common(10):
                message += f"• **{concern.title()}**: mentioned {count} time(s)\n"
        else:
            message = "No client concerns recorded in meetings this month."
        
        return AgentResponse(
            success=True,
            data={"concerns": all_concerns, "summary": dict(concern_counter)},
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            follow_up_suggestions=[
                "Show clients who mentioned volatility",
                "How should I address these concerns?"
            ]
        )
    
    async def _handle_retirement_book(self, query: AgentQuery) -> AgentResponse:
        """Show percentage of book approaching retirement in next 5 years."""
        # Get all client profiles with time horizon
        profiles = self.supabase.table("client_profiles").select(
            "client_id, time_horizon_years, retirement_target_age, clients(name)"
        ).execute().data or []
        
        total_clients = len(profiles)
        approaching_retirement = []
        
        for profile in profiles:
            time_horizon = profile.get("time_horizon_years", 100) or 100
            
            if time_horizon <= 5:
                client_info = profile.get("clients", {})
                approaching_retirement.append({
                    "client_id": profile.get("client_id"),
                    "client_name": client_info.get("name", "Unknown"),
                    "years_to_retirement": time_horizon,
                    "target_age": profile.get("retirement_target_age")
                })
        
        # Sort by nearest retirement
        approaching_retirement.sort(key=lambda x: x["years_to_retirement"])
        
        percentage = (len(approaching_retirement) / total_clients * 100) if total_clients > 0 else 0
        
        message = f"**{percentage:.1f}% of your book** ({len(approaching_retirement)}/{total_clients} clients) approaching retirement in next 5 years:\n\n"
        
        for client in approaching_retirement[:10]:
            message += f"• **{client['client_name']}**: {client['years_to_retirement']} years (targeting age {client['target_age']})\n"
        
        return AgentResponse(
            success=True,
            data=approaching_retirement,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            metadata={
                "percentage": round(percentage, 1),
                "count": len(approaching_retirement),
                "total": total_clients
            },
            follow_up_suggestions=[
                "Which need at-retirement reviews?",
                "Show their retirement income projections"
            ]
        )
    
    async def _handle_revenue_analysis(self, query: AgentQuery) -> AgentResponse:
        """Analyze which clients generate most revenue (by AUM as proxy)."""
        # Get investments aggregated by client
        investments = self.supabase.table("investments").select(
            "client_id, current_value, clients(name)"
        ).execute().data or []
        
        # Aggregate by client
        client_aum = {}
        for inv in investments:
            client_id = inv.get("client_id")
            if client_id not in client_aum:
                client_aum[client_id] = {
                    "name": inv.get("clients", {}).get("name", "Unknown"),
                    "total_aum": 0
                }
            client_aum[client_id]["total_aum"] += inv.get("current_value", 0) or 0
        
        # Convert to list and sort
        results = [
            {
                "client_id": cid,
                "client_name": data["name"],
                "aum": data["total_aum"],
                "estimated_annual_revenue": data["total_aum"] * 0.01  # Assume 1% fee
            }
            for cid, data in client_aum.items()
        ]
        results.sort(key=lambda x: x["aum"], reverse=True)
        
        total_aum = sum(r["aum"] for r in results)
        
        message = f"**Client Revenue Analysis** (Total AUM: £{total_aum:,.0f}):\n\n"
        message += "**Top 10 by AUM:**\n"
        for r in results[:10]:
            pct = (r["aum"] / total_aum * 100) if total_aum > 0 else 0
            message += f"• **{r['client_name']}**: £{r['aum']:,.0f} ({pct:.1f}% of book)\n"
        
        # Pareto analysis
        top_20_pct_count = max(1, len(results) // 5)
        top_20_pct_aum = sum(r["aum"] for r in results[:top_20_pct_count])
        pareto = (top_20_pct_aum / total_aum * 100) if total_aum > 0 else 0
        
        message += f"\n📊 *Top 20% of clients represent {pareto:.0f}% of AUM*"
        
        return AgentResponse(
            success=True,
            data=results,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            metadata={"total_aum": total_aum, "pareto_ratio": pareto}
        )
