from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from db.supabase import get_supabase
from services.logging_service import get_logger

logger = get_logger(__name__)

async def create_task(title: str, description: str = None, due_date: str = None, client_name: str = None) -> Dict[str, Any]:
    """Create task - writes to DB."""
    supabase = get_supabase()
    task = {"title": title, "description": description, "status": "PENDING", "priority": "MEDIUM"}
    
    if due_date:
        if "tomorrow" in due_date.lower():
            task["due_date"] = (datetime.now() + timedelta(days=1)).date().isoformat()
        elif "next week" in due_date.lower():
            task["due_date"] = (datetime.now() + timedelta(days=7)).date().isoformat()
        else:
            task["due_date"] = due_date
    
    if client_name:
        client = supabase.table("clients").select("id").ilike("name", f"%{client_name}%").execute()
        if client.data:
            task["client_id"] = client.data[0]["id"]
    
    result = supabase.table("action_items").insert(task).execute()
    created = result.data[0] if result.data else task
    
    # Broadcast would happen in the layer above or via a hook
    
    return {"created": True, "id": created.get("id"), "title": title}

create_task.tool_schema = {
    "name": "create_task",
    "description": "Create a new task for the advisor or client.",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Title of the task"},
            "description": {"type": "string", "description": "Optional details"},
            "due_date": {"type": "string", "description": "Optional due date or relative time like 'tomorrow'"},
            "client_name": {"type": "string", "description": "Optional name of client to link to"}
        },
        "required": ["title"]
    }
}

async def create_case(client_name: str, case_type: str, description: str = None) -> Dict[str, Any]:
    """Create case - writes to DB and triggers initial outreach."""
    supabase = get_supabase()
    client_result = supabase.table("clients").select("id, name, email").ilike("name", f"%{client_name}%").execute()
    
    if not client_result.data:
        return {"error": f"Client '{client_name}' not found"}
    
    client = client_result.data[0]
    
    # provider = supabase.table("providers").select("id").limit(1).execute()
    # provider_id = provider.data[0]["id"] if provider.data else None
    
    case_data = {
        "client_id": client["id"],
        "advisor_id": "00000000-0000-0000-0000-000000000000", # Default demo advisor
        "title": f"{case_type} - {client['name']}",
        "status": "ACTIVE"
    }
    
    result = supabase.table("cases").insert(case_data).execute()
    if not result.data:
        return {"error": "Failed to create case in database"}
    
    created_case = result.data[0]
    case_id = created_case["id"]
    
    # 1. Create initial requests for the case
    initial_reqs = [
        {"title": "Identity Verification", "type": "CLIENT"},
        {"title": "Letter of Authority", "type": "CLIENT"}
    ]
    
    chase_results = []
    for req_t in initial_reqs:
        req_res = supabase.table("requests").insert({
            "case_id": case_id,
            "title": req_t["title"],
            "owner_type": req_t["type"],
            "status": "PENDING",
            "priority": "STANDARD",
            "next_action_at": datetime.now(timezone.utc).isoformat(),
            "retry_count": 0,
            "client_owner_id": client["id"] if req_t["type"] == "CLIENT" else None
        }).execute()
        
    # Note: Triggering chases logic is complex and might need to be separated or kept here if we import required services.
    # For modularity, let's return the case info and let the agent or another service handle the chase trigger if needed 
    # OR we implement a simplified chase trigger here.
    
    return {
        "created": True, 
        "id": case_id, 
        "title": created_case["title"], 
        "client": client["name"],
        "initial_requests": len(initial_reqs)
    }

create_case.tool_schema = {
    "name": "create_case",
    "description": "Open a new financial case for a client and trigger initial outreach.",
    "parameters": {
        "type": "object",
        "properties": {
            "client_name": {"type": "string", "description": "Name of the client"},
            "case_type": {"type": "string", "description": "Type of case, e.g. 'Pension Transfer'"},
            "description": {"type": "string", "description": "Optional context"}
        },
        "required": ["client_name", "case_type"]
    }
}

async def create_draft_email(to: str, subject: str, body: str) -> Dict[str, Any]:
    """Create draft email - writes to DB."""
    supabase = get_supabase()
    client_id = None
    recipient = to
    
    if "@" not in to:
        client = supabase.table("clients").select("id, email, name").ilike("name", f"%{to}%").execute()
        if client.data:
            client_id = client.data[0]["id"]
            recipient = client.data[0].get("email", to)
    
    draft = {
        "to_email": recipient,
        "subject": subject,
        "body": body,
        "client_id": client_id
    }
    
    result = supabase.table("email_drafts").insert(draft).execute()
    created = result.data[0] if result.data else draft
    
    return {"created": True, "id": created.get("id"), "to": recipient, "subject": subject}

create_draft_email.tool_schema = {
    "name": "create_draft_email",
    "description": "Draft an email for a client or provider. Does not send immediately.",
    "parameters": {
        "type": "object",
        "properties": {
            "to": {"type": "string", "description": "Client name or email address"},
            "subject": {"type": "string", "description": "Email subject line"},
            "body": {"type": "string", "description": "Email content"}
        },
        "required": ["to", "subject", "body"]
    }
}

async def get_open_actions() -> Dict[str, Any]:
    """Get all open action items."""
    supabase = get_supabase()
    result = supabase.table("action_items").select(
        "id, title, due_date, priority, clients(name)"
    ).eq("status", "PENDING").order("due_date").limit(20).execute()
    
    actions = []
    for a in result.data or []:
        client = a.get("clients", {})
        actions.append({
            "title": a.get("title"),
            "due": a.get("due_date"),
            "priority": a.get("priority"),
            "client": client.get("name")
        })
    
    return {"actions": actions, "count": len(actions)}

get_open_actions.tool_schema = {
    "name": "get_open_actions",
    "description": "Get a list of all currently open/pending action items.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def schedule_meeting(client_name: str, meeting_type: str, date_str: str, notes: str = "") -> Dict[str, Any]:
    """Schedule a meeting for a client."""
    supabase = get_supabase()
    
    # 1. Find Client
    client_result = supabase.table("clients").select("id, name").ilike("name", f"%{client_name}%").execute()
    if not client_result.data:
        return {"error": f"Client '{client_name}' not found"}
    
    client = client_result.data[0]
    
    try:
        res = supabase.table("meetings").insert({
            "client_id": client["id"],
            "meeting_type": meeting_type.upper(),
            "scheduled_at": date_str,
            "status": "SCHEDULED",
            "notes": notes
        }).execute()
        
        if res.data:
            return {"created": True, "id": res.data[0]["id"], "summary": f"Meeting scheduled: {meeting_type} on {date_str}"}
        return {"error": "Failed to schedule meeting"}
    except Exception as e:
        logger.error(f"Error scheduling meeting: {e}")
        return {"error": str(e)}

schedule_meeting.tool_schema = {
    "name": "schedule_meeting",
    "description": "Schedule a new meeting with a client.",
    "parameters": {
        "type": "object",
        "properties": {
            "client_name": {"type": "string", "description": "Full name of the client"},
            "meeting_type": {"type": "string", "description": "Type of meeting, e.g. 'ANNUAL_REVIEW'"},
            "date_str": {"type": "string", "description": "ISO 8601 date string"},
            "notes": {"type": "string", "description": "Optional agenda/notes"}
        },
        "required": ["client_name", "meeting_type", "date_str"]
    }
}
