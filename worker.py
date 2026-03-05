import requests
import sqlite3
import os
import time
from config import Config

def process_recording_queue():
    """Fetches pending calls from the DB, downloads the audio, and maps it."""
    
    auth = (Config.MAQSAM_ACCESS_KEY_ID, Config.MAQSAM_ACCESS_SECRET)
    conn = sqlite3.connect(Config.DB_PATH)
    c = conn.cursor()

    # 1. Fetch pending IDs that haven't exceeded the max retry limit
    c.execute("SELECT call_id, retry_count FROM pending_recordings WHERE status='pending'")
    pending_calls = c.fetchall()

    if not pending_calls:
        print("No pending recordings to process.")
        conn.close()
        return

    for row in pending_calls:
        call_id = row[0]
        retry_count = row[1]
        
        # Check if we've hit the maximum retries
        if retry_count >= Config.MAX_DOWNLOAD_RETRIES:
            print(f"❌ Call ID {call_id} exceeded max retries. Marking as failed.")
            c.execute("UPDATE pending_recordings SET status='failed' WHERE call_id=?", (call_id,))
            conn.commit()
            continue

        download_url = f"https://{Config.MAQSAM_BASE_URL}/v1/recording/{call_id}"

        try:
            # 2. Attempt the download
            print(f"Attempting download for {call_id} (Attempt {retry_count + 1})...")
            response = requests.get(download_url, auth=auth, timeout=Config.DOWNLOAD_TIMEOUT_SECONDS)

            # 3. Handle Success: Save file and update database
            if response.status_code == 200:
                file_path = os.path.join(Config.RECORDINGS_SAVE_DIR, f"recording_{call_id}.mp3")
                with open(file_path, "wb") as f:
                    f.write(response.content)

                # Update status to completed
                c.execute("UPDATE pending_recordings SET status='completed' WHERE call_id=?", (call_id,))
                conn.commit()
                print(f"✅ Success: Recording mapped and saved to {file_path}")

            # 4. Handle Processing Delay (Not Ready Yet)
            elif response.status_code == 400:
                error_msg = response.json().get("message", "Not ready")
                print(f"⏳ ID {call_id} not ready ({error_msg}). Incrementing retry count.")
                c.execute("UPDATE pending_recordings SET retry_count = retry_count + 1 WHERE call_id=?", (call_id,))
                conn.commit()

            # 5. Handle Authentication Errors
            elif response.status_code == 401:
                print("🚨 Unauthorized! Check your API credentials in the .env file.")
                break # Stop processing to prevent locking out the account
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Network error while downloading {call_id}: {e}")

    conn.close()

if __name__ == '__main__':
    # In production, you would run this via a Cron Job (e.g., every 5 minutes)
    # For testing, we just run it once.
    print("Starting background worker...")
    process_recording_queue()
    print("Worker cycle complete.")