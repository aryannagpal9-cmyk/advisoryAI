from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
import asyncio
import random
from datetime import datetime, timedelta, timezone

# Stub Imports
from services.llm_service import GroqService
from db.supabase import get_supabase
from services.logging_service import get_logger
from services.exceptions import DatabaseError, NotFoundError, ValidationError

import json
import os
import traceback
from collections import defaultdict

router = APIRouter()
supabase = get_supabase()
logger = get_logger(__name__)
groq_service = GroqService()

# --- Simulation State ---
# No longer using SIM_STATE_FILE = "simulation_state.json" as it causes errors on read-only file systems (e.g. Vercel)

def _get_simulated_now():
    """Get the current simulated time, persisting across requests via Supabase."""
    try:
        # Get the latest simulation state from audit_logs
        res = supabase.table("audit_logs").select("metadata").eq("action", "SIMULATION_STATE").order("created_at", desc=True).limit(1).execute()
        if res.data and res.data[0].get("metadata") and "current_date" in res.data[0]["metadata"]:
            return datetime.fromisoformat(res.data[0]["metadata"]["current_date"])
    except Exception as e:
        logger.error(f"Error fetching simulated time from DB: {e}")
    
    # Default to today 9am UTC if not found or error
    dt = datetime.now(timezone.utc).replace(hour=9, minute=0, second=0, microsecond=0)
    return dt

def _save_simulated_now(dt: datetime):
    """Save the simulated time to Supabase audit_logs."""
    try:
        supabase.table("audit_logs").insert({
            "action": "SIMULATION_STATE",
            "actor": "SYSTEM",
            "reason": f"Time advanced to {dt.isoformat()}",
            "metadata": {"current_date": dt.isoformat()}
        }).execute()
    except Exception as e:
        logger.error(f"Error saving simulated time to DB: {e}")

def _advance_simulated_now():
    """Advance the simulated time by 1 day."""
    now = _get_simulated_now()
    new_now = now + timedelta(days=1)
    _save_simulated_now(new_now)
    return new_now

# --- CACHE SETUP ---
_dashboard_cache = {
    "data": None,
    "timestamp": None
}
CACHE_TTL = 3 # seconds (reduced for simulation feel)

async def get_cached_dashboard():
    global _dashboard_cache
    now = datetime.now()
    if _dashboard_cache["data"] and _dashboard_cache["timestamp"]:
        if (now - _dashboard_cache["timestamp"]).total_seconds() < CACHE_TTL:
            return _dashboard_cache["data"]
    
    # Cache miss or expired - refresh
    data = await _fetch_dashboard_data()
    _dashboard_cache = {
        "data": data,
        "timestamp": now
    }
    return data

async def _fetch_dashboard_data():
    """Inner logic to fetch all dashboard data in parallel."""
    simulated_now = _get_simulated_now()
    simulated_now_str = simulated_now.isoformat()
    
    # 1. Prepare Date Ranges for Trend
    today = simulated_now.replace(hour=0, minute=0, second=0, microsecond=0)
    seven_days_ago = today - timedelta(days=6)
    seven_days_str = seven_days_ago.isoformat()
    
    # 2. Define Tasks
    # Stats: Count total cases, active cases, pending requests, blocked items
    # We fetch status columns to count in memory (efficient enough for small-medium scale)
    stats_cases_task = asyncio.to_thread(
        lambda: supabase.table("cases").select("status").lte("created_at", simulated_now_str).execute()
    )
    stats_reqs_task = asyncio.to_thread(
        lambda: supabase.table("requests").select("status").lte("created_at", simulated_now_str).execute()
    )
    
    # Priority & Recent Activity (Reuse helper functions)
    priority_task = asyncio.to_thread(get_priority_cases)
    recent_task = asyncio.to_thread(get_recent_activity)
    
    # Trend Data
    # Cases created in last 7 days
    trend_cases_task = asyncio.to_thread(
        lambda: supabase.table("cases").select("created_at")
        .gte("created_at", seven_days_str)
        .lte("created_at", simulated_now_str)
        .execute()
    )
    # Chase actions in last 7 days
    trend_logs_task = asyncio.to_thread(
        lambda: supabase.table("audit_logs").select("created_at")
        .gte("created_at", seven_days_str)
        .lte("created_at", simulated_now_str)
        .in_("action", ["CHASE_SENT", "MANUAL_CHASE"])
        .execute()
    )
    
    # 3. Await All
    (
        stats_cases_res, 
        stats_reqs_res, 
        priority_items, 
        recent_activity, 
        trend_cases_res, 
        trend_logs_res
    ) = await asyncio.gather(
        stats_cases_task,
        stats_reqs_task,
        priority_task,
        recent_task,
        trend_cases_task,
        trend_logs_task
    )
    
    # 4. Process Stats
    cases = stats_cases_res.data or []
    reqs = stats_reqs_res.data or []
    
    total_cases = len(cases)
    active_cases = len([c for c in cases if c["status"] == "ACTIVE"])
    pending_requests = len([r for r in reqs if r["status"] == "PENDING" or r["status"] == "WAITING"]) # waiting is also pending-ish
    blocked_items = len([r for r in reqs if r["status"] in ["ESCALATED", "INVALID", "BLOCKED"]])
    
    # Calculate "Automation Rate" / "Time Saved" (Stub logic for now)
    completed_reqs = len([r for r in reqs if r["status"] == "FULFILLED"])
    automation_rate = int((completed_reqs / len(reqs) * 100)) if reqs else 0
    time_saved = round(completed_reqs * 0.5, 1) # assume 30 mins saved per request
    
    stats = {
        "active_cases": active_cases,
        "completed_cases": total_cases - active_cases,
        "pending_requests": pending_requests,
        "blocked_items": blocked_items,
        "time_saved_hours": time_saved,
        "system_health": {"automation_rate": automation_rate}
    }
    
    # 5. Process Trend
    # Initialize last 7 days map
    trend_map = {}
    for i in range(7):
        d = (seven_days_ago + timedelta(days=i)).strftime("%Y-%m-%d")
        trend_map[d] = {"cases": 0, "reachouts": 0}
        
    for c in (trend_cases_res.data or []):
        d = c["created_at"][:10]
        if d in trend_map:
            trend_map[d]["cases"] += 1
            
    for l in (trend_logs_res.data or []):
        d = l["created_at"][:10]
        if d in trend_map:
            trend_map[d]["reachouts"] += 1
            
    trend_data = [{"date": k, **v} for k, v in sorted(trend_map.items())]
    
    # 6. Process Distribution
    # Group requests by status
    dist_map = {"PENDING": 0, "FULFILLED": 0, "ESCALATED": 0, "Other": 0}
    for r in reqs:
        s = r["status"]
        if s in dist_map:
            dist_map[s] += 1
        else:
            dist_map["Other"] += 1
            
    distribution = [
        {"name": "Pending", "value": dist_map["PENDING"]},
        {"name": "Fulfilled", "value": dist_map["FULFILLED"]},
        {"name": "Escalated", "value": dist_map["ESCALATED"]},
        {"name": "Other", "value": dist_map["Other"]},
    ]
    # Filter out zero values for cleaner chart
    distribution = [d for d in distribution if d["value"] > 0]

    return {
        "simulated_date": simulated_now_str,
        "stats": stats,
        "trend": trend_data,
        "distribution": distribution,
        "priority": priority_items,
        "activity": recent_activity
    }

