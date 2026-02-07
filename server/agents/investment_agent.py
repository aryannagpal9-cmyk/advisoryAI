"""
Investment Agent
Handles investment-related queries including portfolio analysis, allowances, and projections.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta

from .base import BaseAgent, AgentType, QueryIntent, AgentQuery, AgentResponse
from services.logging_service import get_logger

logger = get_logger(__name__)


class InvestmentAgent(BaseAgent):
    """Agent for investment and portfolio analysis queries."""
    
    @property
    def agent_type(self) -> AgentType:
        return AgentType.INVESTMENT
    
    @property
    def supported_intents(self) -> List[QueryIntent]:
        return [
            QueryIntent.EQUITY_ANALYSIS,
            QueryIntent.ISA_ALLOWANCE,
            QueryIntent.ANNUAL_ALLOWANCE,
            QueryIntent.CASH_EXCESS,
            QueryIntent.RETIREMENT_TRAJECTORY,
            QueryIntent.PROTECTION_GAPS,
            QueryIntent.WITHDRAWAL_RATE,
            QueryIntent.INTEREST_RATE_IMPACT,
            QueryIntent.LONG_TERM_CARE,
            QueryIntent.MARKET_CORRECTION,
            QueryIntent.EARLY_RETIREMENT,
        ]
    
    async def process(self, query: AgentQuery) -> AgentResponse:
        """Route to specific handler based on intent."""
        handlers = {
            QueryIntent.EQUITY_ANALYSIS: self._handle_equity_analysis,
            QueryIntent.ISA_ALLOWANCE: self._handle_isa_allowance,
            QueryIntent.ANNUAL_ALLOWANCE: self._handle_annual_allowance,
            QueryIntent.CASH_EXCESS: self._handle_cash_excess,
            QueryIntent.WITHDRAWAL_RATE: self._handle_withdrawal_rate,
            QueryIntent.PROTECTION_GAPS: self._handle_protection_gaps,
            QueryIntent.MARKET_CORRECTION: self._handle_market_correction,
            QueryIntent.RETIREMENT_TRAJECTORY: self._handle_retirement_trajectory,
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
    
    async def _handle_equity_analysis(self, query: AgentQuery) -> AgentResponse:
        """Find clients underweight in equities relative to risk profile."""
        # Target equity allocations by risk profile
        RISK_TARGETS = {
            'CAUTIOUS': 30,
            'BALANCED': 60,
            'ADVENTUROUS': 80,
            'AGGRESSIVE': 90
        }
        
        # Fetch all client profiles with their investments
        profiles = self.supabase.table("client_profiles").select(
            "*, clients(id, name, email)"
        ).execute().data or []
        
        underweight_clients = []
        
        for profile in profiles:
            client_id = profile.get("client_id")
            risk_profile = profile.get("risk_profile", "BALANCED")
            target_equity = RISK_TARGETS.get(risk_profile, 60)
            time_horizon = profile.get("time_horizon_years", 10)
            
            # Get client investments
            investments = self.supabase.table("investments").select("*").eq(
                "client_id", client_id
            ).execute().data or []
            
            if not investments:
                continue
            
            # Calculate weighted average equity allocation
            total_value = sum(inv.get("current_value", 0) or 0 for inv in investments)
            if total_value == 0:
                continue
                
            weighted_equity = sum(
                (inv.get("current_value", 0) or 0) * (inv.get("equity_allocation", 0) or 0)
                for inv in investments
            ) / total_value
            
            # Check if underweight (more than 10% below target)
            gap = target_equity - weighted_equity
            if gap > 10:
                client_info = profile.get("clients", {})
                underweight_clients.append({
                    "client_id": client_id,
                    "client_name": client_info.get("name", "Unknown"),
                    "risk_profile": risk_profile,
                    "time_horizon_years": time_horizon,
                    "current_equity": round(weighted_equity, 1),
                    "target_equity": target_equity,
                    "gap": round(gap, 1),
                    "total_portfolio_value": round(total_value, 2)
                })
        
        # Sort by gap (largest first)
        underweight_clients.sort(key=lambda x: x["gap"], reverse=True)
        
        if underweight_clients:
            message = f"Found {len(underweight_clients)} client(s) underweight in equities:\n\n"
            for client in underweight_clients[:5]:
                message += f"• **{client['client_name']}** - {client['current_equity']}% equity vs {client['target_equity']}% target ({client['gap']}% gap)\n"
        else:
            message = "No clients are significantly underweight in equities relative to their risk profiles."
        
        return AgentResponse(
            success=True,
            data=underweight_clients,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            metadata={"count": len(underweight_clients)},
            follow_up_suggestions=[
                "Show me their current portfolio breakdown",
                "Which of these have reviews coming up?",
                "Draft an email about rebalancing"
            ]
        )
    
    async def _handle_isa_allowance(self, query: AgentQuery) -> AgentResponse:
        """Find clients with ISA allowance remaining."""
        ISA_LIMIT = 20000  # 2025-26 ISA allowance
        
        profiles = self.supabase.table("client_profiles").select(
            "client_id, isa_allowance_used, tax_year, clients(name, email)"
        ).execute().data or []
        
        results = []
        for profile in profiles:
            used = profile.get("isa_allowance_used", 0) or 0
            remaining = ISA_LIMIT - used
            
            if remaining > 0:
                client_info = profile.get("clients", {})
                results.append({
                    "client_id": profile.get("client_id"),
                    "client_name": client_info.get("name", "Unknown"),
                    "isa_used": used,
                    "isa_remaining": remaining,
                    "tax_year": profile.get("tax_year", "2025-26")
                })
        
        # Sort by remaining (largest first)
        results.sort(key=lambda x: x["isa_remaining"], reverse=True)
        
        message = f"**{len(results)} client(s)** have ISA allowance remaining this tax year:\n\n"
        for r in results[:10]:
            message += f"• **{r['client_name']}**: £{r['isa_remaining']:,.0f} remaining (£{r['isa_used']:,.0f} used)\n"
        
        return AgentResponse(
            success=True,
            data=results,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            metadata={"total_unused": sum(r["isa_remaining"] for r in results)},
            follow_up_suggestions=[
                "Which of these have excess cash to invest?",
                "Show me clients approaching tax year end"
            ]
        )
    
    async def _handle_annual_allowance(self, query: AgentQuery) -> AgentResponse:
        """Find clients with pension annual allowance remaining."""
        AA_LIMIT = 60000  # Standard annual allowance
        
        profiles = self.supabase.table("client_profiles").select(
            "client_id, annual_allowance_used, annual_income, tax_year, clients(name)"
        ).execute().data or []
        
        results = []
        for profile in profiles:
            # Tapered AA for high earners (simplified)
            income = profile.get("annual_income", 0) or 0
            if income > 260000:
                limit = max(10000, AA_LIMIT - (income - 260000) / 2)
            else:
                limit = AA_LIMIT
            
            used = profile.get("annual_allowance_used", 0) or 0
            remaining = limit - used
            
            if remaining > 0:
                client_info = profile.get("clients", {})
                results.append({
                    "client_id": profile.get("client_id"),
                    "client_name": client_info.get("name", "Unknown"),
                    "aa_limit": limit,
                    "aa_used": used,
                    "aa_remaining": remaining
                })
        
        results.sort(key=lambda x: x["aa_remaining"], reverse=True)
        
        message = f"**{len(results)} client(s)** have annual allowance remaining:\n\n"
        for r in results[:10]:
            message += f"• **{r['client_name']}**: £{r['aa_remaining']:,.0f} remaining\n"
        
        return AgentResponse(
            success=True,
            data=results,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent
        )
    
    async def _handle_cash_excess(self, query: AgentQuery) -> AgentResponse:
        """Find clients with cash above 6 months expenditure."""
        profiles = self.supabase.table("client_profiles").select(
            "client_id, cash_reserves, monthly_expenditure, emergency_fund_months, clients(name)"
        ).execute().data or []
        
        results = []
        for profile in profiles:
            cash = profile.get("cash_reserves", 0) or 0
            monthly_exp = profile.get("monthly_expenditure", 0) or 0
            buffer_months = profile.get("emergency_fund_months", 6) or 6
            
            if monthly_exp == 0:
                continue
            
            required_buffer = monthly_exp * buffer_months
            excess = cash - required_buffer
            
            if excess > 5000:  # Only flag if excess > £5k
                client_info = profile.get("clients", {})
                results.append({
                    "client_id": profile.get("client_id"),
                    "client_name": client_info.get("name", "Unknown"),
                    "cash_reserves": cash,
                    "required_buffer": required_buffer,
                    "excess_cash": excess
                })
        
        results.sort(key=lambda x: x["excess_cash"], reverse=True)
        
        message = f"**{len(results)} client(s)** have excess cash above emergency buffer:\n\n"
        for r in results[:10]:
            message += f"• **{r['client_name']}**: £{r['excess_cash']:,.0f} excess (£{r['cash_reserves']:,.0f} total, £{r['required_buffer']:,.0f} needed)\n"
        
        total_excess = sum(r["excess_cash"] for r in results)
        
        return AgentResponse(
            success=True,
            data=results,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            metadata={"total_excess": total_excess},
            follow_up_suggestions=[
                "Which have ISA allowance remaining?",
                "Show pension contribution options"
            ]
        )
    
    async def _handle_withdrawal_rate(self, query: AgentQuery) -> AgentResponse:
        """Find retired clients with withdrawal rates above 4%."""
        SUSTAINABLE_RATE = 4.0
        
        # Get investments with active drawdown
        investments = self.supabase.table("investments").select(
            "*, clients(id, name)"
        ).eq("drawdown_active", True).execute().data or []
        
        results = []
        seen_clients = set()
        
        for inv in investments:
            client_id = inv.get("clients", {}).get("id")
            if client_id in seen_clients:
                continue
            
            withdrawal_rate = inv.get("withdrawal_rate", 0) or 0
            if withdrawal_rate > SUSTAINABLE_RATE:
                seen_clients.add(client_id)
                results.append({
                    "client_id": client_id,
                    "client_name": inv.get("clients", {}).get("name", "Unknown"),
                    "withdrawal_rate": withdrawal_rate,
                    "fund_value": inv.get("current_value", 0),
                    "annual_withdrawal": inv.get("annual_withdrawal", 0),
                    "gap_from_sustainable": round(withdrawal_rate - SUSTAINABLE_RATE, 2)
                })
        
        results.sort(key=lambda x: x["withdrawal_rate"], reverse=True)
        
        message = f"**{len(results)} retired client(s)** taking more than {SUSTAINABLE_RATE}% withdrawal:\n\n"
        for r in results:
            message += f"• **{r['client_name']}**: {r['withdrawal_rate']}% withdrawal rate (£{r['fund_value']:,.0f} fund)\n"
        
        return AgentResponse(
            success=True,
            data=results,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            follow_up_suggestions=[
                "Show their income sources",
                "What happens if markets drop 20%?"
            ]
        )
    
    async def _handle_protection_gaps(self, query: AgentQuery) -> AgentResponse:
        """Find clients with protection gaps based on family circumstances."""
        # Get clients with dependents or mortgages
        profiles = self.supabase.table("client_profiles").select(
            "client_id, dependents, has_children, marital_status, annual_income, clients(name)"
        ).gt("dependents", 0).execute().data or []
        
        # Also get those married
        married_profiles = self.supabase.table("client_profiles").select(
            "client_id, dependents, has_children, marital_status, annual_income, clients(name)"
        ).eq("marital_status", "MARRIED").execute().data or []
        
        # Combine and dedupe
        all_relevant = {p["client_id"]: p for p in profiles + married_profiles}
        
        results = []
        for client_id, profile in all_relevant.items():
            # Check for protection policies
            policies = self.supabase.table("protection_policies").select("*").eq(
                "client_id", client_id
            ).eq("is_active", True).execute().data or []
            
            has_life = any(p["type"] in ["TERM_LIFE", "WHOLE_OF_LIFE"] for p in policies)
            has_critical = any(p["type"] == "CRITICAL_ILLNESS" for p in policies)
            has_income = any(p["type"] == "INCOME_PROTECTION" for p in policies)
            
            gaps = []
            if not has_life and (profile.get("dependents", 0) > 0 or profile.get("marital_status") == "MARRIED"):
                gaps.append("Life insurance")
            if not has_income and profile.get("annual_income", 0) > 50000:
                gaps.append("Income protection")
            
            if gaps:
                client_info = profile.get("clients", {})
                results.append({
                    "client_id": client_id,
                    "client_name": client_info.get("name", "Unknown"),
                    "dependents": profile.get("dependents", 0),
                    "income": profile.get("annual_income", 0),
                    "missing_protection": gaps
                })
        
        message = f"**{len(results)} client(s)** have protection gaps:\n\n"
        for r in results[:10]:
            gaps_str = ", ".join(r["missing_protection"])
            message += f"• **{r['client_name']}** ({r['dependents']} dependents): Missing {gaps_str}\n"
        
        return AgentResponse(
            success=True,
            data=results,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            follow_up_suggestions=[
                "Get quotes for these clients",
                "Which have reviews coming up?"
            ]
        )
    
    async def _handle_market_correction(self, query: AgentQuery) -> AgentResponse:
        """Model impact of 20% market correction on clients."""
        # Get all investments
        investments = self.supabase.table("investments").select(
            "client_id, current_value, equity_allocation, clients(name)"
        ).execute().data or []
        
        # Aggregate by client
        client_portfolios = {}
        for inv in investments:
            client_id = inv.get("client_id")
            if client_id not in client_portfolios:
                client_portfolios[client_id] = {
                    "name": inv.get("clients", {}).get("name", "Unknown"),
                    "total_value": 0,
                    "equity_value": 0
                }
            
            value = inv.get("current_value", 0) or 0
            equity_pct = (inv.get("equity_allocation", 0) or 0) / 100
            
            client_portfolios[client_id]["total_value"] += value
            client_portfolios[client_id]["equity_value"] += value * equity_pct
        
        # Calculate 20% correction impact
        results = []
        for client_id, portfolio in client_portfolios.items():
            equity_loss = portfolio["equity_value"] * 0.20
            new_total = portfolio["total_value"] - equity_loss
            pct_loss = (equity_loss / portfolio["total_value"] * 100) if portfolio["total_value"] > 0 else 0
            
            if equity_loss > 10000:  # Only show significant impacts
                results.append({
                    "client_id": client_id,
                    "client_name": portfolio["name"],
                    "current_value": portfolio["total_value"],
                    "equity_exposure": portfolio["equity_value"],
                    "potential_loss": equity_loss,
                    "new_value": new_total,
                    "percentage_impact": round(pct_loss, 1)
                })
        
        results.sort(key=lambda x: x["potential_loss"], reverse=True)
        
        message = "**20% Market Correction Impact Analysis:**\n\n"
        for r in results[:10]:
            message += f"• **{r['client_name']}**: -£{r['potential_loss']:,.0f} ({r['percentage_impact']}% of portfolio)\n"
        
        total_at_risk = sum(r["potential_loss"] for r in results)
        
        return AgentResponse(
            success=True,
            data=results,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent,
            metadata={"total_at_risk": total_at_risk}
        )
    
    async def _handle_retirement_trajectory(self, query: AgentQuery) -> AgentResponse:
        """Flag clients whose trajectory won't meet retirement goals."""
        profiles = self.supabase.table("client_profiles").select(
            "*, clients(name)"
        ).not_.is_("retirement_income_goal", "null").execute().data or []
        
        results = []
        for profile in profiles:
            client_id = profile.get("client_id")
            goal = profile.get("retirement_income_goal", 0) or 0
            target_age = profile.get("retirement_target_age", 65) or 65
            time_horizon = profile.get("time_horizon_years", 10) or 10
            
            # Get current portfolio
            investments = self.supabase.table("investments").select(
                "current_value, annual_contribution"
            ).eq("client_id", client_id).execute().data or []
            
            current_fund = sum(inv.get("current_value", 0) or 0 for inv in investments)
            annual_contrib = sum(inv.get("annual_contribution", 0) or 0 for inv in investments)
            
            # Simple projection: 5% growth, 4% withdrawal
            projected_fund = current_fund
            for year in range(time_horizon):
                projected_fund = (projected_fund + annual_contrib) * 1.05
            
            sustainable_income = projected_fund * 0.04
            shortfall = goal - sustainable_income
            
            if shortfall > 5000:
                results.append({
                    "client_id": client_id,
                    "client_name": profile.get("clients", {}).get("name", "Unknown"),
                    "income_goal": goal,
                    "projected_income": round(sustainable_income, 0),
                    "shortfall": round(shortfall, 0),
                    "years_to_retirement": time_horizon,
                    "current_fund": current_fund
                })
        
        results.sort(key=lambda x: x["shortfall"], reverse=True)
        
        message = f"**{len(results)} client(s)** projected to miss retirement income goals:\n\n"
        for r in results[:10]:
            message += f"• **{r['client_name']}**: £{r['shortfall']:,.0f}/yr shortfall (needs £{r['income_goal']:,.0f}, projected £{r['projected_income']:,.0f})\n"
        
        return AgentResponse(
            success=True,
            data=results,
            message=message,
            agent_type=self.agent_type,
            query_type=query.intent
        )
    
    async def generate_all_insights(self) -> List[Dict[str, Any]]:
        """Generate investment-related insights proactively."""
        insights = []
        
        # Run each analysis and create insights
        dummy_query = AgentQuery(raw_query="", intent=QueryIntent.EQUITY_ANALYSIS, entities={}, context={})
        
        equity_response = await self._handle_equity_analysis(dummy_query)
        for client in (equity_response.data or [])[:3]:
            insights.append({
                "category": "INVESTMENT",
                "title": "Portfolio Underweight in Equities",
                "description": f"{client['client_name']}'s portfolio is at {client['current_equity']}% equities vs {client['target_equity']}% target.",
                "client_id": client["client_id"],
                "priority": "MEDIUM",
                "metrics": {"gap": client["gap"]}
            })
        
        return insights
