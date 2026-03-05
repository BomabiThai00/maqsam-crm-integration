from flask import Flask, request, jsonify
import sqlite3
from config import Config

app = Flask(__name__)

def init_db():
    """Initializes the SQLite database with our robust queue schema."""
    conn = sqlite3.connect(Config.DB_PATH)
    c = conn.cursor()
    # Adding a retry_count ensures we don't try to download broken files forever
    c.execute('''CREATE TABLE IF NOT EXISTS pending_recordings (
                    call_id TEXT PRIMARY KEY, 
                    status TEXT,
                    retry_count INTEGER DEFAULT 0
                 )''')
    conn.commit()
    conn.close()

@app.route('/', methods=['POST'])
def handle_maqsam_notify():
    """Catches the Maqsam Notify API payload and queues the Call ID."""
    
    # Extract the ID from the x-www-form-urlencoded payload
    call_id = request.form.get('id')

    if not call_id:
        return jsonify({"error": "Missing Call ID"}), 400

    conn = sqlite3.connect(Config.DB_PATH)
    c = conn.cursor()
    
    try:
        # Insert the call into our queue with a 'pending' status
        c.execute("INSERT INTO pending_recordings (call_id, status, retry_count) VALUES (?, ?, ?)", 
                  (call_id, "pending", 0))
        conn.commit()
        print(f"📥 Queued Call ID {call_id} for background download.")
    except sqlite3.IntegrityError:
        # If the ID is already in the database, we just ignore it
        print(f"⚡ Call ID {call_id} is already in the queue.")
    except Exception as e:
        print(f"🚨 Database Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        conn.close()

    # Always return 200 quickly so Maqsam knows we received it
    return jsonify({"message": "Webhook queued successfully"}), 200

if __name__ == '__main__':
    init_db()
    print(f"🚀 Starting webhook server on port {Config.FLASK_PORT}...")
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT)