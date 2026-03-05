import os
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# 1. Fetch and strictly validate required credentials at startup
_key_id = os.getenv("MAQSAM_ACCESS_KEY_ID")
_secret = os.getenv("MAQSAM_ACCESS_SECRET")

if _key_id is None or _secret is None:
    raise ValueError("🚨 Missing MAQSAM_ACCESS_KEY_ID or MAQSAM_ACCESS_SECRET in .env file.")

class Config:
    # Explicit type annotations guarantee to the linter that these are strings
    MAQSAM_BASE_URL: str = os.getenv("MAQSAM_BASE_URL", "api.maqsam.com")
    MAQSAM_ACCESS_KEY_ID: str = _key_id
    MAQSAM_ACCESS_SECRET: str = _secret

    # 2. Server Config
    FLASK_HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # 3. Database
    DB_PATH: str = os.getenv("DB_PATH", "database/crm_queue.db")

    # 4. Storage
    RECORDINGS_SAVE_DIR: str = os.getenv("RECORDINGS_SAVE_DIR", "storage/recordings/")

    # 5. Worker Config
    DOWNLOAD_TIMEOUT_SECONDS: int = int(os.getenv("DOWNLOAD_TIMEOUT_SECONDS", "15"))
    MAX_DOWNLOAD_RETRIES: int = int(os.getenv("MAX_DOWNLOAD_RETRIES", "5"))

# Ensure required directories exist
os.makedirs(os.path.dirname(Config.DB_PATH), exist_ok=True)
os.makedirs(Config.RECORDINGS_SAVE_DIR, exist_ok=True)