import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from services.logging_service import get_logger
from services.llm_service import GroqService
from datetime import datetime, timedelta, timezone

# Import modularized tools
from agent_mcp.tools.investments import (
    get_equity_underweight_clients,
    get_isa_allowance_clients,
    get_pension_allowance_clients,
    get_cash_excess_clients,
    get_protection_gap_clients,
    get_high_withdrawal_clients,
    model_market_correction,
    model_retirement_trajectory,
    model_interest_rate_impact
)
from agent_mcp.tools.compliance import (
    get_pending_documents,
    get_recommendation_history,
    search_exact_wording_risk,
    get_sustainable_investing_summary,
    get_promises_made
)
from agent_mcp.tools.analytics import (
    get_monthly_client_concerns,
    get_book_segmentation,
    get_referral_conversion_rates,
    get_revenue_vs_service_time,
    get_recommendation_pushback_analysis,
    get_overdue_review_clients,
    get_upcoming_birthdays,
    get_estate_planning_gaps,
    get_business_owners_rd_tax,
    get_education_planning_gaps,
    find_similar_client_profiles
)
from agent_mcp.tools.actions import (
    create_task,
    create_case,
    create_draft_email,
    get_open_actions,
    schedule_meeting
)
from agent_mcp.tools.search import (
    search_clients,
    get_client_profile
)
from agent_mcp.tools.followups import (
    draft_meeting_followup_email,
    get_clients_waiting_on_info,
    get_overdue_followups,
    get_similar_value_add_cases,
    get_implementation_triggers
)
# We also need these from server.py or similar if we want to support them
# search_cases, get_case_status, draft_chaser_email are in server.py but not modularized into tools/
# Let's import them from server if possible, or move them. 
# For now, to keep it clean, I will assume we should move them to a 'cases.py' tool or 'email.py'.
# Define Tool Registry
TOOL_REGISTRY = {
    # Investment
    "get_equity_underweight_clients": get_equity_underweight_clients,
    "get_isa_allowance_clients": get_isa_allowance_clients,
    "get_pension_allowance_clients": get_pension_allowance_clients,
    "get_cash_excess_clients": get_cash_excess_clients,
    "get_protection_gap_clients": get_protection_gap_clients,
    "get_high_withdrawal_clients": get_high_withdrawal_clients,
    "model_market_correction": model_market_correction,
    "model_retirement_trajectory": model_retirement_trajectory,
    "model_interest_rate_impact": model_interest_rate_impact,
    
    # Compliance
    "get_pending_documents": get_pending_documents,
    "get_recommendation_history": get_recommendation_history,
    "search_exact_wording_risk": search_exact_wording_risk,
    "get_sustainable_investing_summary": get_sustainable_investing_summary,
    "get_promises_made": get_promises_made,
    
    # Analytics
    "get_monthly_client_concerns": get_monthly_client_concerns,
    "get_book_segmentation": get_book_segmentation,
    "get_referral_conversion_rates": get_referral_conversion_rates,
    "get_revenue_vs_service_time": get_revenue_vs_service_time,
    "get_recommendation_pushback_analysis": get_recommendation_pushback_analysis,
    "get_overdue_review_clients": get_overdue_review_clients,
    "get_upcoming_birthdays": get_upcoming_birthdays,
    "get_estate_planning_gaps": get_estate_planning_gaps,
    "get_business_owners_rd_tax": get_business_owners_rd_tax,
    "get_education_planning_gaps": get_education_planning_gaps,
    "find_similar_client_profiles": find_similar_client_profiles,
    
    # Actions
    "create_task": create_task,
    "create_case": create_case,
    "create_draft_email": create_draft_email,
    "get_open_actions": get_open_actions,
    "schedule_meeting": schedule_meeting,
    
    # Search
    "search_clients": search_clients,
    "get_client_profile": get_client_profile,
    
    # Followups
    "draft_meeting_followup_email": draft_meeting_followup_email,
    "get_clients_waiting_on_info": get_clients_waiting_on_info,
    "get_overdue_followups": get_overdue_followups,
    "get_similar_value_add_cases": get_similar_value_add_cases,
    "get_implementation_triggers": get_implementation_triggers
}

