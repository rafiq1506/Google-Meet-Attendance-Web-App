import os
import sys
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file

from attendance_tracker.config import (
    DEFAULT_MIN_DURATION_MINUTES,
    REPORTS_DIR,
    EXCEL_REPORT_PREFIX,
    APPEND_TIMESTAMP_TO_EXCEL,
    TOKEN_FILE,
    CREDENTIALS_FILE
)
from attendance_tracker.tracker import AttendanceTracker
from attendance_tracker.reporter import AttendanceReporter
from attendance_tracker.mock_service import get_mock_meeting_participants

from dotenv import load_dotenv
load_dotenv()
from keep_alive import keep_alive
keep_alive()


app = Flask(__name__)
app.config["REPORTS_DIR"] = REPORTS_DIR


def check_auth_status():
    """Checks if Google credentials or cached tokens exist."""
    has_token_env = bool(os.getenv("GOOGLE_TOKEN_JSON", "").strip() or os.getenv("GOOGLE_REFRESH_TOKEN", "").strip())
    has_token_file = TOKEN_FILE.exists()
    has_creds_env = bool(os.getenv("GOOGLE_CLIENT_ID", "").strip() or os.getenv("GOOGLE_CREDENTIALS_JSON", "").strip())
    has_creds_file = CREDENTIALS_FILE.exists()
    is_ready = has_token_env or has_token_file or has_creds_env or has_creds_file
    return {
        "ready": is_ready,
        "has_token": has_token_env or has_token_file,
        "has_creds": has_creds_env or has_creds_file
    }


@app.route("/")
def index():
    auth_info = check_auth_status()
    return render_template(
        "index.html",
        auth_info=auth_info,
        default_min_duration=DEFAULT_MIN_DURATION_MINUTES
    )


@app.route("/api/status", methods=["GET"])
def api_status():
    auth_info = check_auth_status()
    return jsonify({
        "status": "ok",
        "auth": auth_info,
        "default_min_duration": DEFAULT_MIN_DURATION_MINUTES
    })


@app.route("/api/recent-meetings", methods=["GET"])
def api_recent_meetings():
    auth_info = check_auth_status()
    if not auth_info["ready"]:
        return jsonify({
            "success": False,
            "message": "Google Cloud OAuth credentials not found yet. You can use Demo mode."
        }), 400

    try:
        from attendance_tracker.meet_service import GoogleMeetService
        service = GoogleMeetService()
        records = service.list_conference_records(page_size=10)
        formatted = []
        for rec in records:
            formatted.append({
                "record_id": rec.get("name", ""),
                "start_time": rec.get("startTime", ""),
                "end_time": rec.get("endTime", ""),
                "space": rec.get("space", "")
            })
        return jsonify({
            "success": True,
            "meetings": formatted
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route("/api/attendance", methods=["POST"])
def api_attendance():
    data = request.get_json() or {}
    meeting_input = (data.get("meeting_code") or "").strip()
    min_duration = float(data.get("min_duration") or DEFAULT_MIN_DURATION_MINUTES)
    is_demo = bool(data.get("is_demo") or meeting_input.lower() == "demo")

    # Clean Google Meet URL if pasted (e.g. https://meet.google.com/abc-defg-hij)
    clean_code = meeting_input
    if "meet.google.com/" in clean_code:
        clean_code = clean_code.split("meet.google.com/")[-1].split("?")[0].strip("/")

    participants = []
    meeting_title = f"Meet: {clean_code or 'Demo'}"

    if is_demo or not clean_code:
        participants = get_mock_meeting_participants()
        meeting_title = "Demo Class - Google Meet"
    else:
        try:
            from attendance_tracker.meet_service import GoogleMeetService
            service = GoogleMeetService()
            resolved_id = service.resolve_record_id(clean_code)
            participants = service.get_participants_with_sessions(resolved_id)
            meeting_title = f"Google Meet ({clean_code})"
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Could not retrieve participants: {str(e)}"
            }), 400

    if not participants:
        return jsonify({
            "success": False,
            "message": "No participant sessions found for this meeting."
        }), 404

    # Process Attendance (Direct mode without mandatory roster)
    tracker = AttendanceTracker(min_duration_minutes=min_duration)
    attendance_records = tracker.process_attendance(participants)

    # Compute Summary
    total_attendees = len(attendance_records)
    present_count = sum(1 for r in attendance_records if r.get("status") == "Present")
    absent_count = total_attendees - present_count
    attendance_rate = round((present_count / total_attendees * 100), 1) if total_attendees > 0 else 0

    # Generate Excel Report
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_filename = f"{EXCEL_REPORT_PREFIX}_{clean_code or 'demo'}_{timestamp_str}.xlsx"
    out_path = REPORTS_DIR / clean_filename
    AttendanceReporter.export_excel(attendance_records, out_path, meeting_title=meeting_title)

    return jsonify({
        "success": True,
        "meeting_title": meeting_title,
        "summary": {
            "total": total_attendees,
            "present": present_count,
            "absent": absent_count,
            "attendance_rate": attendance_rate,
            "min_duration": min_duration
        },
        "records": attendance_records,
        "download_url": f"/api/download/{clean_filename}"
    })


@app.route("/api/download/<filename>", methods=["GET"])
def api_download(filename):
    file_path = REPORTS_DIR / filename
    if not file_path.exists():
        return jsonify({"error": "File not found"}), 404
    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
