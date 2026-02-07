from typing import Dict, Any, List
from db.supabase import get_supabase

async def get_equity_underweight_clients() -> Dict[str, Any]:
    """Find clients underweight in equities."""
    supabase = get_supabase()
    result = supabase.table("clients").select(
        "id, name, client_profiles(risk_profile), investments(equity_allocation, current_value)"
    ).execute()
    
    underweight = []
    targets = {"LOW": 30, "CAUTIOUS": 30, "BALANCED": 50, "MEDIUM": 50, "HIGH": 70, "ADVENTUROUS": 70}
    
    for c in result.data or []:
        profile = c.get("client_profiles", {}) or {}
        invs = c.get("investments", [])
        total = sum(i.get("current_value", 0) or 0 for i in invs)
        equity = sum((i.get("current_value", 0) or 0) * ((i.get("equity_allocation", 0) or 0) / 100) for i in invs)
        
        if total > 0:
            pct = (equity / total) * 100
            risk = profile.get("risk_profile", "BALANCED")
            target = targets.get(risk, 50)
            if pct < target - 10:
                underweight.append({
                    "name": c["name"],
                    "equity_pct": round(pct, 1),
                    "target": target,
                    "gap": round(target - pct, 1)
                })
    
    return {"clients": underweight, "count": len(underweight)}