logger = get_logger(__name__)


# ============================================================================
# COMPRESSED TOOL DEFINITIONS (Token Optimized)
# ============================================================================

# Generate TOOLS_COMPACT from TOOL_REGISTRY
TOOLS_COMPACT = [
    {"type": "function", "function": func.tool_schema}
    for func in TOOL_REGISTRY.values() if hasattr(func, 'tool_schema')
]


# ============================================================================
# COMPRESSED SYSTEM PROMPT (Token Optimized)
# ============================================================================

SYSTEM_PROMPT_COMPACT = """You are a world-class financial advisor AI assistant.
Your goal is to provide flawless, proactive, and comprehensive support.
- ALWAYS use tools to back up your answers with real data. 
- If a query is complex, call multiple tools sequentially or in parallel if appropriate.
- Be PROACTIVE: If a user asks about a client, check for allowances, protection gaps, or overdue reviews without being asked.
- SYNTHESIZE: Combine tool results into a smooth, natural language response. No JSON or XML.
- NEVER simulate tool calls in text. Use the provided function calling mechanism."""


# ============================================================================
# TOOL RESULT WITH DB TRACKING
# ============================================================================

@dataclass
class ToolResult:
    """Result from executing a tool."""
    tool_name: str
    success: bool
    data: Any
    error: Optional[str] = None
    db_write: bool = False  # Track if this was a DB write action
    record_id: Optional[str] = None  # ID of created record


# ============================================================================
# TOKEN USAGE TRACKER
# ============================================================================

