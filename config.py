import os
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

class Config:
    # 1. API Credentials
    MAQSAM_BASE_URL = os.getenv("MAQSAM_BASE_URL", "api.mq.maqsam.com")
    MAQSAM_ACCESS_KEY_ID = os.getenv("MAQSAM_ACCESS_KEY_ID")
    MAQSAM_ACCESS_SECRET = os.getenv("MAQSAM_ACCESS_SECRET")

    # 2. Server Config
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 80))
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

    # 3. Database
    DB_PATH = os.getenv("DB_PATH", "database/crm_queue.db")

    # 4. Storage
    RECORDINGS_SAVE_DIR = os.getenv("RECORDINGS_SAVE_DIR", "storage/recordings/")

    # 5. Worker Config
    DOWNLOAD_TIMEOUT_SECONDS = int(os.getenv("DOWNLOAD_TIMEOUT_SECONDS", 15))
    MAX_DOWNLOAD_RETRIES = int(os.getenv("MAX_DOWNLOAD_RETRIES", 5))

# Ensure required directories exist when the app starts
os.makedirs(os.path.dirname(Config.DB_PATH), exist_ok=True)
os.makedirs(Config.RECORDINGS_SAVE_DIR, exist_ok=True)