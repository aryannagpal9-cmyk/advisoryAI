import requests
import json
import time

URL = "http://localhost:8000/api/simulate/advance-day"

def test_advance():
    print("Calling /simulate/advance-day...")
    try:
        resp = requests.post(URL, verify=False)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            # Summarize output
            # print(json.dumps(data, indent=2))
            actions = data.get("details", [])
            
            action_counts = {}
            for a in actions:
                act = a.get("action", "UNKNOWN")
                action_counts[act] = action_counts.get(act, 0) + 1
                if act == "SIM_ERROR":
                    print(f"  ERROR: {a.get('description')}")
            
            for act, count in action_counts.items():
                print(f"  {act}: {count}")
            
            print(f"  Total Actions: {len(actions)}")
            
            if action_counts.get("CHASE_SENT") or action_counts.get("CHASE_EMAIL_SENT"):
                print("\nSUCCESS: Chase actions observed!")
                return True
            elif action_counts.get("CASE_CREATED"):
                print("\nCase created, check for chase in next runs.")
                return False
            else:
                print("\nContinuing simulation...")
                return False
        else:
            print("FAILED: Server returned error")
            print(resp.text)
            return False
    except Exception as e:
        print(f"Request Failed: {e}")
        return False

if __name__ == "__main__":
    for i in range(5):
        print(f"\n--- Attempt {i+1} ---")
        if test_advance():
            break
        time.sleep(1)