@dataclass 
class TokenUsage:
    """Track token usage for a request."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    def add(self, prompt: int, completion: int):
        self.prompt_tokens += prompt
        self.completion_tokens += completion
        self.total_tokens = self.prompt_tokens + self.completion_tokens


# ============================================================================
# OPTIMIZED SMART AGENT
# ============================================================================

class SmartAgent:
    """Token-optimized LLM agent for intelligent chat (rate limiting disabled)."""
    
    def __init__(self, supabase, llm_client: GroqService, websocket_manager=None):
        self.supabase = supabase
        self.llm = llm_client
        self.tools = TOOLS_COMPACT # This is the list of tool schemas for the LLM
        self.tool_registry = TOOL_REGISTRY # This maps tool names to actual functions
        self.system_prompt = SYSTEM_PROMPT_COMPACT
        self.ws_manager = websocket_manager
        self._actions_taken = []
        self.token_usage = TokenUsage()
        
        # Use smaller model for simple queries (can be made configurable)
        self.model_fast = "llama-3.1-8b-instant"  # Fast, cheap
        self.model_smart = "llama-3.3-70b-versatile"  # Capable
    
    def _estimate_tokens(self, messages: List[Dict], include_tools: bool = True) -> int:
        """Rough token estimation (4 chars ≈ 1 token)."""
        text = json.dumps(messages)
        if include_tools:
            text += json.dumps(self.tools)
        return len(text) // 4
    
    def _select_model(self, query: str) -> str:
        """Select appropriate model based on query complexity."""
        # Simple queries use fast model
        simple_patterns = ["hello", "hi", "thanks", "ok", "yes", "no", "what can you"]
        if any(p in query.lower() for p in simple_patterns):
            return self.model_fast
        return self.model_smart
    
    async def process_query(
        self, 
        query: str, 
        conversation_history: List[Dict[str, str]] = None,
        max_history: int = 4  # Limit history to save tokens
    ) -> Dict[str, Any]:
        """Process query with token optimization and rate limiting (v2: Multi-turn support)."""
        
        # Build messages with limited history
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if conversation_history:
            recent_history = conversation_history[-max_history:]
            messages.extend(recent_history)
        
        messages.append({"role": "user", "content": query})
        
        all_tools_used = []
        all_db_writes = []
        all_tool_results_data = []
        
        # Sequential/Multi-turn loop (max 10 turns for complex tool chains)
        for turn in range(10):
            # Select model based on complexity (mostly smart model for multi-turn)
            model = self._select_model(query)
            
            # Initial LLM call with tools
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 1000
            }
            # Provide tools on most turns to enable proper chaining
            if turn < 8:
                kwargs["tools"] = self.tools
                kwargs["tool_choice"] = "auto"
            
            response = await self.llm.chat.completions.create(**kwargs)
            
            # Track token usage
            if hasattr(response, 'usage') and response.usage:
                self.token_usage.add(
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens
                )
            
            assistant_message = response.choices[0].message
            # Convert to dict for history to avoid serialization errors
            assistant_msg_dict = {"role": "assistant", "content": assistant_message.content}
            if assistant_message.tool_calls:
                assistant_msg_dict["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                    } for tc in assistant_message.tool_calls
                ]
            messages.append(assistant_msg_dict)
            
            if assistant_message.tool_calls:
                # Execute tool calls
                for tool_call in assistant_message.tool_calls:
                    args = {}
                    if tool_call.function.arguments:
                        try:
                            parsed = json.loads(tool_call.function.arguments)
                            if parsed is not None: args = parsed
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse tool arguments: {tool_call.function.arguments}")
                    
                    result = await self._execute_tool(tool_call.function.name, args)
                    all_tools_used.append(tool_call.function.name)
                    
                    if result.success:
                        all_tool_results_data.append(result.data)
                    
                    # Track DB writes
                    if result.db_write:
                        all_db_writes.append({
                            "action": tool_call.function.name,
                            "record_id": result.record_id,
                            "success": result.success
                        })
                    
                    # Prep result for next turn
                    result_data = result.data if result.success else {"error": result.error}
                    if isinstance(result_data, dict) and "clients" in result_data:
                        clients = result_data.get("clients", [])[:5]
                        result_data = {"clients": clients, "count": result_data.get("count", 0), "truncated": len(clients) < result_data.get("count", 0)}
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result_data)
                    })
                
                # Continue loop to let LLM see results and potentially call more tools
                continue
            else:
                # No more tool calls, we have the final answer
                return {
                    "success": True,
                    "message": assistant_message.content,
                    "tools_used": list(set(all_tools_used)),
                    "data": all_tool_results_data,
                    "db_writes": all_db_writes,
                    "token_usage": {
                        "prompt": self.token_usage.prompt_tokens,
                        "completion": self.token_usage.completion_tokens,
                        "total": self.token_usage.total_tokens
                    }
                }
        
        # If we exit catch-all (max turns)
        return {
            "success": True,
            "message": messages[-1].content if messages and messages[-1].get('content') else "Max tool turns reached.",
            "tools_used": list(set(all_tools_used)),
            "data": all_tool_results_data,
            "db_writes": all_db_writes,
            "token_usage": {"total": self.token_usage.total_tokens}
        }
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Execute a tool and return the result."""
        logger.info(f"Tool: {tool_name} args: {arguments}")
        
        try:
            handler = TOOL_REGISTRY.get(tool_name)
            if handler:
                # Pass supabase client to the tool function
                data = await handler(**arguments)
                # Check if this was a DB write action
                is_db_write = tool_name in ["create_task", "schedule_meeting", "create_case", "create_draft_email"]
                record_id = data.get("id") if isinstance(data, dict) else None
                
                # Broadcast if websocket manager is present
                # Note: The tools themselves don't broadcast in this architecture unless we pass ws_manager to them
                # or handle it here.
                # In the previous monolithic version, _broadcast_action was called inside the tools.
                # Here we can inspect the result and broadcast if needed, or tools should emit events.
                # For now, we will handle broadcasting for key actions here by checking the tool name
                
                if is_db_write and self.ws_manager and isinstance(data, dict) and data.get("created"):
                    try:
                        action_type = "ACTION_TAKEN" # simplified
                        if tool_name == "create_task": action_type = "TASK_CREATED"
                        elif tool_name == "schedule_meeting": action_type = "MEETING_SCHEDULED"
                        elif tool_name == "create_case": action_type = "CASE_CREATED"
                        elif tool_name == "create_draft_email": action_type = "EMAIL_DRAFTED"
                        
                        await self.ws_manager.broadcast({
                            "type": "ACTION_TAKEN",
                            "action": action_type,
                            "data": data,
                            "refresh": ["stats", "actions", "meetings", "cases"]
                        })
                    except Exception as e:
                        logger.error(f"Broadcast failed: {e}")

                return ToolResult(
                    tool_name=tool_name, 
                    success=True, 
                    data=data,
                    db_write=is_db_write,
                    record_id=record_id
                )
            else:
                return ToolResult(tool_name=tool_name, success=False, data=None, error=f"Tool {tool_name} not found")
        except Exception as e:
            logger.error(f"Tool error {tool_name}: {e}")
            return ToolResult(tool_name=tool_name, success=False, data=None, error=str(e))

    async def _trigger_chase(self, request_id: str, simulated_now: datetime = None) -> Dict[str, Any]:
        """
        Trigger a chase for a specific request.
        """
        if not simulated_now:
            simulated_now = datetime.now(timezone.utc)
        
        # 1. Fetch Request
        try:
            req_res = self.supabase.table("requests").select("*, cases(title, clients(id, name, email))").eq("id", request_id).single().execute()
            req = req_res.data
        except Exception as e:
            logger.error(f"Error fetching request {request_id}: {e}")
            return {"success": False, "error": str(e)}

        if not req:
            return {"success": False, "error": "Request not found"}

        case = req.get("cases", {}) or {}
        client = case.get("clients", {}) or {}
        
        # 2. Generate Email Content
        prompt = f"""Draft a polite professional follow-up email to {client.get('name', 'Client')} regarding '{req.get('title')}'.
        Context:
        - Case: {case.get('title')}
        - Item needed: {req.get('title')}
        - Priority: {req.get('priority', 'Standard')}
        
        Keep it concise. Sign off as 'AdvisoryAI Team'."""
        
        email_body = "Draft content unavailable."
        
        try:
            # Check if LLM client is available
            if hasattr(self.llm, "chat"): # It's an AsyncGroq client
                response = await self.llm.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model_fast,
                    temperature=0.7
                )
                email_body = response.choices[0].message.content
            # Fallback handling just in case
            else:
                email_body = f"Dear {client.get('name')},\n\nWe are following up on {req.get('title')}. Please provide this at your earliest convenience.\n\nBest,\nAdvisoryAI Team"
        except Exception as e:
            logger.warning(f"LLM generation failed for chase: {e}")
            email_body = f"Dear {client.get('name')},\n\nWe are following up on {req.get('title')}. Please provide this at your earliest convenience.\n\nBest,\nAdvisoryAI Team"

        # 3. Queue Next Action & Update Status
        retry_count = req.get("retry_count", 0) + 1
        # Simple backoff: 3 days for high, 7 for standard
        days_to_add = 3 if req.get("priority") == "HIGH" else 7
        next_action_at = simulated_now + timedelta(days=days_to_add)

        self.supabase.table("requests").update({
            "retry_count": retry_count,
            "next_action_at": next_action_at.isoformat(),
            "updated_at": simulated_now.isoformat()
        }).eq("id", request_id).execute()

        # 4. Save Draft
        self.supabase.table("email_drafts").insert({
            "client_id": client.get("id"),
            "to_email": client.get("email"),
            "to_name": client.get("name"),
            "subject": f"Follow Up: {req.get('title')}",
            "body": email_body,
            "context_type": "CHASE",
            "context_summary": f"Chase #{retry_count} for {req.get('title')}",
            "sent_at": simulated_now.isoformat(),
            "created_at": simulated_now.isoformat()
        }).execute()

        # 5. Audit Log
        self.supabase.table("audit_logs").insert({
            "case_id": req.get("case_id"),
            "action": "CHASE_SENT", 
            "actor": "AGENT",
            "reason": f"Automated chase #{retry_count} sent for {req.get('title')}",
            "created_at": simulated_now.isoformat()
        }).execute()

        return {"success": True, "action": "CHASE_SENT"}

    def get_actions_taken(self) -> list:
        """Return actions taken this session."""
        return self._actions_taken


# Singleton
_smart_agent = None

def get_smart_agent(supabase, llm_client, websocket_manager=None):
    """Get or create smart agent."""
    global _smart_agent
    if _smart_agent is None:
        _smart_agent = SmartAgent(supabase, llm_client, websocket_manager)
    return _smart_agent

