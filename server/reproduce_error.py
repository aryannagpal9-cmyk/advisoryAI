
import os
import sys
import asyncio
import json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Add the current directory to sys.path to import local modules
sys.path.append(os.getcwd())

from db.supabase import get_supabase
from services.llm_service import GroqService
from agents.smart_agent import SmartAgent

async def test_advance_day():
    load_dotenv()
    supabase = get_supabase()
    llm = GroqService()
    agent = SmartAgent(supabase, llm.client)
    
    # Mocking the _get_simulated_now and _advance_simulated_now from api.py
    SIM_STATE_FILE = "simulation_state.json"
    
    def _get_simulated_now():
        if not os.path.exists(SIM_STATE_FILE):
            dt = datetime.now(timezone.utc).replace(hour=9, minute=0, second=0, microsecond=0)
            return dt
        try:
            with open(SIM_STATE_FILE, "r") as f:
                data = json.load(f)
                return datetime.fromisoformat(data["current_date"])
        except:
            dt = datetime.now(timezone.utc).replace(hour=9, minute=0, second=0, microsecond=0)
            return dt

    def _save_simulated_now(dt):
        with open(SIM_STATE_FILE, "w") as f:
            json.dump({"current_date": dt.isoformat()}, f)

    def _advance_simulated_now():
        now = _get_simulated_now()
        new_now = now + timedelta(days=1)
        _save_simulated_now(new_now)
        return new_now

    print("Advancing day...")
    simulated_now = _advance_simulated_now()
    print(f"New simulated time: {simulated_now}")
    
    # 4. MASTER CHASE LOOP
    print("Checking daily chases...")
    pending = supabase.table("requests").select("*, cases(id, title, clients(id, name, email))").eq("status", "PENDING").execute()
    
    for req in (pending.data or []):
        if req.get("next_action_at"):
            try:
                next_action_str = req["next_action_at"].replace('Z', '+00:00')
                next_action = datetime.fromisoformat(next_action_str)
                if next_action.tzinfo is None:
                    next_action = next_action.replace(tzinfo=timezone.utc)
                
                if next_action <= simulated_now:
                    print(f"Triggering chase for request: {req.get('id')}")
                    chase_res = await agent._trigger_chase(req["id"], simulated_now=simulated_now)
                    print(f"Chase result: {chase_res}")
            except Exception as e:
                print(f"Error in chase logic for request {req.get('id')}: {e}")
                raise e

if __name__ == "__main__":
    asyncio.run(test_advance_day())