@router.get("/cases")
def get_cases():
    simulated_now_str = _get_simulated_now().isoformat()
    res = supabase.table("cases").select("*, clients(name)").lte("created_at", simulated_now_str).execute()
    # Flattener to match frontend expectation (client_name)
    data = []
    for c in res.data:
        c["client_name"] = c["clients"]["name"] if c.get("clients") else "Unknown"
        data.append(c)
    return data

@router.get("/cases/priority")
def get_priority_cases():
    """
    Get cases with HIGH priority requests for Priority Focus section.
    Respects simulated date.
    """
    simulated_now_str = _get_simulated_now().isoformat()
    # Get requests with HIGH priority AND created before/at simulated_now
    res = supabase.table("requests").select("*, cases(title, clients(name), status)").eq("priority", "HIGH").lte("created_at", simulated_now_str).limit(5).execute()
    
    priority_items = []
    for r in res.data:
        # Also check if the CASE itself is visible
        # (Technically if request is visible, case should be, but good to be safe)
        if r.get("cases"):
            priority_items.append({
                "case_id": r["case_id"],
                "case_title": r["cases"]["title"],
                "client_name": r["cases"]["clients"]["name"] if r["cases"].get("clients") else "Unknown",
                "case_status": r["cases"]["status"],
                "request_status": r["status"],
                "request_title": r["title"]
            })
    
    return priority_items

@router.get("/cases/search")
def search_cases(q: str = ""):
    """
    Search cases by client name or title.
    """
    if not q:
        return []

    simulated_now_str = _get_simulated_now().isoformat()
    
    # Simple search using ilike on title, then filter client-side by client name as well
    res = (
        supabase.table("cases")
        .select("*, clients(name)")
        .ilike("title", f"%{q}%")
        .lte("created_at", simulated_now_str)
        .execute()
    )

    data = []
    for c in res.data:
        c["client_name"] = c["clients"]["name"] if c.get("clients") else "Unknown"
        if q.lower() in c.get("client_name", "").lower() or q.lower() in c.get("title", "").lower():
            data.append(c)

    return data

@router.get("/cases/{case_id}")
def get_case(case_id: str):
    simulated_now_str = _get_simulated_now().isoformat()

    # Fetch case with client details
    case_res = supabase.table("cases").select("*, clients(name)").eq("id", case_id).lte("created_at", simulated_now_str).single().execute()
    
    if not case_res.data:
        raise HTTPException(status_code=404, detail="Case not found or created in future")
        
    case = case_res.data
    case["client_name"] = case["clients"]["name"] if case.get("clients") else "Unknown"
    
    # Fetch requests (related items) - FILTERED
    req_res = supabase.table("requests").select("*").eq("case_id", case_id).lte("created_at", simulated_now_str).execute()
    case["requests"] = req_res.data

    # Fetch audit logs - FILTERED
    logs_res = supabase.table("audit_logs").select("*").eq("case_id", case_id).lte("created_at", simulated_now_str).order("created_at", desc=True).execute()
    data_logs = []
    for log in logs_res.data:
        log["details"] = log.get("reason") # Map for frontend
        data_logs.append(log)
    case["audit_logs"] = data_logs
    
    return case

@router.get("/recent-activity")
def get_recent_activity():
    """
    Get recent global activity (audit logs).
    Respects simulated date.
    """
    simulated_now_str = _get_simulated_now().isoformat()
    res = supabase.table("audit_logs").select("*").lte("created_at", simulated_now_str).order("created_at", desc=True).limit(10).execute()
    data = []
    for log in res.data:
        log["details"] = log.get("reason")
        data.append(log)
    return data

# ...

@router.get("/feed/exceptions")
def get_exception_feed():
    """
    Returns only items that are BLOCKED, ESCALATED, or INVALID.
    Respects simulated date.
    """
    simulated_now_str = _get_simulated_now().isoformat()
    res = supabase.table("requests").select("*, cases(title, clients(name))").in_("status", ["ESCALATED", "INVALID"]).lte("created_at", simulated_now_str).execute()
    # Flatten structure for frontend
    data = []
    for r in res.data:
        r["case_title"] = r["cases"]["title"] if r.get("cases") else "Unknown"
        r["client_name"] = r["cases"]["clients"]["name"] if r.get("cases") and r["cases"].get("clients") else "Unknown"
        data.append(r)
    return data

from engine.guardrails import guardrails

@router.post("/chat/intent")
async def classify_intent(message: str):
    is_safe, reason = guardrails.validate_input(message)
    if not is_safe:
        return {"original_message": message, "classified_intent": "BLOCKED", "reason": reason}

    intent = await groq_service.classify_chat_intent(message)
    return {"original_message": message, "classified_intent": intent}

@router.get("/dashboard/overview")
async def get_dashboard_overview():
    """Consolidated dashboard data for performance optimization."""
    return await get_cached_dashboard()

@router.get("/dashboard/stats")
async def get_dashboard_stats():
    # Keep for internal or legacy use, but frontend should move to /overview
    data = await get_cached_dashboard()
    return data["stats"]

@router.get("/dashboard/trend")
async def get_dashboard_trend():
    data = await get_cached_dashboard()
    return data["trend"]

@router.get("/dashboard/distribution")
async def get_dashboard_distribution():
    data = await get_cached_dashboard()
    return data["distribution"]

