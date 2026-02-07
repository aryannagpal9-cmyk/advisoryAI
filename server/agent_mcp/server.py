from fastmcp import FastMCP
from db.supabase import get_supabase
from services.llm_service import GroqService
from typing import List, Optional
from datetime import datetime

# Import new tools
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
    get_open_actions
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

# Initialize FastMCP Server
mcp = FastMCP("Agentic Chaser")
groq_service = GroqService()

# --- REGISTER NEW TOOLS ---

# Investment Tools
mcp.tool()(get_equity_underweight_clients)
mcp.tool()(get_isa_allowance_clients)
mcp.tool()(get_pension_allowance_clients)
mcp.tool()(get_cash_excess_clients)
mcp.tool()(get_protection_gap_clients)
mcp.tool()(get_high_withdrawal_clients)
mcp.tool()(model_market_correction)
mcp.tool()(model_retirement_trajectory)
mcp.tool()(model_interest_rate_impact)

# Compliance Tools
mcp.tool()(get_pending_documents)
mcp.tool()(get_recommendation_history)
mcp.tool()(search_exact_wording_risk)
mcp.tool()(get_sustainable_investing_summary)
mcp.tool()(get_promises_made)

# Analytics Tools
mcp.tool()(get_monthly_client_concerns)
mcp.tool()(get_book_segmentation)
mcp.tool()(get_referral_conversion_rates)
mcp.tool()(get_revenue_vs_service_time)
mcp.tool()(get_recommendation_pushback_analysis)
mcp.tool()(get_overdue_review_clients)
mcp.tool()(get_upcoming_birthdays)
mcp.tool()(get_estate_planning_gaps)
mcp.tool()(get_business_owners_rd_tax)
mcp.tool()(get_education_planning_gaps)
mcp.tool()(find_similar_client_profiles)

# Action Tools
mcp.tool()(create_task)
mcp.tool()(create_case)
mcp.tool()(create_draft_email)
mcp.tool()(get_open_actions)

# Search Tools
mcp.tool()(search_clients)
mcp.tool()(get_client_profile)

# Follow-up Tools
mcp.tool()(draft_meeting_followup_email)
mcp.tool()(get_clients_waiting_on_info)
mcp.tool()(get_overdue_followups)
mcp.tool()(get_similar_value_add_cases)
mcp.tool()(get_implementation_triggers)

@mcp.tool()
async def search_cases(query: str) -> List[dict]:
    """
    Search for cases by client name or title.
    """
    supabase = get_supabase()
    # Perform a text search on title or client name
    res = supabase.table("cases").select("*, clients(name)").execute()
    
    results = []
    for c in res.data:
        client_name = c["clients"]["name"] if c.get("clients") else ""
        if query.lower() in c["title"].lower() or query.lower() in client_name.lower():
            results.append({
                "id": c["id"],
                "client": client_name,
                "title": c["title"],
                "status": c["status"]
            })
    return results

@mcp.tool()
async def get_case_status(case_id: str) -> dict:
    """
    Get the status of a specific case and its outstanding requests.
    """
    supabase = get_supabase()
    case_res = supabase.table("cases").select("*, clients(name)").eq("id", case_id).single().execute()
    req_res = supabase.table("requests").select("*").eq("case_id", case_id).execute()
    
    case = case_res.data
    requests = req_res.data
    
    return {
        "case_title": case["title"],
        "client": case["clients"]["name"],
        "status": case["status"],
        "outstanding_requests": [
            {"title": r["title"], "status": r["status"], "owner": r["owner_type"]}
            for r in requests if r["status"] not in ["FULFILLED", "CLOSED"]
        ]
    }

@mcp.tool()
async def draft_chaser_email(case_id: str, tone: str = "formal") -> str:
    """
    Draft a chasing email for the case using the LLM.
    tone: 'formal' or 'urgent' or 'empathetic'
    """
    # 1. Fetch Case Context
    status_data = await get_case_status(case_id)
    
    # 2. Use LLM to generate email
    requests_str = "\n".join([f"- {r['title']} ({r['status']})" for r in status_data['outstanding_requests']])
    
    prompt = f"""
    You are an expert financial advisor assistant.
    Draft a {tone} email to the provider/client for the case: '{status_data['case_title']}' for client {status_data['client']}.
    
    Outstanding items:
    {requests_str}
    
    The email should be concise and professional.
    """
    return await groq_service.generate_completion(prompt)



@mcp.tool()
async def schedule_meeting(client_id: str, meeting_type: str, date_str: str, notes: str = "") -> str:
    """
    Schedule a meeting for a client.
    meeting_type: 'INITIAL_CONSULTATION', 'ANNUAL_REVIEW', 'AD_HOC', 'PHONE_CALL'
    date_str: ISO 8601 string (e.g. '2024-11-01T10:00:00')
    """
    supabase = get_supabase()
    
    try:
        res = supabase.table("meetings").insert({
            "client_id": client_id,
            "meeting_type": meeting_type.upper(),
            "scheduled_at": date_str,
            "status": "SCHEDULED",
            "notes": notes
        }).execute()
        
        if res.data:
            return f"Meeting scheduled: {meeting_type} on {date_str}"
        return "Failed to schedule meeting"
    except Exception as e:
        return f"Error scheduling meeting: {str(e)}"

@mcp.tool()
async def send_email(to_email: str, subject: str, body: str, client_id: Optional[str] = None) -> str:
    """
    Simulate sending an email to a client or provider.
    """
    supabase = get_supabase()
    
    try:
        # 1. Create record in email_drafts (as SENT)
        draft_data = {
            "to_email": to_email,
            "subject": subject,
            "body": body,
            "status": "SENT",
            "sent_at": datetime.now().isoformat()
        }
        if client_id:
            draft_data["client_id"] = client_id
            
        supabase.table("email_drafts").insert(draft_data).execute()
        
        # 2. Log to Audit Logs
        log_data = {
            "action": "EMAIL_SENT",
            "actor": "AGENT",
            "reason": f"Email sent to {to_email}: {subject}"
        }
        if client_id:
            # We need a case_id for audit logs usually, but let's check schema. 
            pass 
            
        supabase.table("audit_logs").insert(log_data).execute()
        
        return f"Email sent to {to_email}"
    except Exception as e:
        return f"Error sending email: {str(e)}"
