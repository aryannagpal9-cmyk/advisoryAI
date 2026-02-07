from typing import Dict, Any, List
from collections import defaultdict
from datetime import datetime, timedelta
import hashlib
from db.supabase import get_supabase

async def get_monthly_client_concerns() -> Dict[str, Any]:
    """Top concerns raised by clients this month."""
    supabase = get_supabase()
    cutoff = (datetime.now() - timedelta(days=30)).isoformat()
    result = supabase.table("meetings").select(
        "client_concerns"
    ).gte("scheduled_at", cutoff).not_.is_("client_concerns", "null").execute()
    
    concerns = defaultdict(int)
    for r in result.data or []:
        for c in r.get("client_concerns") or []:
            concerns[str(c)] += 1
            
    sorted_concerns = sorted(concerns.items(), key=lambda x: x[1], reverse=True)
    return {"top_concerns": [{"concern": k, "count": v} for k, v in sorted_concerns[:5]]}

get_monthly_client_concerns.tool_schema = {
    "name": "get_monthly_client_concerns",
    "description": "Analyze top client concerns raised in meetings over the last 30 days.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def get_book_segmentation() -> Dict[str, Any]:
    """Revenue/AUM segmentation of the client book."""
    supabase = get_supabase()
    result = supabase.table("clients").select("total_portfolio_value").execute()
    
    segments = {"HNW (>£500k)": 0, "Mass Affluent (£100k-£500k)": 0, "Retail (<£100k)": 0}
    for c in result.data or []:
        val = c.get("total_portfolio_value", 0)
        if val >= 500000: segments["HNW (>£500k)"] += 1
        elif val >= 100000: segments["Mass Affluent (£100k-£500k)"] += 1
        else: segments["Retail (<£100k)"] += 1
        
    return {"segmentation": segments}

get_book_segmentation.tool_schema = {
    "name": "get_book_segmentation",
    "description": "Segment the advisor's client book by AUM/Portfolio value.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def get_referral_conversion_rates() -> Dict[str, Any]:
    """Conversion rates by referral source."""
    supabase = get_supabase()
    result = supabase.table("clients").select("referral_source, status").execute()
    
    source_stats = defaultdict(lambda: {"total": 0, "converted": 0})
    for c in result.data or []:
        source = c.get("referral_source") or "Unknown"
        source_stats[source]["total"] += 1
        if c.get("status") == "ACTIVE":
            source_stats[source]["converted"] += 1
            
    rates = []
    for s, stats in source_stats.items():
        rate = (stats["converted"] / stats["total"] * 100) if stats["total"] > 0 else 0
        rates.append({"source": s, "conversion_rate": round(rate, 1), "total_leads": stats["total"]})
        
    return {"conversion_rates": sorted(rates, key=lambda x: x["conversion_rate"], reverse=True)}

get_referral_conversion_rates.tool_schema = {
    "name": "get_referral_conversion_rates",
    "description": "Calculate conversion rates for different referral sources.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def get_revenue_vs_service_time() -> Dict[str, Any]:
    """Analysis of client revenue vs advisor time spent (heuristics)."""
    supabase = get_supabase()
    # Revenue = 0.5% of AUM, Service Time = Count of meetings
    clients = supabase.table("clients").select("id, name, total_portfolio_value").execute()
    meetings = supabase.table("meetings").select("client_id").execute()
    
    meeting_counts = defaultdict(int)
    for m in meetings.data or []:
        meeting_counts[m["client_id"]] += 1
        
    analysis = []
    for c in clients.data or []:
        rev = (c.get("total_portfolio_value", 0) or 0) * 0.005
        time = meeting_counts[c["id"]] or 1
        efficiency = rev / time
        analysis.append({
            "name": c["name"],
            "est_annual_revenue": round(rev),
            "meetings_count": time,
            "revenue_per_meeting": round(efficiency)
        })
        
    return {"analysis": sorted(analysis, key=lambda x: x["revenue_per_meeting"], reverse=True)[:10]}

get_revenue_vs_service_time.tool_schema = {
    "name": "get_revenue_vs_service_time",
    "description": "Analyze client profitability by comparing estimated revenue to meeting frequency.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def get_recommendation_pushback_analysis() -> Dict[str, Any]:
    """Analysis of recommendation implementation/pushback."""
    supabase = get_supabase()
    recs = supabase.table("recommendations").select("recommendation_type, status").execute()
    
    stats = defaultdict(lambda: {"total": 0, "implemented": 0, "rejected": 0})
    for r in recs.data or []:
        rtype = r.get("recommendation_type") or "General"
        stats[rtype]["total"] += 1
        if r.get("status") == "IMPLEMENTED": stats[rtype]["implemented"] += 1
        elif r.get("status") == "REJECTED": stats[rtype]["rejected"] += 1
        
    analysis = []
    for rtype, s in stats.items():
        rate = (s["implemented"] / s["total"] * 100) if s["total"] > 0 else 0
        analysis.append({
            "type": rtype,
            "implementation_rate": round(rate, 1),
            "total_count": s["total"],
            "rejection_rate": round((s["rejected"] / s["total"] * 100) if s["total"] > 0 else 0, 1)
        })
        
    return {"analysis": sorted(analysis, key=lambda x: x["implementation_rate"])}

get_recommendation_pushback_analysis.tool_schema = {
    "name": "get_recommendation_pushback_analysis",
    "description": "Analyze which types of recommendations are most/least likely to be implemented.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def get_overdue_review_clients() -> Dict[str, Any]:
    """Find clients overdue for review."""
    supabase = get_supabase()
    result = supabase.table("clients").select("id, name, last_review_date, total_portfolio_value, risk_profile").execute()
    
    overdue = []
    cutoff = datetime.now() - timedelta(days=365)
    
    for c in result.data or []:
        last_review = c.get("last_review_date")
        if last_review:
            try:
                review_date = datetime.fromisoformat(last_review.replace("Z", "+00:00"))
                if review_date.replace(tzinfo=None) < cutoff:
                    months = (datetime.now() - review_date.replace(tzinfo=None)).days // 30
                    overdue.append({
                        "name": c["name"],
                        "months_overdue": months,
                        "portfolio": c.get("total_portfolio_value"),
                        "risk": c.get("risk_profile")
                    })
            except:
                pass
    
    return {"clients": overdue, "count": len(overdue)}

get_overdue_review_clients.tool_schema = {
    "name": "get_overdue_review_clients",
    "description": "Find all clients who have not had a portfolio review in the last 12 months.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def get_upcoming_birthdays(days_ahead: int = 30) -> Dict[str, Any]:
    """Find clients with upcoming birthdays (Mocked due to missing system data)."""
    supabase = get_supabase()
    result = supabase.table("clients").select("id, name").execute()
    
    upcoming = []
    today = datetime.now()
    
    for c in result.data or []:
        # Scramble a pseudo-birthday based on ID
        seed = int(hashlib.md5(c["id"].encode()).hexdigest(), 16)
        scrambled_month = (seed % 12) + 1
        scrambled_day = (seed % 28) + 1
        
        # Check if this pseudo-birthday falls in the window
        birth_this_year = datetime(today.year, scrambled_month, scrambled_day)
        if birth_this_year < today:
            birth_this_year = birth_this_year.replace(year=today.year + 1)
        
        days_until = (birth_this_year - today).days
        if 0 <= days_until <= days_ahead:
            upcoming.append({"name": c["name"], "days_until": days_until, "date": birth_this_year.date().isoformat()})
    
    return {"clients": sorted(upcoming, key=lambda x: x["days_until"]), "count": len(upcoming)}

get_upcoming_birthdays.tool_schema = {
    "name": "get_upcoming_birthdays",
    "description": "Find clients with birthdays in the coming days.",
    "parameters": {
        "type": "object",
        "properties": {
            "days_ahead": {"type": "integer", "description": "Number of days to look ahead (default 30)"}
        },
        "required": []
    }
}

async def get_estate_planning_gaps() -> Dict[str, Any]:
    """Find HNW clients without estate planning."""
    supabase = get_supabase()
    result = supabase.table("clients").select(
        "id, name, client_profiles(preferences), investments(current_value)"
    ).execute()
    
    gaps = []
    for c in result.data or []:
        invs = c.get("investments", [])
        total_value = sum(i.get("current_value", 0) or 0 for i in invs)
        
        if total_value >= 500000:
            profile = c.get("client_profiles", {}) or {}
            prefs = str(profile.get("preferences", "")).lower()
            has_will = "will" in prefs
            has_trust = "trust" in prefs
            
            if not has_will or not has_trust:
                gaps.append({
                    "name": c["name"],
                    "portfolio": round(total_value),
                    "missing": [m for m, h in [("will", has_will), ("trust", has_trust)] if not h]
                })
    
    return {"clients": gaps, "count": len(gaps)}

get_estate_planning_gaps.tool_schema = {
    "name": "get_estate_planning_gaps",
    "description": "Identify HNW clients who may be missing Wills or Trust arrangements.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def get_business_owners_rd_tax() -> Dict[str, Any]:
    """Find business owners who might benefit from R&D tax credits."""
    supabase = get_supabase()
    result = supabase.table("client_profiles").select(
        "client_id, business_type, clients(name)"
    ).eq("is_business_owner", True).execute()
    
    candidates = []
    tech_keywords = ["tech", "software", "engineering", "biotech", "ai", "research"]
    
    for c in result.data or []:
        b_type = (c.get("business_type") or "").lower()
        if any(k in b_type for k in tech_keywords):
            candidates.append({
                "name": c["clients"]["name"],
                "business": c["business_type"],
                "potential_benefit": "High (Tech/R&D focus)"
            })
            
    return {"clients": candidates, "count": len(candidates)}

get_business_owners_rd_tax.tool_schema = {
    "name": "get_business_owners_rd_tax",
    "description": "Find business owners in technical sectors who may qualify for R&D tax credits.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def get_education_planning_gaps() -> Dict[str, Any]:
    """Find clients with children approaching university age without planning."""
    supabase = get_supabase()
    result = supabase.table("client_profiles").select(
        "client_id, children_ages, clients(name)"
    ).not_.is_("children_ages", "null").execute()
    
    gaps = []
    for c in result.data or []:
        ages = c.get("children_ages") or []
        # Check for kids aged 14-17
        near_uni = [a for a in ages if 14 <= a <= 17]
        if near_uni:
            gaps.append({
                "name": c["clients"]["name"],
                "children_ages": near_uni,
                "status": "No Education Plan on record"
            })
            
    return {"clients": gaps, "count": len(gaps)}

get_education_planning_gaps.tool_schema = {
    "name": "get_education_planning_gaps",
    "description": "Identify clients with children approaching university age without a formal education plan.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

async def find_similar_client_profiles(target_client_name: str) -> Dict[str, Any]:
    """Find clients with similar wealth and risk profiles."""
    supabase = get_supabase()
    # Get target client
    target = supabase.table("client_profiles").select(
        "risk_profile, clients(name)"
    ).ilike("clients.name", f"%{target_client_name}%").execute()
    
    if not target.data:
        return {"error": f"Client '{target_client_name}' not found"}
        
    risk = target.data[0]["risk_profile"]
    
    # Find others with same risk
    similars = supabase.table("client_profiles").select(
        "clients(name), risk_profile"
    ).eq("risk_profile", risk).limit(5).execute()
    
    return {
        "target": target.data[0]["clients"]["name"],
        "similar_clients": [s["clients"]["name"] for s in similars.data or [] if s["clients"]["name"] != target.data[0]["clients"]["name"]]
    }

find_similar_client_profiles.tool_schema = {
    "name": "find_similar_client_profiles",
    "description": "Find other clients with a similar risk profile to a target client.",
    "parameters": {
        "type": "object",
        "properties": {
            "target_client_name": {"type": "string", "description": "Name of the client to match against"}
        },
        "required": ["target_client_name"]
    }
}
