# 🎓 Google Meet Attendance Tracker (Web App & Python)

An automated tool & modern web dashboard to track student attendance from Google Meet sessions, extract participant display names, calculate exact active durations (including reconnects/multiple sessions), and export formatted Excel reports with visual status badges.

---

## 🚀 1. Run the Web Dashboard (Local)

Launch the web application on your local machine:

```bash
# Start the web app
python app.py
```
Open your browser and navigate to: **`http://localhost:5000`**

* **Enter Meet Code / URL**: Paste `https://meet.google.com/abc-defg-hij` or just `abc-defg-hij`.
* **Duration Slider**: Adjust minimum duration required to be marked *Present* (e.g. 30 mins).
* **Live Metrics**: Instantly see Total Attendees, Present, Absent, and Attendance %.
* **Instant Download**: Click **Download Excel** to get the formatted spreadsheet.
* **Test / Demo**: Click **Run Test (Demo)** to preview reporting without a live meeting.

---

## ☁️ 2. Deploy to Render (Cloud Web Service)

This application is ready for deployment on [Render.com](https://render.com):

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Meet Attendance Web App"
   git push origin main
   ```
2. **Create a New Web Service on Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com) > Click **New +** > **Web Service**.
   - Connect your GitHub repository.
3. **Configure Settings (or use `render.yaml`)**:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. **Environment Variables**:
   In Render's **Environment** tab, add:
   - `GOOGLE_TOKEN_JSON`: Paste the entire JSON contents of your local `token.json` file.
   *(This allows Render to authenticate with your Google Meet API without needing local file uploads!)*
   - `DEFAULT_MIN_DURATION_MINUTES`: `30.0` (Optional)

---

## 💻 3. CLI Mode (Command Line Runner)

You can also run from the terminal directly:

```bash
# Process live meeting
python main.py --record-id "abc-defg-hij" --min-duration 30

# Run CLI demo
python main.py --demo
```

This will:
1. Load `sample_students.csv` (Roll numbers 101 to 106).
2. Process mock participant sessions with varying durations and reconnects.
3. Mark students as **Present** (>= 30 mins) or **Absent** (< 30 mins).
4. Output the table to terminal and generate `reports/attendance_report.xlsx`.

---

## 🔑 Google API & Cloud Console Setup

To connect live with Google Meet:

### Step 1: Create a Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click **Select a project** > **New Project** and name it (e.g. `Meet-Attendance-Tracker`).

### Step 2: Enable Google Meet API
1. Navigate to **APIs & Services** > **Library**.
2. Search for **Google Meet API** and click **Enable**.

### Step 3: Configure OAuth Consent Screen
1. Go to **APIs & Services** > **OAuth consent screen**.
2. Choose **External** (or **Internal** if using a Google Workspace organization).
3. Fill in App Name (e.g., `Meet Attendance`) and your email.
4. Add the following Scopes:
   - `https://www.googleapis.com/auth/meetings.space.readonly`
   - `https://www.googleapis.com/auth/meetings.space.created`
5. In **Test Users**, add your Google email address.

### Step 4: Create OAuth 2.0 Credentials
1. Go to **APIs & Services** > **Credentials**.
2. Click **Create Credentials** > **OAuth client ID**.
3. Select Application type: **Desktop app**.
4. Download the JSON credentials file and rename it to **`credentials.json`** in the root directory.

---

---

## 📖 Usage Guide

### 1. Direct Attendance Tracking (No Pre-made Roster Needed)
You do **not** need to prepare any CSV or roster file in advance. The tracker automatically extracts attendee display names and calculates active durations directly from Google Meet:

```bash
# Track attendance directly by meeting code (e.g. abc-defg-hij)
.venv\Scripts\python.exe main.py --record-id "abc-defg-hij"

# Set minimum required active duration (e.g., 40 minutes)
.venv\Scripts\python.exe main.py --record-id "abc-defg-hij" --min-duration 40

# Custom output Excel report name
.venv\Scripts\python.exe main.py --record-id "abc-defg-hij" --output "Lecture_Attendance.xlsx"
```

### 2. Optional: Custom Student Roster (If Desired)
If you ever want to match against an enrolled student list (to mark absent students who didn't join), you can optionally pass `--roster`:

```bash
.venv\Scripts\python.exe main.py --record-id "abc-defg-hij" --roster "students.csv"
```

---

## 📊 Output Features
- **Zero Pre-Setup**: Tracks attendance directly from participant display names on Google Meet.
- **Duration Calculation**: Accurately sums multiple join/leave sessions if someone reconnects.
- **Formatted Excel Report**: Beautiful summary cards (`Total Attendees`, `Present`, `Absent / Short`, `Attendance %`), participant join/leave times, and color-coded status badges (`Present` in green, `Absent` in red).