@router.post("/simulate/advance-day")
async def simulate_advance_day():
    """
    Simulate advancing time by 1 day.
    Reordered for immediate action.
    """
    from services.llm_service import GroqService
    from agents.smart_agent import SmartAgent
    
    actions_taken = []
    try:
        llm = GroqService()
        agent = SmartAgent(supabase, llm.client)
        
        # 1. ADVANCE PERSISTENT CLOCK
        simulated_now = _advance_simulated_now()
        logger.info(f"ADVANCING SIMULATION TO: {simulated_now}")

        # 2. CREATE NEW CASE (Trigger Immediate First Outreach)
        if random.random() < 0.75:
            try:
                clients = supabase.table("clients").select("id, name").execute().data or []
                if clients:
                    client = random.choice(clients)
                case_types = ["Pension Transfer", "ISA Top Up", "Annual Review", "Protection Review", "New Investment", "Mortgage Application"]
                title = f"{random.choice(case_types)} - {client['name'].split()[-1]}"
                
                new_case = supabase.table("cases").insert({
                    "client_id": client["id"],
                    "advisor_id": "00000000-0000-0000-0000-000000000000",
                    "title": title, "status": "ACTIVE", "created_at": simulated_now.isoformat()
                }).execute()
                
                if new_case.data:
                    case_id = new_case.data[0]["id"]
                    req_templates = [
                        {"title": "Passport Copy", "type": "CLIENT"},
                        {"title": "Utility Bill", "type": "CLIENT"},
                        {"title": "Letter of Authority", "type": "CLIENT"}
                    ]
                    for req_t in random.sample(req_templates, k=random.randint(1, 2)):
                        # Randomize priority: 70% STANDARD, 20% HIGH, 10% CRITICAL
                        rand = random.random()
                        if rand < 0.7: priority = "STANDARD"
                        elif rand < 0.9: priority = "HIGH"
                        else: priority = "CRITICAL"
                        
                        req_res = supabase.table("requests").insert({
                            "case_id": case_id, "title": req_t["title"], "owner_type": req_t["type"],
                            "status": "PENDING", "priority": priority, "created_at": simulated_now.isoformat(),
                            "next_action_at": simulated_now.isoformat(), 
                            "retry_count": 0, "client_owner_id": client["id"] if req_t["type"] == "CLIENT" else None
                        }).execute()
                        
                        if req_res.data:
                            # TRIGGER IMMEDIATE CHASE VIA AGENT
                            chase_res = await agent._trigger_chase(req_res.data[0]["id"], simulated_now=simulated_now)
                            if chase_res.get("success"):
                                actions_taken.append({
                                    "action": "CHASE_EMAIL_SENT", 
                                    "description": f"Initial outreach sent to {client['name']} for {req_t['title']}"
                                })

                    supabase.table("audit_logs").insert({
                        "case_id": case_id, "action": "CASE_CREATED", "actor": "SIMULATION",
                        "reason": f"New inbound case: {title}", "created_at": simulated_now.isoformat()
                    }).execute()
                    actions_taken.append({"action": "CASE_CREATED", "description": f"New case: {title}"})
            except Exception as e: logger.error(f"Error in Case Creation: {e}")

        # 3. MEETING COMPLETION & MINUTES OF MEETING (MoM)
        try:
            overdue_meetings = supabase.table("meetings").select("*, clients(id, name, email)").eq("status", "SCHEDULED").lte("scheduled_at", simulated_now.isoformat()).execute().data or []
            for meeting in overdue_meetings:
                supabase.table("meetings").update({"status": "COMPLETED", "notes": "Meeting held. Minutes of Meeting sent."}).eq("id", meeting["id"]).execute()
                
                # Gather meeting details for MoM
                client_name = (meeting.get("clients") or {}).get("name", "Client")
                client_email = (meeting.get("clients") or {}).get("email")
            meeting_title = meeting.get("title", "Meeting")
            topics = meeting.get("topics_discussed") or ["General discussion"]
            recommendations = meeting.get("recommendations_made") or []
            
            # Generate detailed Minutes of Meeting
            mom_prompt = f"""You are a professional financial advisor. Generate a formal Minutes of Meeting email.

Client: {client_name}
Meeting: {meeting_title}
Date: {simulated_now.strftime('%d %B %Y')}
Topics Discussed: {', '.join(topics) if isinstance(topics, list) else topics}
Recommendations Made: {json.dumps(recommendations) if recommendations else 'None specific'}

Write a professional MoM email including:
1. Thank the client for attending
2. Summary of topics discussed
3. Key recommendations made (if any)
4. Action items and next steps
5. Timeline for follow-up

Sign off as "AdvisoryAI Team". Keep it concise but comprehensive."""

            mom_body = await llm.generate_completion(mom_prompt)
            
            # Create action items from the meeting
            if recommendations:
                for rec in recommendations[:3]:  # Limit to 3 action items
                    rec_title = rec.get("type", "Follow-up") if isinstance(rec, dict) else str(rec)[:50]
                    supabase.table("action_items").insert({
                        "client_id": meeting.get("client_id"),
                        "title": f"Follow-up: {rec_title}",
                        "status": "PENDING",
                        "priority": "MEDIUM",
                        "due_date": (simulated_now + timedelta(days=7)).date().isoformat(),
                        "created_at": simulated_now.isoformat()
                    }).execute()
            
            supabase.table("email_drafts").insert({
                "client_id": meeting["client_id"], 
                "subject": f"Minutes of Meeting: {meeting_title}",
                "body": mom_body, 
                "to_email": client_email, 
                "to_name": client_name,
                "context_type": "MOM", 
                "context_summary": f"MoM for {meeting_title}",
                "sent_at": simulated_now.isoformat(), 
                "created_at": simulated_now.isoformat()
            }).execute()

            supabase.table("audit_logs").insert({
                "action": "MOM_SENT", "actor": "SYSTEM",
                "reason": f"Minutes of Meeting sent for: {meeting_title}", "created_at": simulated_now.isoformat()
            }).execute()
            actions_taken.append({"action": "MOM_SENT", "description": f"Minutes of Meeting sent for: {meeting_title}"})
        except Exception as e: logger.error(f"Error in Meeting Completion/MoM: {e}")

        # 3b. SCHEDULE NEW MEETINGS
        if random.random() < 0.3:
            try:
                clients = supabase.table("clients").select("id, name, email").execute().data or []
                if clients:
                    client = random.choice(clients)
                    meeting_types = ["Annual Review", "Investment Strategy", "Retirement Planning", "Tax Optimization", "Portfolio Rebalancing"]
                    title = f"{random.choice(meeting_types)} with {client['name']}"
                    
                    # Schedule 2-10 days in the future
                    scheduled_at = simulated_now + timedelta(days=random.randint(2, 10), hours=random.randint(9, 16))
                    
                    new_meeting = supabase.table("meetings").insert({
                        "client_id": client["id"],
                        "title": title,
                        "status": "SCHEDULED",
                        "meeting_type": "VIDEO_CALL",
                        "scheduled_at": scheduled_at.isoformat(),
                        "created_at": simulated_now.isoformat(),
                        "topics_discussed": [random.choice(meeting_types)],
                        "recommendations_made": [{"type": "Follow-up", "detail": "Discussed during simulation"}]
                    }).execute()
                    
                    if new_meeting.data:
                        actions_taken.append({
                            "action": "MEETING_SCHEDULED", 
                            "description": f"New meeting scheduled: {title} on {scheduled_at.strftime('%d %b')}"
                        })
                        
                        supabase.table("audit_logs").insert({
                            "action": "MEETING_SCHEDULED", "actor": "SYSTEM",
                            "reason": f"System scheduled a meeting: {title}", 
                            "created_at": simulated_now.isoformat()
                        }).execute()
            except Exception as e: logger.error(f"Error Scheduling Meeting: {e}")

        # 4. MASTER CHASE LOOP (Agent checks ALL pending daily)
        logger.info(f"AGENT CHECKING DAILY CHASES: {simulated_now.date()}")
        pending = supabase.table("requests").select("*, cases(id, title, clients(id, name, email))").eq("status", "PENDING").execute()

        
        for req in (pending.data or []):
            if req.get("next_action_at"):
                try:
                    next_action_str = req["next_action_at"].replace('Z', '+00:00')
                    next_action = datetime.fromisoformat(next_action_str)
                    if next_action.tzinfo is None:
                        next_action = next_action.replace(tzinfo=timezone.utc)
                    
                    if next_action <= simulated_now:
                        # Agent handles the chase logic
                        chase_res = await agent._trigger_chase(req["id"], simulated_now=simulated_now)
                        if chase_res.get("success"):
                            actions_taken.append({
                                "action": chase_res.get("action", "CHASE_SENT"),
                                "description": f"Automated action for {req['title']}: {chase_res.get('action')}",
                                "request_id": req["id"]
                            })
                except Exception as e:
                    logger.error(f"Error in chase logic for request {req.get('id')}: {e}")

        # --- 5. Check if any cases can be auto-completed ---
        try:
            active_cases = supabase.table("cases").select("id").eq("status", "ACTIVE").execute().data or []
            for case in active_cases:
                case_requests = supabase.table("requests").select("status").eq("case_id", case["id"]).execute().data or []
                if case_requests and all(r["status"] == "FULFILLED" for r in case_requests):
                    supabase.table("cases").update({
                        "status": "COMPLETED",
                        "updated_at": simulated_now.isoformat()
                    }).eq("id", case["id"]).execute()
                    
                    supabase.table("audit_logs").insert({
                        "case_id": case["id"],
                        "action": "CASE_COMPLETED",
                        "actor": "SYSTEM",
                        "reason": "All requests fulfilled - case auto-completed",
                        "created_at": simulated_now.isoformat()
                    }).execute()
                    
                    actions_taken.append({
                        "action": "CASE_COMPLETED",
                        "description": "Case auto-completed (all requests fulfilled)",
                        "case_id": case["id"]
                    })
        except Exception as e:
            logger.error(f"Error checking case completion: {e}")

        # 6. PROACTIVE BIRTHDAY EMAILS
        try:
            # Note: date_of_birth column is missing from DB, using deterministic generator for simulation
            clients_result = supabase.table("clients").select("id, name, email").execute()
            today = simulated_now.date()
            
            for client in (clients_result.data or []):
                # Deterministic birthday based on client ID hash to ensure consistency in simulation
                import hashlib
                h = int(hashlib.md5(client["id"].encode()).hexdigest(), 16)
                
                # Map hash to a day of the year (1-365)
                # This ensures each client has a stable "birthday" during simulation
                day_of_year = (h % 365) + 1
                
                # Check if this day of year matches "today"
                # (Simple approximation for leap years)
                current_day_of_year = today.timetuple().tm_yday
                
                if current_day_of_year == day_of_year:
                    # Today is their simulated birthday!
                    birthday_prompt = f"""Write a warm, personalized birthday greeting email for {client['name']}.
Keep it professional but heartfelt. Mention how valued they are as a client.
Sign off as "AdvisoryAI Team". Keep it to 2-3 short paragraphs."""
                    
                    birthday_body = await llm.generate_completion(birthday_prompt)
                    
                    supabase.table("email_drafts").insert({
                        "client_id": client["id"],
                        "to_email": client.get("email"),
                        "to_name": client["name"],
                        "subject": f"Happy Birthday, {client['name'].split()[0]}! 🎂",
                        "body": birthday_body,
                        "context_type": "BIRTHDAY",
                        "context_summary": "Birthday greeting",
                        "sent_at": simulated_now.isoformat(),
                        "created_at": simulated_now.isoformat()
                    }).execute()
                    
                    supabase.table("audit_logs").insert({
                        "action": "BIRTHDAY_EMAIL_SENT", "actor": "SYSTEM",
                        "reason": f"Birthday greeting sent to {client['name']}", 
                        "created_at": simulated_now.isoformat()
                    }).execute()
                    
                    actions_taken.append({
                        "action": "BIRTHDAY_EMAIL_SENT",
                        "description": f"Birthday greeting sent to {client['name']}"
                    })
        except Exception as e:
            logger.error(f"Error in birthday emails: {e}")

        # 7. PROACTIVE CLIENT RELATIONSHIP EMAILS (No recent contact)
        try:
            # Find clients without recent emails (30+ days)
            thirty_days_ago = (simulated_now - timedelta(days=30)).isoformat()
            all_clients = supabase.table("clients").select("id, name, email").execute().data or []
            
            for client in random.sample(all_clients, min(2, len(all_clients))):  # Max 2 per day
                recent_emails = supabase.table("email_drafts").select("id").eq(
                    "client_id", client["id"]
                ).gte("created_at", thirty_days_ago).limit(1).execute().data
                
                if not recent_emails:
                    checkin_prompt = f"""Write a brief, friendly check-in email for {client['name']}.
Ask how they're doing and if there's anything we can help with regarding their financial goals.
Keep it warm and not pushy. Sign off as "AdvisoryAI Team"."""
                    
                    checkin_body = await llm.generate_completion(checkin_prompt)
                    
                    supabase.table("email_drafts").insert({
                        "client_id": client["id"],
                        "to_email": client.get("email"),
                        "to_name": client["name"],
                        "subject": f"Checking In - {client['name'].split()[0]}",
                        "body": checkin_body,
                        "context_type": "RELATIONSHIP",
                        "context_summary": "Proactive check-in",
                        "sent_at": simulated_now.isoformat(),
                        "created_at": simulated_now.isoformat()
                    }).execute()
                    
                    actions_taken.append({
                        "action": "RELATIONSHIP_EMAIL_SENT",
                        "description": f"Proactive check-in sent to {client['name']}"
                    })
        except Exception as e:
            logger.error(f"Error in relationship emails: {e}")

        # 8. SIMULATE INBOUND EMAILS & REQUEST FULFILLMENT (Client Reactions)
        try:
            # A. Inbound Emails (Replies/Queries)
            if random.random() < 0.7:  # Slightly increased probability
                num_inbound = random.randint(1, 4)  # 1 to 4 emails
                all_clients = supabase.table("clients").select("id, name, email").execute().data or []
                
                # Pre-fetch clients with pending requests to prioritize them for document submissions
                clients_with_pending = supabase.table("requests").select("client_owner_id").eq("status", "PENDING").not_.is_("client_owner_id", "null").execute().data or []
                pending_client_ids = list(set([r["client_owner_id"] for r in clients_with_pending]))
                
                inbound_types = [
                    ("Document Submission", "Please find attached the documents you requested."),
                    ("Query", "I have a question about my portfolio performance."),
                    ("Meeting Request", "Could we schedule a call to discuss my retirement plans?"),
                    ("Thank You", "Thank you for your help with my ISA application."),
                    ("Update Request", "Could you provide an update on my case?")
                ]
                
                for _ in range(num_inbound):
                    if all_clients:
                        # If we have many pending requests, increase chance of "Document Submission"
                        current_inbound_types = inbound_types
                        if len(pending_client_ids) > 3 and random.random() < 0.5:
                            inbound_type, base_content = inbound_types[0] # Force Document Submission
                        else:
                            inbound_type, base_content = random.choice(inbound_types)
                        
                        # Pick a client. If document submission, try to pick one who has pending requests.
                        if inbound_type == "Document Submission" and pending_client_ids:
                            client_id = random.choice(pending_client_ids)
                            client = next((c for c in all_clients if c["id"] == client_id), random.choice(all_clients))
                        else:
                            client = random.choice(all_clients)
                        
                        # If it's a document submission, try to fulfill a request
                        fulfilled_metadata = {}
                        if inbound_type == "Document Submission":
                            pending_reqs = supabase.table("requests").select("id, title").eq("client_owner_id", client["id"]).eq("status", "PENDING").limit(1).execute().data
                            if pending_reqs:
                                req = pending_reqs[0]
                                supabase.table("requests").update({
                                    "status": "FULFILLED",
                                    "updated_at": simulated_now.isoformat()
                                }).eq("id", req["id"]).execute()
                                
                                # Add to audit log
                                supabase.table("audit_logs").insert({
                                    "request_id": req["id"],
                                    "action": "REQUEST_FULFILLED",
                                    "actor": "CLIENT",
                                    "reason": f"Client submitted: {req['title']}",
                                    "created_at": simulated_now.isoformat()
                                }).execute()
                                
                                actions_taken.append({
                                    "action": "REQUEST_FULFILLED",
                                    "description": f"{client['name']} fulfilled request: {req['title']}",
                                    "request_id": req["id"]
                                })
                                fulfilled_metadata = {"fulfilled_request_id": req["id"], "fulfilled_title": req["title"]}

                        supabase.table("email_drafts").insert({
                            "client_id": client["id"],
                            "to_email": "advisor@advisoryai.com",
                            "to_name": "AdvisoryAI Team",
                            "subject": f"Re: {inbound_type} - {client['name']}",
                            "body": f"From: {client['name']} <{client.get('email')}>\n\nHi,\n\n{base_content}\n\nBest regards,\n{client['name']}",
                            "context_type": "INBOUND",
                            "context_summary": f"Client reply: {inbound_type}",
                            "status": "SENT", # Inbound emails are 'received' (SENT to us)
                            "sent_at": simulated_now.isoformat(),
                            "created_at": simulated_now.isoformat()
                        }).execute()
                        
                        actions_taken.append({
                            "action": "INBOUND_EMAIL_RECEIVED",
                            "description": f"Email from {client['name']}: {inbound_type}"
                        })

            # B. Passive Fulfillment (Clients resolving items without an email, e.g. via portal)
            if random.random() < 0.7:  # Increased from 0.5
                # Find pending requests that are NOT already being processed in this batch's emails
                already_fulfilled_ids = [a.get("request_id") for a in actions_taken if a.get("action") == "REQUEST_FULFILLED" and a.get("request_id")]
                pending_reqs_query = supabase.table("requests").select("*, cases(client_id, title)").eq("status", "PENDING")
                if already_fulfilled_ids:
                    pending_reqs_query = pending_reqs_query.not_.in_("id", already_fulfilled_ids)
                
                pending_reqs = pending_reqs_query.limit(5).execute().data
                for req in (pending_reqs or []):
                    if random.random() < 0.7: # 70% chance (up from 60%) for each selected pending item
                        supabase.table("requests").update({
                            "status": "FULFILLED",
                            "updated_at": simulated_now.isoformat(),
                            "last_action_at": simulated_now.isoformat()
                        }).eq("id", req["id"]).execute()
                        
                        # Add to audit log for tracking
                        supabase.table("audit_logs").insert({
                            "request_id": req["id"],
                            "case_id": req.get("case_id"),
                            "action": "REQUEST_FULFILLED",
                            "actor": "CLIENT",
                            "reason": f"Request fulfilled via portal: {req['title']}",
                            "created_at": simulated_now.isoformat()
                        }).execute()
                        
                        actions_taken.append({
                            "action": "REQUEST_FULFILLED",
                            "description": f"Request fulfilled: {req['title']} (Case: {req.get('cases', {}).get('title')})",
                            "request_id": req["id"]
                        })
        except Exception as e:
            logger.error(f"Error simulating inbound/fulfillment: {e}")

        # Guaranteed feedback
        actions_taken.append({
            "action": "TIME_ADVANCED",
            "description": f"Date advanced to {simulated_now.strftime('%d %b %Y')}"
        })


        # Invalidate Cache
        global _dashboard_cache
        _dashboard_cache = {"data": None, "timestamp": None}

        return {
            "simulated_date": simulated_now.isoformat(),
            "actions_taken": len(actions_taken),
            "details": actions_taken
        }
    except Exception as e:
        logger.error(f"FATAL ERROR in /simulate/advance-day: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")


