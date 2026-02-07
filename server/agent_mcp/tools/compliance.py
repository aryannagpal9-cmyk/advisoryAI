from typing import Dict, Any, List
from db.supabase import get_supabase

async def get_pending_documents() -> Dict[str, Any]:
    """Get pending documents."""
    supabase = get_supabase()
    result = supabase.table("document_requests").select(
        "id, document_type, requested_date, clients(name)"
    ).eq("status", "PENDING").execute()
    
    docs = []
    for d in result.data or []:
        client = d.get("clients", {})
        docs.append({
            "client": client.get("name", "Unknown"),
            "type": d.get("document_type"),
            "requested": d.get("requested_date")
        })
    
    return {"documents": docs, "count": len(docs)}

get_pending_documents.tool_schema = {
    "name": "get_pending_documents",
    "description": "Find all documents currently pending from clients or providers.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def get_recommendation_history(client_name: str) -> Dict[str, Any]:
    """Get client recommendation history."""
    supabase = get_supabase()
    client = supabase.table("clients").select("id, name").ilike("name", f"%{client_name}%").execute()
    
    if not client.data:
        return {"error": f"Client '{client_name}' not found"}
    
    client_id = client.data[0]["id"]
    recs = supabase.table("recommendations").select(
        "id, recommendation_type, description, created_at, status"
    ).eq("client_id", client_id).order("created_at", desc=True).limit(10).execute()
    
    return {"client": client.data[0]["name"], "recommendations": recs.data or []}

get_recommendation_history.tool_schema = {
    "name": "get_recommendation_history",
    "description": "Get the historical list of financial recommendations for a specific client.",
    "parameters": {
        "type": "object",
        "properties": {
            "client_name": {"type": "string", "description": "Name of the client"}
        },
        "required": ["client_name"]
    }
}

async def search_exact_wording_risk(client_name: str) -> Dict[str, Any]:
    """Search exact wording of risk discussions for a client."""
    supabase = get_supabase()
    client = supabase.table("clients").select("id, name").ilike("name", f"%{client_name}%").execute()
    if not client.data:
        return {"error": f"Client '{client_name}' not found"}
        
    meetings = supabase.table("meetings").select(
        "scheduled_at, risk_discussions"
    ).eq("client_id", client.data[0]["id"]).not_.is_("risk_discussions", "null").execute()
    
    return {
        "client": client.data[0]["name"],
        "discussions": meetings.data or []
    }

search_exact_wording_risk.tool_schema = {
    "name": "search_exact_wording_risk",
    "description": "Retrieve meeting notes regarding risk for compliance auditing.",
    "parameters": {
        "type": "object",
        "properties": {
            "client_name": {"type": "string", "description": "Name of the client"}
        },
        "required": ["client_name"]
    }
}

async def get_sustainable_investing_summary() -> Dict[str, Any]:
    """Summary of ESG/Sustainable investing discussions."""
    supabase = get_supabase()
    profiles = supabase.table("client_profiles").select(
        "clients(name), preferences"
    ).execute()
    
    esg_prefs = []
    for p in profiles.data or []:
        prefs = p.get("preferences") or {}
        if any(k in str(prefs).lower() for k in ["esg", "sustainable", "ethical"]):
            esg_prefs.append({"name": p["clients"]["name"], "preferences": prefs})
            
    return {"esg_clients": esg_prefs, "count": len(esg_prefs)}

get_sustainable_investing_summary.tool_schema = {
    "name": "get_sustainable_investing_summary",
    "description": "Get a summary of clients with ESG/sustainable investing preferences.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def get_promises_made(client_name: str = None) -> Dict[str, Any]:
    """Find items promised to clients (heuristics via status)."""
    supabase = get_supabase()
    # Since promised_at is missing, we look for items in action_items marked as AGENT owner
    query = supabase.table("action_items").select(
        "title, status, due_date, clients(name)"
    ).eq("owner", "AGENT")
    
    if client_name:
        query = query.ilike("clients.name", f"%{client_name}%")
        
    result = query.execute()
    return {"promises": result.data or [], "count": len(result.data or [])}

get_promises_made.tool_schema = {
    "name": "get_promises_made",
    "description": "Track items or tasks promised to clients by the advisor/agent.",
    "parameters": {
        "type": "object",
        "properties": {
            "client_name": {"type": "string", "description": "Optional name to filter by"}
        },
        "required": []
    }
}
