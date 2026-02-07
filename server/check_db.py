
import os
from db.supabase import get_supabase
from dotenv import load_dotenv

def check_requests():
    load_dotenv()
    supabase = get_supabase()
    
    # Check pending requests
    res = supabase.table("requests").select("id, status, client_owner_id, owner_type").eq("status", "PENDING").execute()
    pending = res.data or []
    
    # Check fulfilled requests
    res_f = supabase.table("requests").select("id, status").eq("status", "FULFILLED").execute()
    fulfilled = res_f.data or []
    
    print(f"Total Pending Requests: {len(pending)}")
    print(f"Total Fulfilled Requests: {len(fulfilled)}")
    
    has_owner = [r for r in pending if r.get("client_owner_id")]
    print(f"Pending Requests with client_owner_id: {len(has_owner)}")
    
    # Check recent fulfillment audit logs
    res_logs = supabase.table("audit_logs").select("reason, created_at").eq("action", "REQUEST_FULFILLED").order("created_at", desc=True).limit(20).execute()
    logs = res_logs.data or []
    if logs:
        print("\nRecent Fulfillment Actions:")
        for log in logs:
            print(f"- {log['created_at']}: {log['reason']}")



if __name__ == "__main__":
    check_requests()
