
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

async def test_fulfillment():
    load_dotenv()
    supabase = get_supabase()
    llm = GroqService()
    agent = SmartAgent(supabase, llm.client)
    
    simulated_now = datetime.now(timezone.utc)
    actions_taken = []
    
    print("Testing Inbound Emails...")
    num_inbound = 2
    all_clients = supabase.table("clients").select("id, name, email").execute().data or []
    
    clients_with_pending = supabase.table("requests").select("client_owner_id").eq("status", "PENDING").not_.is_("client_owner_id", "null").execute().data or []
    pending_client_ids = list(set([r["client_owner_id"] for r in clients_with_pending]))
    print(f"Pending client IDs: {pending_client_ids}")

    for _ in range(num_inbound):
        inbound_type = "Document Submission"
        if pending_client_ids:
            client_id = pending_client_ids[0] # Pick the first one for testing
            client = next((c for c in all_clients if c["id"] == client_id), None)
            if client:
                print(f"Attempting fulfillment for {client['name']}")
                pending_reqs = supabase.table("requests").select("id, title").eq("client_owner_id", client["id"]).eq("status", "PENDING").limit(1).execute().data
                if pending_reqs:
                    req = pending_reqs[0]
                    print(f"Fulfilling: {req['title']}")
                    res = supabase.table("requests").update({"status": "FULFILLED"}).eq("id", req["id"]).execute()
                    print(f"Update result: {res.data}")
                    actions_taken.append({
                        "action": "REQUEST_FULFILLED",
                        "request_id": req["id"]
                    })

    print(f"Actions taken match REQUEST_FULFILLED: {[a for a in actions_taken if a.get('action') == 'REQUEST_FULFILLED']}")
    
    print("\nTesting Passive Fulfillment...")
    already_fulfilled_ids = [a.get("request_id") for a in actions_taken if a.get("action") == "REQUEST_FULFILLED" and a.get("request_id")]
    print(f"Already fulfilled IDs: {already_fulfilled_ids}")
    
    pending_reqs_query = supabase.table("requests").select("*, cases(client_id, title)").eq("status", "PENDING")
    if already_fulfilled_ids:
        pending_reqs_query = pending_reqs_query.not_.in_("id", already_fulfilled_ids)
    
    pending_reqs = pending_reqs_query.limit(5).execute().data
    print(f"Potential passive fulfillments: {len(pending_reqs or [])}")
    for req in (pending_reqs or []):
        print(f"Passively fulfilling: {req['title']}")
        res = supabase.table("requests").update({"status": "FULFILLED"}).eq("id", req["id"]).execute()
        print(f"Passive result: {res.data}")

if __name__ == "__main__":
    asyncio.run(test_fulfillment())

