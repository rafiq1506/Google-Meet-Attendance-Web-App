import os
from pathlib import Path
from dotenv import load_dotenv

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env in project root
load_dotenv(BASE_DIR / ".env")

# File & Directory Paths from .env
REPORTS_DIR = BASE_DIR / os.getenv("REPORTS_DIR", "reports")
DATA_DIR = BASE_DIR / "data"
CREDENTIALS_FILE = BASE_DIR / os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
TOKEN_FILE = BASE_DIR / os.getenv("GOOGLE_TOKEN_FILE", "token.json")
roster_env = os.getenv("DEFAULT_ROSTER_FILE", "").strip()
DEFAULT_ROSTER_FILE = (BASE_DIR / roster_env) if roster_env else None

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# Google Meet API Scopes
SCOPES = [
    "https://www.googleapis.com/auth/meetings.space.readonly",
    "https://www.googleapis.com/auth/meetings.space.created",
]

# Google OAuth Credentials (if supplied directly in .env)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "").strip()
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN", "").strip()

# Attendance Criteria Defaults from .env
DEFAULT_MIN_DURATION_MINUTES = float(os.getenv("DEFAULT_MIN_DURATION_MINUTES", "30.0"))
DEFAULT_MIN_ATTENDANCE_PERCENT = float(os.getenv("DEFAULT_MIN_ATTENDANCE_PERCENT", "60.0"))

# Excel Export Preferences
EXCEL_REPORT_PREFIX = os.getenv("EXCEL_REPORT_PREFIX", "attendance_report")
APPEND_TIMESTAMP_TO_EXCEL = os.getenv("APPEND_TIMESTAMP_TO_EXCEL", "True").lower() in ("true", "1", "yes")