@router.post("/simulate/reset")
async def simulate_reset():
    """Reset the simulation clock to the real current time."""
    # Reset to today 9am UTC
    dt = datetime.now(timezone.utc).replace(hour=9, minute=0, second=0, microsecond=0)
    _save_simulated_now(dt)
    
    # Invalidate Cache
    global _dashboard_cache
    _dashboard_cache = {"data": None, "timestamp": None}
    
    return {
        "message": "Simulation reset successfully",
        "simulated_date": dt.isoformat()
    }
@router.get("/emails")
def get_emails(limit: int = 50):
    """Fetch history of sent/draft emails. Respects simulated date."""
    simulated_now_str = _get_simulated_now().isoformat()
    res = supabase.table("email_drafts").select("*, clients(name)").lte("created_at", simulated_now_str).order("created_at", desc=True).limit(limit).execute()
    return res.data or []

@router.get("/meetings")
def get_meetings(limit: int = 50):
    """Fetch history of meetings. Respects simulated date."""
    simulated_now_str = _get_simulated_now().isoformat()
    res = supabase.table("meetings").select("*, clients(name)").lte("created_at", simulated_now_str).order("scheduled_at", desc=True).limit(limit).execute()
    return res.data or []

@router.post("/meetings")
async def create_meeting(data: Dict[str, Any]):
    """Create a new meeting."""
    res = supabase.table("meetings").insert(data).execute()
    return res.data[0] if res.data else None