get_equity_underweight_clients.tool_schema = {
    "name": "get_equity_underweight_clients",
    "description": "Find clients who are underweight in equities compared to their risk profile.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def get_isa_allowance_clients() -> Dict[str, Any]:
    """Find clients with ISA allowance remaining."""
    supabase = get_supabase()
    result = supabase.table("clients").select("id, name, client_profiles(isa_allowance_used)").execute()
    
    ISA_LIMIT = 20000
    clients = []
    for c in result.data or []:
        profile = c.get("client_profiles", {}) or {}
        used = profile.get("isa_allowance_used", 0) or 0
        remaining = ISA_LIMIT - used
        if remaining > 0:
            clients.append({"name": c["name"], "remaining": remaining})
    
    return {"clients": clients, "count": len(clients), "limit": ISA_LIMIT}

get_isa_allowance_clients.tool_schema = {
    "name": "get_isa_allowance_clients",
    "description": "Find clients with remaining ISA allowance for the current tax year.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def get_pension_allowance_clients() -> Dict[str, Any]:
    """Find clients with pension allowance remaining."""
    supabase = get_supabase()
    result = supabase.table("clients").select("id, name, client_profiles(annual_allowance_used)").execute()
    
    AA_LIMIT = 60000
    clients = []
    for c in result.data or []:
        profile = c.get("client_profiles", {}) or {}
        used = profile.get("annual_allowance_used", 0) or 0
        remaining = AA_LIMIT - used
        if remaining > 0:
            clients.append({"name": c["name"], "remaining": remaining})
    
    return {"clients": clients, "count": len(clients), "limit": AA_LIMIT}

get_pension_allowance_clients.tool_schema = {
    "name": "get_pension_allowance_clients",
    "description": "Find clients with remaining pension annual allowance.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def get_cash_excess_clients() -> Dict[str, Any]:
    """Find clients with excess cash."""
    supabase = get_supabase()
    result = supabase.table("clients").select("id, name, client_profiles(cash_reserves, monthly_expenditure)").execute()
    
    clients = []
    for c in result.data or []:
        profile = c.get("client_profiles", {}) or {}
        cash = profile.get("cash_reserves", 0) or 0
        monthly = profile.get("monthly_expenditure", 0) or 0
        if monthly > 0:
            buffer = monthly * 6
            if cash > buffer:
                clients.append({"name": c["name"], "excess": cash - buffer})
    
    return {"clients": clients, "count": len(clients)}

get_cash_excess_clients.tool_schema = {
    "name": "get_cash_excess_clients",
    "description": "Find clients with cash reserves exceeding 6 months of expenditure.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def get_protection_gap_clients() -> Dict[str, Any]:
    """Find clients with protection gaps."""
    supabase = get_supabase()
    result = supabase.table("clients").select(
        "id, name, client_profiles(dependents), protection_policies(type, sum_assured)"
    ).execute()
    
    gaps = []
    for c in result.data or []:
        profile = c.get("client_profiles", {}) or {}
        policies = c.get("protection_policies", [])
        has_life = any(p.get("type") in ["TERM_LIFE", "WHOLE_LIFE", "LIFE"] for p in policies)
        
        dependents = profile.get("dependents", 0) or 0
        if dependents > 0 and not has_life:
            gaps.append({"name": c["name"], "dependents": dependents, "missing": ["life"]})
    
    return {"clients": gaps, "count": len(gaps)}

get_protection_gap_clients.tool_schema = {
    "name": "get_protection_gap_clients",
    "description": "Find clients with potential protection gaps (e.g., dependents but no life cover).",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def get_high_withdrawal_clients() -> Dict[str, Any]:
    """Find retired clients with high withdrawal rates."""
    supabase = get_supabase()
    result = supabase.table("clients").select(
        "id, name, client_profiles(marital_status), investments(withdrawal_rate, current_value)"
    ).execute()
    
    high = []
    for c in result.data or []:
        invs = c.get("investments", [])
        total_value = sum(i.get("current_value", 0) or 0 for i in invs)
        withdrawals = sum((i.get("withdrawal_rate", 0) or 0) * (i.get("current_value", 0) or 0) / 100 for i in invs if i.get("withdrawal_rate"))
        
        if total_value > 0 and withdrawals > 0:
            rate = (withdrawals / total_value) * 100
            if rate > 4:
                high.append({"name": c["name"], "rate": round(rate, 2)})
    
    return {"clients": high, "count": len(high)}

get_high_withdrawal_clients.tool_schema = {
    "name": "get_high_withdrawal_clients",
    "description": "Find retired clients with unsustainable withdrawal rates (>4%).",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def model_market_correction(correction_percent: float) -> Dict[str, Any]:
    """Model market correction impact."""
    supabase = get_supabase()
    result = supabase.table("clients").select(
        "id, name, investments(equity_allocation, current_value)"
    ).execute()
    
    impacted = []
    for c in result.data or []:
        invs = c.get("investments", [])
        equity = sum((i.get("current_value", 0) or 0) * ((i.get("equity_allocation", 0) or 0) / 100) for i in invs)
        if equity > 0:
            loss = equity * (correction_percent / 100)
            impacted.append({"name": c["name"], "equity_exposure": equity, "potential_loss": round(loss)})
    
    impacted.sort(key=lambda x: x["potential_loss"], reverse=True)
    return {"clients": impacted[:10], "correction": correction_percent}

model_market_correction.tool_schema = {
    "name": "model_market_correction",
    "description": "Model the potential loss for all clients in a market correction.",
    "parameters": {
        "type": "object",
        "properties": {
            "correction_percent": {"type": "number", "description": "Percentage market drop (e.g. 20)"}
        },
        "required": ["correction_percent"]
    }
}

async def model_retirement_trajectory(client_name: str) -> Dict[str, Any]:
    """Project if client meets retirement goals."""
    supabase = get_supabase()
    result = supabase.table("client_profiles").select(
        "*, clients(name)"
    ).ilike("clients.name", f"%{client_name}%").execute()
    
    if not result.data:
        return {"error": f"Client '{client_name}' not found"}
    
    profile = result.data[0]
    goal = profile.get("retirement_income_goal", 0) or 0
    target_age = profile.get("retirement_target_age", 65) or 65
    
    # Get current fund
    inv_result = supabase.table("investments").select("current_value, annual_contribution").eq("client_id", profile["client_id"]).execute()
    current_fund = sum(i.get("current_value", 0) or 0 for i in inv_result.data or [])
    annual_contrib = sum(i.get("annual_contribution", 0) or 0 for i in inv_result.data or [])
    
    # Simple projection (5% growth, 4% withdrawal)
    years_to_retire = max(0, target_age - 55) # Simplified age check
    projected = current_fund
    for _ in range(years_to_retire):
        projected = (projected + annual_contrib) * 1.05
        
    est_income = projected * 0.04
    client_name_actual = profile.get("clients", {}).get("name", client_name) if isinstance(profile.get("clients"), dict) else client_name
    
    return {
        "client": client_name_actual,
        "goal": goal,
        "projected_income": round(est_income),
        "shortfall": round(max(0, goal - est_income)),
        "on_track": est_income >= goal
    }

model_retirement_trajectory.tool_schema = {
    "name": "model_retirement_trajectory",
    "description": "Project retirement income and shortfall for a client.",
    "parameters": {
        "type": "object",
        "properties": {
            "client_name": {"type": "string", "description": "Name of the client"}
        },
        "required": ["client_name"]
    }
}

async def model_interest_rate_impact(new_rate: float) -> Dict[str, Any]:
    """Model impact of interest rate changes on cash-heavy clients."""
    supabase = get_supabase()
    result = supabase.table("clients").select("name, cash_holdings").gt("cash_holdings", 50000).execute()
    
    impacted = []
    for c in result.data or []:
        cash = c.get("cash_holdings", 0)
        income_change = cash * (new_rate / 100) / 12 # Monthly impact
        impacted.append({
            "name": c["name"],
            "cash": cash,
            "monthly_interest_at_new_rate": round(income_change)
        })
        
    return {"impacted_clients": impacted[:10], "rate": new_rate}

model_interest_rate_impact.tool_schema = {
    "name": "model_interest_rate_impact",
    "description": "Model impact of interest rate changes on cash-heavy clients.",
    "parameters": {
        "type": "object",
        "properties": {
            "new_rate": {"type": "number", "description": "The new interest rate percentage"}
        },
        "required": ["new_rate"]
    }
}
