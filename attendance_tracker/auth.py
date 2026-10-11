import os
import sys
from pathlib import Path
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import json
from attendance_tracker.config import (
    SCOPES,
    CREDENTIALS_FILE,
    TOKEN_FILE,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_PROJECT_ID
)


def get_credentials() -> Credentials:
    """
    Handles Google OAuth 2.0 authentication.
    - Loads existing token from GOOGLE_TOKEN_JSON env var or token.json file.
    - Refreshes expired token if refresh token exists.
    - Initiates local browser OAuth flow using credentials.json or .env variables.
    """
    creds: Optional[Credentials] = None

    # 1. Load directly from environment variables (Safest for Render/Cloud - NO JSON FILES NEEDED!)
    refresh_token_env = os.getenv("GOOGLE_REFRESH_TOKEN", "").strip()
    client_id_env = GOOGLE_CLIENT_ID or os.getenv("GOOGLE_CLIENT_ID", "").strip()
    client_secret_env = GOOGLE_CLIENT_SECRET or os.getenv("GOOGLE_CLIENT_SECRET", "").strip()

    if refresh_token_env and client_id_env and client_secret_env:
        try:
            creds = Credentials(
                token=None,
                refresh_token=refresh_token_env,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id_env,
                client_secret=client_secret_env,
                scopes=SCOPES
            )
            creds.refresh(Request())
            return creds
        except Exception as e:
            print(f"[!] Warning: Failed to initialize credentials from GOOGLE_REFRESH_TOKEN ({e})")
            creds = None

    # 2. Load cached token from GOOGLE_TOKEN_JSON environment variable if set
    token_json_env = os.getenv("GOOGLE_TOKEN_JSON", "").strip()
    if token_json_env:
        try:
            token_data = json.loads(token_json_env)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        except Exception as e:
            print(f"[!] Warning: Failed to parse GOOGLE_TOKEN_JSON from env ({e})")
            creds = None

    # 3. Load cached token from token.json file if available
    if not creds and TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except Exception as e:
            print(f"[!] Warning: Failed to load cached token ({e}). Re-authenticating...")
            creds = None

    # Validate or refresh credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"[!] Token refresh failed ({e}). Starting fresh authentication...")
                creds = None

        if not creds:
            creds_json_env = os.getenv("GOOGLE_CREDENTIALS_JSON", "").strip()
            if creds_json_env:
                try:
                    client_config = json.loads(creds_json_env)
                    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                except Exception as e:
                    raise ValueError(f"Invalid GOOGLE_CREDENTIALS_JSON in env: {e}")
            elif GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
                # Construct client config from .env directly
                client_config = {
                    "installed": {
                        "client_id": GOOGLE_CLIENT_ID,
                        "client_secret": GOOGLE_CLIENT_SECRET,
                        "project_id": GOOGLE_PROJECT_ID or "google-meet-attendance",
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "redirect_uris": ["http://localhost"]
                    }
                }
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            elif CREDENTIALS_FILE.exists():
                flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            else:
                raise FileNotFoundError(
                    f"OAuth credentials not found.\n"
                    f"Either set GOOGLE_TOKEN_JSON / GOOGLE_CLIENT_ID in environment,\n"
                    f"or place your client secrets JSON at '{CREDENTIALS_FILE}'."
                )

            creds = flow.run_local_server(port=0)

        # Only save to token.json if environment variables are not being used
        if not (refresh_token_env or token_json_env):
            try:
                with open(TOKEN_FILE, "w", encoding="utf-8") as token:
                    token.write(creds.to_json())
            except Exception:
                pass

    return creds