@router.get("/meetings/{meeting_id}")
def get_meeting_detail(meeting_id: str):
    """Get full meeting details including client info."""
    res = supabase.table("meetings").select(
        "*, clients(id, name, email)"
    ).eq("id", meeting_id).single().execute()
    
    if not res.data:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    meeting = res.data
    
    # Get related action items
    actions = supabase.table("action_items").select("*").eq(
        "meeting_id", meeting_id
    ).execute().data or []
    
    meeting["action_items"] = actions
    return meeting

@router.get("/exceptions")
def get_exceptions(limit: int = 50):
    """Fetch all escalated/exception requests. Respects simulated date."""
    simulated_now_str = _get_simulated_now().isoformat()
    res = supabase.table("requests").select(
        "*, cases(id, title, clients(id, name))"
    ).in_("status", ["ESCALATED", "INVALID"]).lte("created_at", simulated_now_str).order("updated_at", desc=True).limit(limit).execute()
    
    # Format for frontend
    exceptions = []
    for req in (res.data or []):
        case = req.get("cases", {}) or {}
        client = case.get("clients", {}) or {}
        exceptions.append({
            "id": req["id"],
            "title": req["title"],
            "status": req["status"],
            "case_id": req.get("case_id"),
            "case_title": case.get("title", "Unknown Case"),
            "client_name": client.get("name", "Unknown Client"),
            "retry_count": req.get("retry_count", 0),
            "updated_at": req.get("updated_at"),
            "created_at": req.get("created_at")
        })
    
    return exceptions

@router.post("/requests/{request_id}/chase")
def chase_request(request_id: str):
    """
    Manually trigger a chase for a specific request.
    """
    # Get the request
    req_res = supabase.table("requests").select("*").eq("id", request_id).single().execute()
    req = req_res.data
    
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Increment retry, schedule next chase
    new_retry = req.get("retry_count", 0) + 1
    priority = req.get("priority", "STANDARD")
    chase_days = 1 if priority == "HIGH" else 7
    next_chase = datetime.now() + timedelta(days=chase_days)
    
    supabase.table("requests").update({
        "retry_count": new_retry,
        "next_action_at": next_chase.isoformat()
    }).eq("id", request_id).execute()
    
    # Log the chase
    supabase.table("audit_logs").insert({
        "case_id": req["case_id"],
        "action": "MANUAL_CHASE",
        "actor": "ADVISOR",
        "reason": f"Manual chase #{new_retry} sent for: {req['title']}"
    }).execute()
    
    return {"status": "success", "message": f"Chase #{new_retry} sent", "next_action_at": next_chase.isoformat()}

@router.post("/requests/{request_id}/resolve")
def resolve_request(request_id: str):
    """
    Mark a request as fulfilled (resolved).
    If all requests in the case are fulfilled, mark case as COMPLETED.
    """
    req_res = supabase.table("requests").select("*").eq("id", request_id).single().execute()
    req = req_res.data
    
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    supabase.table("requests").update({
        "status": "FULFILLED"
    }).eq("id", request_id).execute()
    
    supabase.table("audit_logs").insert({
        "case_id": req["case_id"],
        "action": "REQUEST_FULFILLED",
        "actor": "ADVISOR",
        "reason": f"Request '{req['title']}' marked as fulfilled"
    }).execute()
    
    # Check if all requests in the case are now fulfilled
    case_id = req["case_id"]
    all_requests = supabase.table("requests").select("status").eq("case_id", case_id).execute()
    
    all_fulfilled = all(r["status"] == "FULFILLED" for r in all_requests.data)
    
    if all_fulfilled and len(all_requests.data) > 0:
        # Mark case as COMPLETED
        supabase.table("cases").update({
            "status": "COMPLETED"
        }).eq("id", case_id).execute()
        
        supabase.table("audit_logs").insert({
            "case_id": case_id,
            "action": "CASE_COMPLETED",
            "actor": "SYSTEM",
            "reason": "All requests fulfilled - case automatically marked as completed"
        }).execute()
        
        return {"status": "success", "message": "Request resolved - Case completed!", "case_completed": True}
    
    return {"status": "success", "message": "Request resolved"}

