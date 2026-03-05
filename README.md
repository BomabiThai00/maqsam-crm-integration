# Maqsam Click-to-Call CRM Integration

This repository contains decoupled microservice for integrating a CRM with Maqsam's telephony systems.

It handles initiating outbound calls, catching call-completion webhooks via a local database queue, and asynchronously downloading the call recordings for CRM mapping. This event-driven architecture ensures zero data loss during network hiccups or API rate limits.

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your local machine:

* **Python 3.8+**
* **ngrok** (for exposing the local webhook receiver to the internet during development)
* A **Maqsam Account** with Access Key ID and Secret (found in Account Settings -> API Credentials).

---

## 🛠️ Local Setup

**1. Clone the repository and navigate into the directory:**

```bash
git clone https://github.com/BomabiThai00/maqsam-crm-integration
cd maqsam-crm-integration

```

**2. Create and activate a virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

```

**3. Install dependencies:**

```bash
pip install flask requests python-dotenv

```

**4. Configure Environment Variables:**
Create a file named `.env` in the root directory and add your credentials:

```env
# 1. Maqsam API Credentials  # from maqsam portal under API_credentials
MAQSAM_BASE_URL=api.{base_url}
MAQSAM_ACCESS_KEY_ID=your_access_key_here 
MAQSAM_ACCESS_SECRET=your_secret_key_here

# 2. Server Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
ENVIRONMENT=development

# 3. Database & Storage Paths
DB_PATH=database/crm_queue.db
RECORDINGS_SAVE_DIR=storage/recordings/

# 4. Worker Configuration
DOWNLOAD_TIMEOUT_SECONDS=15
MAX_DOWNLOAD_RETRIES=5

```

---

## 🚀 End-to-End Testing Guide

To test the full lifecycle, you will need to open **three separate terminal windows**.

### Step 1: Start the Webhook Receiver (Terminal 1)

This Flask server listens for the end-of-call payload from Maqsam.

```bash
source venv/bin/activate
python app.py

```

*Expected Output: `🚀 Starting webhook server on port 5000...*`

### Step 2: Expose the Server with ngrok (Terminal 2)

Maqsam cannot send webhooks to `localhost`. We use ngrok to create a secure, public URL.

```bash
ngrok http 5000

```

* **Action Required:** Copy the `Forwarding` HTTPS URL that ngrok generates (e.g., `https://1234-abcd.ngrok-free.app`).
* Go to your **Maqsam Dashboard** -> **Notify API**.
* Set the URL to your ngrok address + the endpoint route: `https://1234-abcd.ngrok-free.app/webhook`.
* Set the Method to **POST** and save.

### Step 3: Trigger a Call (Terminal 3)

Make sure your Maqsam agent dialer is open and online. Open `trigger_call.py` and temporarily uncomment the function call at the bottom, inserting your email and a valid test phone number. Then run:

```bash
source venv/bin/activate
python trigger_call.py

```

* You should see your dialer instantly start calling the test number.
* Answer the call, wait 5 seconds, and hang up.

### Step 4: Verify the Webhook

Look back at **Terminal 1** (your Flask server). Within a few seconds of hanging up, you should see a message indicating the webhook was received and the Call ID was safely queued in the local SQLite database:
`📥 Queued Call ID call_123456789 for background download.`

### Step 5: Run the Background Worker (Terminal 3)

Now that the ID is queued, run the worker to download the recording.

```bash
python worker.py

```

*Expected Output: The worker will detect the pending ID, download the `.mp3` file into `storage/recordings/`, and update the database status to `completed`.*

### Step 6: Test the Fallback Sweep (Terminal 3)

To ensure no webhooks were missed while your server was off, run the daily sweep:

```bash
python fallback_sweep.py

```

*Expected Output: It will audit the API index against your local database and queue any missing Call IDs.*

---

## 📂 Project Structure

```text
maqsam-crm-integration/
├── app.py                 # Flask webhook receiver
├── config.py              # Strict typing and env var loader
├── fallback_sweep.py      # Daily cron job to catch missed webhooks
├── trigger_call.py        # CRM click-to-call initiator
├── worker.py              # Background job to download and map audio
├── .env                   # Environment variables (ignored by git)
├── .gitignore             # Git ignore rules
├── database/              # SQLite queue storage
└── storage/recordings/    # Downloaded MP3 files

```

---

This should give your client's engineering team a completely frictionless setup experience.

As a final housekeeping step, would you like me to generate the `requirements.txt` file so you can include that in the repository as well?
