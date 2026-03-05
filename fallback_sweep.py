import requests
import sqlite3
from config import Config

def run_daily_fallback_sweep():
    """Audits the Maqsam V2 Calls API to catch any missed webhooks."""
    
    print("Starting daily webhook fallback sweep...")
    url = f"https://{Config.MAQSAM_BASE_URL}/v2/calls"
    auth = (Config.MAQSAM_ACCESS_KEY_ID, Config.MAQSAM_ACCESS_SECRET)
    
    try:
        response = requests.get(url, auth=auth, timeout=Config.DOWNLOAD_TIMEOUT_SECONDS)
        response.raise_for_status()
        calls_data = response.json() 
    except requests.exceptions.RequestException as e:
        print(f"🚨 Failed to fetch calls index: {e}")
        return

    conn = sqlite3.connect(Config.DB_PATH)
    c = conn.cursor()
    missed_count = 0

    # Ensure calls_data structure matches Maqsam's actual JSON response (assuming 'data' array)
    for call in calls_data.get('data', []):
        call_id = call.get('id')
        
        if not call_id:
            continue
            
        # Check if this call ID exists anywhere in our local database
        c.execute("SELECT 1 FROM pending_recordings WHERE call_id=?", (call_id,))
        exists = c.fetchone()
        
        if not exists:
            # We missed the webhook! Insert it as pending to be caught by worker.py
            c.execute("INSERT INTO pending_recordings (call_id, status, retry_count) VALUES (?, ?, ?)", 
                      (call_id, "pending", 0))
            missed_count += 1
            print(f"🕸️ Caught missing Call ID: {call_id}")

    conn.commit()
    conn.close()
    print(f"Sweep complete. Queued {missed_count} missing recordings.")

if __name__ == '__main__':
    run_daily_fallback_sweep()