@router.post("/requests/{request_id}/escalate")
def escalate_request(request_id: str):
    """
    Manually escalate a request.
    """
    req_res = supabase.table("requests").select("*").eq("id", request_id).single().execute()
    req = req_res.data
    
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    supabase.table("requests").update({
        "status": "ESCALATED"
    }).eq("id", request_id).execute()
    
    supabase.table("audit_logs").insert({
        "case_id": req["case_id"],
        "action": "MANUAL_ESCALATION",
        "actor": "ADVISOR",
        "reason": f"Request '{req['title']}' manually escalated"
    }).execute()
    
    return {"status": "success", "message": "Request escalated"}


# ============================================================================
# NEW AGENTIC ADVISORY ENDPOINTS
# ============================================================================

from pydantic import Field, BaseModel
from uuid import uuid4 as generate_uuid

# --- Chat Endpoint ---

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    session_id: str
    follow_up_suggestions: Optional[List[str]] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Main conversational AI endpoint.
    Uses LLM-first SmartAgent with function calling for intelligent responses.
    """
    from agents.smart_agent import SmartAgent
    from services.llm_service import GroqService
    from services.websocket_manager import manager as ws_manager
    
    try:
        llm_service = GroqService()
        
        # Check if LLM is available
        if not llm_service.client:
            return ChatResponse(
                success=False,
                message="AI service is not configured. Please set GROQ_API_KEY environment variable.",
                session_id=req.session_id or str(generate_uuid()),
                follow_up_suggestions=["Check environment configuration"]
            )
        
        # Initialize SmartAgent with WebSocket manager for real-time updates
        smart_agent = SmartAgent(supabase, llm_service.client, ws_manager)
        session_id = req.session_id or str(generate_uuid())

        
        # Get conversation history from database for context
        conversation_history = []
        if req.session_id:
            history_result = supabase.table("conversations").select(
                "role, content"
            ).eq("session_id", req.session_id).order("created_at").limit(10).execute()
            
            if history_result.data:
                conversation_history = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in history_result.data
                ]
        
        # Process query with SmartAgent
        response = await smart_agent.process_query(
            query=req.message,
            conversation_history=conversation_history
        )
        
        # Store conversation in database
        try:
            supabase.table("conversations").insert({
                "session_id": session_id,
                "role": "user",
                "content": req.message
            }).execute()
            
            supabase.table("conversations").insert({
                "session_id": session_id,
                "role": "assistant",
                "content": response.get("message", "")
            }).execute()
        except Exception as e:
            logger.warning(f"Failed to store conversation: {e}")
        
        # Generate follow-up suggestions based on tools used
        follow_ups = _generate_follow_ups(response.get("tools_used", []))
        
        return ChatResponse(
            success=response.get("success", True),
            message=response.get("message", "I processed your request."),
            data={"tools_used": response.get("tools_used"), "raw_data": response.get("data")} if response.get("data") else None,
            session_id=session_id,
            follow_up_suggestions=follow_ups
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return ChatResponse(
            success=False,
            message=f"I encountered an error processing your request: {str(e)}",
            session_id=req.session_id or str(generate_uuid()),
            follow_up_suggestions=["Try rephrasing your question"]
        )


def _generate_follow_ups(tools_used: List[str]) -> List[str]:
    """Generate contextual follow-up suggestions based on tools used."""
    suggestions = []
    
    if not tools_used:
        return [
            "Which clients need annual reviews?",
            "Show me clients with protection gaps",
            "What action items are overdue?"
        ]
    
    # Context-aware suggestions based on what was queried
    if any("equity" in t or "investment" in t for t in tools_used):
        suggestions.extend([
            "Model a 20% market correction impact",
            "Which clients have excess cash to invest?"
        ])
    
    if any("review" in t or "overdue" in t for t in tools_used):
        suggestions.extend([
            "Schedule review meetings for these clients",
            "Draft outreach emails for overdue reviews"
        ])
    
    if any("protection" in t for t in tools_used):
        suggestions.extend([
            "Create cases for protection reviews",
            "Which clients have high-risk profiles?"
        ])
    
    if any("action" in t or "followup" in t for t in tools_used):
        suggestions.extend([
            "Draft follow-up emails for pending items",
            "What documents am I still waiting for?"
        ])
    
    # Default suggestions if none matched
    if not suggestions:
        suggestions = [
            "Tell me more about a specific client",
            "What other analysis would you like?",
            "Create a task or schedule a meeting"
        ]
    
    return suggestions[:3]




# --- Insights Endpoints ---

@router.get("/insights")
def get_insights(category: Optional[str] = None, unread_only: bool = False):
    """Get proactive insights, optionally filtered by category."""
    query = supabase.table("insights").select(
        "*, clients(name)"
    ).order("created_at", desc=True)
    
    if category:
        query = query.eq("category", category.upper())
    
    if unread_only:
        query = query.eq("is_read", False).eq("is_dismissed", False)
    
    result = query.limit(50).execute()
    
    # Format response
    insights = []
    for item in result.data or []:
        client_info = item.get("clients", {})
        insights.append({
            "id": item["id"],
            "category": item["category"],
            "title": item["title"],
            "description": item["description"],
            "recommendation": item.get("recommendation"),
            "priority": item["priority"],
            "client_id": item.get("client_id"),
            "client_name": client_info.get("name") if client_info else None,
            "metrics": item.get("metrics"),
            "affected_value": item.get("affected_value"),
            "is_read": item["is_read"],
            "is_actioned": item["is_actioned"],
            "created_at": item["created_at"]
        })
    
    return {"insights": insights, "count": len(insights)}

@router.post("/insights/generate")
async def generate_insights():
    """Trigger insight generation across all agents."""
    from agents import get_orchestrator
    
    try:
        orchestrator = get_orchestrator()
        new_insights = await orchestrator.generate_insights()
        
        # Store generated insights
        inserted = 0
        for insight in new_insights:
            try:
                supabase.table("insights").insert({
                    "client_id": insight.get("client_id"),
                    "category": insight["category"],
                    "title": insight["title"],
                    "description": insight["description"],
                    "recommendation": insight.get("recommendation"),
                    "priority": insight.get("priority", "MEDIUM"),
                    "query_type": insight.get("query_type"),
                    "source_agent": insight.get("source_agent"),
                    "metrics": insight.get("metrics")
                }).execute()
                inserted += 1
            except Exception as e:
                logger.warning(f"Failed to insert insight: {e}")
        
        return {"success": True, "generated": len(new_insights), "inserted": inserted}
    except Exception as e:
        logger.error(f"Insight generation error: {e}")
        return {"success": False, "error": str(e)}

@router.patch("/insights/{insight_id}")
def update_insight(insight_id: str, is_read: Optional[bool] = None, is_dismissed: Optional[bool] = None, is_actioned: Optional[bool] = None):
    """Update insight status (read, dismissed, actioned)."""
    update_data = {}
    if is_read is not None:
        update_data["is_read"] = is_read
    if is_dismissed is not None:
        update_data["is_dismissed"] = is_dismissed
    if is_actioned is not None:
        update_data["is_actioned"] = is_actioned
        if is_actioned:
            update_data["actioned_at"] = datetime.now().isoformat()
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update fields provided")
    
    supabase.table("insights").update(update_data).eq("id", insight_id).execute()
    return {"success": True}

# --- Action Items Endpoints ---

class ActionItemCreate(BaseModel):
    client_id: Optional[str] = None
    case_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    owner: str = "ADVISOR"
    priority: str = "MEDIUM"
    due_date: Optional[str] = None
    category: Optional[str] = None

class ActionItemUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None

@router.get("/action-items")
def get_action_items(status: Optional[str] = None, client_id: Optional[str] = None):
    """Get action items with optional filtering."""
    query = supabase.table("action_items").select(
        "*, clients(name)"
    ).order("due_date")
    
    if status:
        if status.upper() == "OPEN":
            query = query.in_("status", ["PENDING", "IN_PROGRESS", "OVERDUE"])
        else:
            query = query.eq("status", status.upper())
    
    if client_id:
        query = query.eq("client_id", client_id)
    
    result = query.limit(100).execute()
    
    items = []
    for item in result.data or []:
        client_info = item.get("clients", {})
        items.append({
            "id": item["id"],
            "title": item["title"],
            "description": item.get("description"),
            "client_id": item.get("client_id"),
            "client_name": client_info.get("name") if client_info else None,
            "case_id": item.get("case_id"),
            "status": item["status"],
            "priority": item["priority"],
            "owner": item["owner"],
            "due_date": item.get("due_date"),
            "category": item.get("category"),
            "created_at": item["created_at"],
            "completed_at": item.get("completed_at")
        })
    
    # Count by status
    status_counts = {
        "pending": len([i for i in items if i["status"] == "PENDING"]),
        "in_progress": len([i for i in items if i["status"] == "IN_PROGRESS"]),
        "overdue": len([i for i in items if i["status"] == "OVERDUE"]),
        "completed": len([i for i in items if i["status"] == "COMPLETED"])
    }
    
    return {"items": items, "counts": status_counts}

@router.post("/action-items")
def create_action_item(item: ActionItemCreate):
    """Create a new action item."""
    data = {
        "title": item.title,
        "description": item.description,
        "owner": item.owner.upper(),
        "priority": item.priority.upper(),
        "category": item.category,
        "status": "PENDING"
    }
    
    if item.client_id:
        data["client_id"] = item.client_id
    if item.case_id:
        data["case_id"] = item.case_id
    if item.due_date:
        data["due_date"] = item.due_date
    
    result = supabase.table("action_items").insert(data).execute()
    
    if result.data:
        return {"success": True, "item": result.data[0]}
    raise HTTPException(status_code=500, detail="Failed to create action item")

@router.patch("/action-items/{item_id}")
def update_action_item(item_id: str, update: ActionItemUpdate):
    """Update an action item."""
    update_data = {}
    
    if update.status:
        update_data["status"] = update.status.upper()
        if update.status.upper() == "COMPLETED":
            update_data["completed_at"] = datetime.now().isoformat()
    if update.priority:
        update_data["priority"] = update.priority.upper()
    if update.due_date:
        update_data["due_date"] = update.due_date
    if update.title:
        update_data["title"] = update.title
    if update.description:
        update_data["description"] = update.description
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update fields provided")
    
    supabase.table("action_items").update(update_data).eq("id", item_id).execute()
    return {"success": True}

@router.delete("/action-items/{item_id}")
def delete_action_item(item_id: str):
    """Delete an action item."""
    supabase.table("action_items").delete().eq("id", item_id).execute()
    return {"success": True}

# --- Meetings Endpoints ---

class MeetingCreate(BaseModel):
    client_id: str
    meeting_type: str
    title: Optional[str] = None
    scheduled_at: str
    duration_minutes: int = 60
    is_virtual: bool = False
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    agenda: Optional[List[str]] = None

@router.get("/meetings")
def get_meetings(upcoming: bool = False, client_id: Optional[str] = None):
    """Get meetings with optional filtering."""
    query = supabase.table("meetings").select(
        "*, clients(name)"
    ).order("scheduled_at", desc=not upcoming)
    
    if upcoming:
        query = query.gte("scheduled_at", datetime.now().isoformat())
        query = query.in_("status", ["SCHEDULED", "CONFIRMED"])
    
    if client_id:
        query = query.eq("client_id", client_id)
    
    result = query.limit(50).execute()
    
    meetings = []
    for m in result.data or []:
        client_info = m.get("clients", {})
        meetings.append({
            "id": m["id"],
            "client_id": m["client_id"],
            "client_name": client_info.get("name") if client_info else None,
            "meeting_type": m["meeting_type"],
            "status": m["status"],
            "title": m.get("title"),
            "scheduled_at": m["scheduled_at"],
            "duration_minutes": m.get("duration_minutes", 60),
            "is_virtual": m.get("is_virtual", False),
            "location": m.get("location"),
            "notes": m.get("notes"),
            "created_at": m["created_at"]
        })
    
    return {"meetings": meetings}

@router.post("/meetings")
def create_meeting(meeting: MeetingCreate):
    """Create a new meeting."""
    data = {
        "client_id": meeting.client_id,
        "meeting_type": meeting.meeting_type.upper(),
        "title": meeting.title,
        "scheduled_at": meeting.scheduled_at,
        "duration_minutes": meeting.duration_minutes,
        "is_virtual": meeting.is_virtual,
        "location": meeting.location,
        "meeting_link": meeting.meeting_link,
        "agenda": meeting.agenda,
        "status": "SCHEDULED"
    }
    
    result = supabase.table("meetings").insert(data).execute()
    
    if result.data:
        return {"success": True, "meeting": result.data[0]}
    raise HTTPException(status_code=500, detail="Failed to create meeting")

@router.patch("/meetings/{meeting_id}")
def update_meeting(meeting_id: str, status: Optional[str] = None, notes: Optional[str] = None):
    """Update meeting status or notes."""
    update_data = {}
    
    if status:
        update_data["status"] = status.upper()
        if status.upper() == "COMPLETED":
            update_data["completed_at"] = datetime.now().isoformat()
    if notes:
        update_data["notes"] = notes
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update fields provided")
    
    supabase.table("meetings").update(update_data).eq("id", meeting_id).execute()
    return {"success": True}

# --- Email Drafts Endpoints ---

class DraftRequest(BaseModel):
    client_id: Optional[str] = None
    meeting_id: Optional[str] = None
    context_type: str = "FOLLOW_UP"
    tone: str = "FORMAL"

@router.get("/drafts")
def get_drafts(status: Optional[str] = None):
    """Get email drafts."""
    query = supabase.table("email_drafts").select(
        "*, clients(name)"
    ).order("created_at", desc=True)
    
    if status:
        query = query.eq("status", status.upper())
    
    # Check if we are in simulated mode
    simulated_now_str = _get_simulated_now().isoformat()
    query = query.lte("created_at", simulated_now_str)
    
    result = query.limit(20).execute()
    
    drafts = []
    for d in result.data or []:
        client_info = d.get("clients", {})
        drafts.append({
            "id": d["id"],
            "client_id": d.get("client_id"),
            "client_name": client_info.get("name") if client_info else None,
            "subject": d["subject"],
            "body": d["body"],
            "tone": d.get("tone"),
            "status": d["status"],
            "to_email": d["to_email"],
            "to_name": d.get("to_name"),
            "context_type": d.get("context_type"),
            "created_at": d["created_at"]
        })
    
    return drafts # Return list directly for frontend consistency

@router.post("/drafts")
async def generate_draft(req: DraftRequest):
    """Generate an email draft using AI."""
    from agents.orchestrator import get_orchestrator
    from agents.base import AgentQuery, QueryIntent
    
    orchestrator = get_orchestrator()
    
    # Build context for the follow-up agent
    query = AgentQuery(
        raw_query=f"Draft a {req.tone.lower()} {req.context_type.lower()} email",
        intent=QueryIntent.DRAFT_EMAIL,
        entities={"client_id": req.client_id, "meeting_id": req.meeting_id},
        context={"tone": req.tone, "context_type": req.context_type}
    )
    
    followup_agent = orchestrator.agents.get(orchestrator.agents.__class__.__dict__.get("FOLLOWUP"))
    if not followup_agent:
        from agents.followup_agent import FollowupAgent
        followup_agent = FollowupAgent(supabase, groq_service)
    
    response = await followup_agent.process(query)
    
    return {
        "success": response.success,
        "draft": response.data,
        "message": response.message
    }

@router.patch("/drafts/{draft_id}")
def update_draft(draft_id: str, body: Optional[str] = None, subject: Optional[str] = None, status: Optional[str] = None):
    """Update a draft."""
    update_data = {}
    
    if body:
        update_data["body"] = body
        update_data["edited_at"] = datetime.now().isoformat()
    if subject:
        update_data["subject"] = subject
    if status:
        update_data["status"] = status.upper()
        if status.upper() == "SENT":
            update_data["sent_at"] = datetime.now().isoformat()
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update fields provided")
    
    supabase.table("email_drafts").update(update_data).eq("id", draft_id).execute()
    return {"success": True}

# --- Unified Search Endpoint ---

@router.get("/search")
def unified_search(q: str):
    """Search across clients, cases, meetings, and action items."""
    if not q or len(q) < 2:
        return {"results": []}
    
    results = []
    
    # Search clients
    clients = supabase.table("clients").select("id, name, email").ilike("name", f"%{q}%").limit(5).execute()
    for c in clients.data or []:
        results.append({
            "type": "client",
            "id": c["id"],
            "title": c["name"],
            "subtitle": c.get("email"),
            "url": f"/clients/{c['id']}"
        })
    
    # Search cases
    cases = supabase.table("cases").select("id, title, status, clients(name)").ilike("title", f"%{q}%").limit(5).execute()
    for c in cases.data or []:
        client_name = c.get("clients", {}).get("name", "Unknown") if c.get("clients") else "Unknown"
        results.append({
            "type": "case",
            "id": c["id"],
            "title": c["title"],
            "subtitle": f"{client_name} • {c['status']}",
            "url": f"/cases/{c['id']}"
        })
    
    # Search action items
    actions = supabase.table("action_items").select("id, title, status, clients(name)").ilike("title", f"%{q}%").limit(5).execute()
    for a in actions.data or []:
        client_name = a.get("clients", {}).get("name", "") if a.get("clients") else ""
        results.append({
            "type": "action",
            "id": a["id"],
            "title": a["title"],
            "subtitle": f"{client_name} • {a['status']}",
            "url": f"/actions/{a['id']}"
        })
    
    return {"results": results, "count": len(results)}

# --- Client Profile Endpoints ---

@router.get("/clients/{client_id}/profile")
def get_client_profile(client_id: str):
    """Get detailed client profile with investments and protection."""
    # Get client
    client = supabase.table("clients").select("*").eq("id", client_id).single().execute()
    if not client.data:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get profile
    profile = supabase.table("client_profiles").select("*").eq("client_id", client_id).execute()
    
    # Get investments
    investments = supabase.table("investments").select("*").eq("client_id", client_id).execute()
    
    # Get protection
    protection = supabase.table("protection_policies").select("*").eq("client_id", client_id).eq("is_active", True).execute()
    
    # Get recent meetings
    meetings = supabase.table("meetings").select("*").eq("client_id", client_id).order("scheduled_at", desc=True).limit(5).execute()
    
    # Get open action items
    actions = supabase.table("action_items").select("*").eq("client_id", client_id).in_("status", ["PENDING", "IN_PROGRESS", "OVERDUE"]).execute()
    
    # Calculate totals
    total_investments = sum(inv.get("current_value", 0) or 0 for inv in investments.data or [])
    
    return {
        "client": client.data,
        "profile": profile.data[0] if profile.data else None,
        "investments": {
            "items": investments.data or [],
            "total_value": total_investments
        },
        "protection": protection.data or [],
        "recent_meetings": meetings.data or [],
        "open_actions": actions.data or []
    }

@router.get("/clients/{client_id}/analysis")
async def get_client_analysis(client_id: str):
    """Get AI-powered analysis for a specific client."""
    from agents import get_orchestrator
    
    # Get client name
    client = supabase.table("clients").select("name").eq("id", client_id).single().execute()
    if not client.data:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client_name = client.data["name"]
    
    orchestrator = get_orchestrator()
    
    # Run multiple analyses
    analyses = []
    
    queries = [
        f"Check equity allocation for {client_name}",
        f"Check ISA allowance for {client_name}",
        f"Check protection gaps for {client_name}",
    ]
    
    for query in queries:
        try:
            response = await orchestrator.process_query(query)
            if response.success and response.data:
                analyses.append({
                    "type": response.query_type.value,
                    "message": response.message,
                    "data": response.data
                })
        except Exception as e:
            logger.warning(f"Analysis failed for {query}: {e}")
    
    return {
        "client_id": client_id,
        "client_name": client_name,
        "analyses": analyses
    }


# --- Client Management Endpoints ---

class ClientCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

@router.get("/clients")
def get_clients():
    """List all clients."""
    result = supabase.table("clients").select("*").order("name").execute()
    return result.data

@router.post("/clients")
def create_client(client: ClientCreate):
    """Create a new client."""
    # Check for duplicate email
    existing = supabase.table("clients").select("id").eq("email", client.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Client with this email already exists")

    result = supabase.table("clients").insert({
        "name": client.name,
        "email": client.email,
        "phone": client.phone
    }).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create client")
        
    return result.data[0]

@router.patch("/clients/{client_id}")
def update_client(client_id: str, client: ClientUpdate):
    """Update a client."""
    update_data = {k: v for k, v in client.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = supabase.table("clients").update(update_data).eq("id", client_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Client not found")
        
    return result.data[0]

# --- Provider Management Endpoints ---

class ProviderCreate(BaseModel):
    name: str
    email: str
    portal_url: Optional[str] = None
    standard_response_days: int = 10

class ProviderUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    portal_url: Optional[str] = None
    standard_response_days: Optional[int] = None

@router.get("/providers")
def get_providers():
    """List all providers."""
    result = supabase.table("providers").select("*").order("name").execute()
    return result.data

@router.post("/providers")
def create_provider(provider: ProviderCreate):
    """Create a new provider."""
    # Check for duplicate name (providers might share generic emails)
    existing = supabase.table("providers").select("id").eq("name", provider.name).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Provider with this name already exists")

    result = supabase.table("providers").insert({
        "name": provider.name,
        "email": provider.email,
        "portal_url": provider.portal_url,
        "standard_response_days": provider.standard_response_days
    }).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create provider")
        
    return result.data[0]

@router.patch("/providers/{provider_id}")
def update_provider(provider_id: str, provider: ProviderUpdate):
    """Update a provider."""
    update_data = {k: v for k, v in provider.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = supabase.table("providers").update(update_data).eq("id", provider_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Provider not found")
        
    return result.data[0]

