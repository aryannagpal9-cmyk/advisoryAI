from typing import Dict, Any, List
from db.supabase import get_supabase

async def search_clients(query: str) -> Dict[str, Any]:
    """Search clients by name."""
    supabase = get_supabase()
    result = supabase.table("clients").select(
        "id, name, email, phone"
    ).ilike("name", f"%{query}%").limit(10).execute()
    
    return {"clients": result.data or [], "count": len(result.data or [])}

search_clients.tool_schema = {
    "name": "search_clients",
    "description": "Search for clients by name.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Name or partial name to search for"}
        },
        "required": ["query"]
    }
}

async def get_client_profile(client_name: str) -> Dict[str, Any]:
    """Get full client profile."""
    supabase = get_supabase()
    result = supabase.table("clients").select(
        "*, investments(*), protection_policies(*)"
    ).ilike("name", f"%{client_name}%").execute()
    
    if not result.data:
        return {"error": f"Client '{client_name}' not found"}
    
    c = result.data[0]
    return {
        "name": c.get("name"),
        "email": c.get("email"),
        "risk": c.get("risk_profile"),
        "portfolio": c.get("total_portfolio_value"),
        "investments": len(c.get("investments", [])),
        "policies": len(c.get("protection_policies", []))
    }

get_client_profile.tool_schema = {
    "name": "get_client_profile",
    "description": "Get detailed financial profile for a client by name.",
    "parameters": {
        "type": "object",
        "properties": {
            "client_name": {"type": "string", "description": "Full name of the client"}
        },
        "required": ["client_name"]
    }
}
