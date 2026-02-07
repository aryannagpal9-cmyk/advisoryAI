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
            
            chases = [a for a in actions if "CHASE" in a.get("action", "")]
            emails = [a for a in actions if "EMAIL" in a.get("action", "")]
            moms = [a for a in actions if "MOM" in a.get("action", "")]
            cases = [a for a in actions if "CASE_CREATED" in a.get("action", "")]
            
            print(f"  Cases Created: {len(cases)}")
            print(f"  Chases Sent: {len(chases)}")
            print(f"  Emails Sent: {len(emails)}")
            print(f"  MoMs Sent: {len(moms)}")
            print(f"  Total Actions: {len(actions)}")
            
            if len(chases) > 0:
                print("\nSUCCESS: Chase actions observed!")
                return True
            elif len(cases) > 0:
                print("\nWARNING: Cases created but NO chase sent? Check agent logic.")
                return False
            else:
                print("\nNo cases created this run. Try again.")
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
