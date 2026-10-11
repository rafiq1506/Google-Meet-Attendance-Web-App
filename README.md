# 🎓 Google Meet Attendance Tracker (Web App)

A modern, automated web application and attendance dashboard for Google Meet sessions. Directly tracks participants who joined the meeting, calculates active durations (handling reconnects and multiple sessions), and generates color-coded Excel reports with 1-click downloads.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)
![Render](https://img.shields.io/badge/Deploy-Render.com-46E3B7?logo=render)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Key Features

- **🌐 Modern Web Dashboard**: Sleek dark-mode interface with live summary metric cards (Total Attendees, Present, Absent, Attendance %).
- **🚫 Zero Pre-Setup Required**: No need to prepare CSV rosters or roll number lists beforehand. The tracker pulls attendee display names directly from Google Meet.
- **⏱️ Active Duration Calculation**: Accurately sums multiple join/leave sessions if a student gets disconnected and rejoins.
- **🎚️ Dynamic Threshold Slider**: Instantly adjust the minimum required minutes for a student to be marked **Present** (e.g. 15m, 30m, 45m).
- **📊 1-Click Excel Export**: Formatted spreadsheets with summary statistics, timestamps, and color badges (**Present** in green, **Absent** in red).
- **🔒 100% Secure & GitHub Safe**: All secrets and OAuth tokens reside strictly in `.env`. No credentials or token JSON files are pushed to GitHub.
- **☁️ Cloud & Render Ready**: Includes `render.yaml` and `Procfile` for 1-click deployment on Render.com.

---

## 📁 Project Architecture

```
Attendance tracker/
├── attendance_tracker/
│   ├── __init__.py
│   ├── config.py           # Configuration & environment loader
│   ├── auth.py             # Cloud-native OAuth 2.0 authentication
│   ├── meet_service.py     # Google Meet REST API v2 client
│   ├── tracker.py          # Attendance & duration processor
│   ├── reporter.py         # Formatted Excel exporter with badges
│   └── mock_service.py     # Mock participant logs for immediate testing
├── templates/
│   └── index.html          # Modern dashboard frontend
├── static/
│   ├── css/style.css       # Dark glassmorphism design system
│   └── js/app.js           # Client-side interactive logic
├── .env.example            # Environment variables template
├── requirements.txt        # Production dependencies
├── Procfile                # WSGI command for Render
├── render.yaml             # Render deployment blueprint
├── app.py                  # Web application entry point (Flask)
└── README.md
```

---

## 🚀 Quick Start (Local Machine)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Create a `.env` file (copied from `.env.example`) and add your Google OAuth credentials:
```env
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_PROJECT_ID=your_project_id
GOOGLE_REFRESH_TOKEN=your_refresh_token

DEFAULT_MIN_DURATION_MINUTES=30.0
```

### 3. Run the Web Application
```bash
python app.py
```
Open your browser and navigate to: **`http://localhost:5000`**

- **Live Meeting**: Paste your Google Meet link (`https://meet.google.com/abc-defg-hij`) or meeting code (`abc-defg-hij`) and click **Fetch & Generate Attendance**.
- **Instant Demo**: Click **Run Test (Demo)** to preview attendance tracking without needing a live call.
- **Download Excel**: Click **Download Excel** to get the formatted `.xlsx` report.

---

## ☁️ Deploy to Render.com (Cloud Web Service)

Deploy your attendance tracker to Render for free so you and your team can access it from any browser:

### Step 1: Push Code to GitHub
```bash
git init
git add .
git commit -m "Initial commit: Meet Attendance Web App"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
git push -u origin main
```
> **Security Notice**: Both `.env`, `credentials.json`, and `token.json` are listed in `.gitignore`. Your secrets will **never** be uploaded to GitHub.

---

### Step 2: Create Web Service on Render
1. Go to [dashboard.render.com](https://dashboard.render.com) and log in.
2. Click **New +** > **Web Service**.
3. Connect your GitHub repository.

---

### Step 3: Render Configuration
Render will automatically detect the settings from `render.yaml` / `Procfile`:
- **Language / Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`

---

### Step 4: Add Environment Variables in Render
In the Render Service dashboard, go to the **Environment** tab and add the following keys from your `.env`:

| Key | Value | Description |
|---|---|---|
| `GOOGLE_CLIENT_ID` | `487140...apps.googleusercontent.com` | Google OAuth Client ID |
| `GOOGLE_CLIENT_SECRET` | `GOCSPX-...` | Google OAuth Client Secret |
| `GOOGLE_REFRESH_TOKEN` | `1//0gvug...` | Refresh token (auto-refreshes access tokens) |
| `DEFAULT_MIN_DURATION_MINUTES` | `30.0` | Default minimum attendance duration |

Click **Save Changes**. Render will automatically build and deploy your app, giving you a live URL like `https://meet-attendance-tracker.onrender.com`!

---

## 🔑 Google Cloud API Setup (First Time Setup)

To connect with live Google Meet calls:

1. **Google Cloud Console**: Go to [console.cloud.google.com](https://console.cloud.google.com) and create a project.
2. **Enable Google Meet API**: Go to **APIs & Services** > **Library** > search for **Google Meet API** and click **Enable**.
3. **OAuth Consent Screen**:
   - User Type: **External**
   - Scopes:
     - `https://www.googleapis.com/auth/meetings.space.readonly`
     - `https://www.googleapis.com/auth/meetings.space.created`
   - Test Users: Add your host Google account email.
4. **Create OAuth 2.0 Credentials**:
   - Go to **Credentials** > **Create Credentials** > **OAuth client ID**.
   - Application Type: **Desktop app**.
   - Copy the Client ID and Client Secret into your `.env` file.

---

## 📄 License
This project is licensed under the MIT License.
