from typing import Dict, Any, List
from datetime import datetime, timedelta
from db.supabase import get_supabase

async def draft_meeting_followup_email(client_name: str) -> Dict[str, Any]:
    """Draft a follow-up email based on the most recent meeting."""
    supabase = get_supabase()
    client = supabase.table("clients").select("id, name").ilike("name", f"%{client_name}%").execute()
    if not client.data:
        return {"error": f"Client '{client_name}' not found"}
        
    meeting = supabase.table("meetings").select(
        "notes, recommendations_made"
    ).eq("client_id", client.data[0]["id"]).order("scheduled_at", desc=True).limit(1).execute()
    
    if not meeting.data:
        return {"error": "No recent meeting found"}
        
    return {
        "client": client.data[0]["name"],
        "notes": meeting.data[0]["notes"],
        "draft": f"Dear {client.data[0]['name']},\n\nIt was great meeting you. Based on our discussion regarding {meeting.data[0]['notes'][:50]}..., I have outlined the next steps..."
    }

draft_meeting_followup_email.tool_schema = {
    "name": "draft_meeting_followup_email",
    "description": "Draft a follow-up email based on the most recent meeting with a client.",
    "parameters": {
        "type": "object",
        "properties": {
            "client_name": {"type": "string", "description": "Name of the client"}
        },
        "required": ["client_name"]
    }
}

async def get_clients_waiting_on_info() -> Dict[str, Any]:
    """Find clients who haven't responded to info/document requests."""
    supabase = get_supabase()
    result = supabase.table("document_requests").select(
        "client_id, document_type, requested_date, clients(name)"
    ).eq("status", "PENDING").execute()
    
    waiting = []
    for r in result.data or []:
        waiting.append({
            "name": r["clients"]["name"],
            "waiting_for": r["document_type"],
            "since": r["requested_date"]
        })
        
    return {"waiting_clients": waiting, "count": len(waiting)}

get_clients_waiting_on_info.tool_schema = {
    "name": "get_clients_waiting_on_info",
    "description": "Find clients who have not yet provided requested documents or info.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def get_overdue_followups() -> Dict[str, Any]:
    """Get overdue follow-ups."""
    supabase = get_supabase()
    today = datetime.now().date().isoformat()
    result = supabase.table("action_items").select(
        "id, title, due_date, priority, clients(name)"
    ).eq("status", "PENDING").lt("due_date", today).execute()
    
    overdue = []
    for a in result.data or []:
        client = a.get("clients", {})
        overdue.append({
            "title": a.get("title"),
            "due": a.get("due_date"),
            "client": client.get("name")
        })
    
    return {"actions": overdue, "count": len(overdue)}

get_overdue_followups.tool_schema = {
    "name": "get_overdue_followups",
    "description": "Get a list of action items that are past their due date.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def get_similar_value_add_cases() -> Dict[str, Any]:
    """Show cases where significant value was added (e.g., tax saved)."""
    supabase = get_supabase()
    result = supabase.table("cases").select(
        "title, notes, clients(name)"
    ).ilike("notes", "%tax saved%").limit(5).execute()
    return {"cases": result.data or []}

get_similar_value_add_cases.tool_schema = {
    "name": "get_similar_value_add_cases",
    "description": "Search for previous cases with documented tax savings or high value added.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def get_implementation_triggers() -> Dict[str, Any]:
    """Analyze what life events trigger recommendation implementation."""
    supabase = get_supabase()
    result = supabase.table("recommendations").select(
        "description, created_at, clients(name)"
    ).eq("status", "IMPLEMENTED").limit(10).execute()
    
    triggers = ["inheritance", "retirement", "redundancy", "marriage", "birth", "sale"]
    found_triggers = []
    for r in result.data or []:
        desc = r.get("description", "").lower()
        for t in triggers:
            if t in desc:
                found_triggers.append({"client": r["clients"]["name"], "trigger": t, "action": r["description"]})
                
    return {"triggers": found_triggers}

get_implementation_triggers.tool_schema = {
    "name": "get_implementation_triggers",
    "description": "Analyze common life events that lead to clients implementing recommendations.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}
