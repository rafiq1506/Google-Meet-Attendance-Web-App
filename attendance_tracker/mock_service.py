from datetime import datetime, timedelta
from typing import List, Dict, Any


def get_mock_meeting_participants() -> List[Dict[str, Any]]:
    """
    Returns simulated Google Meet participant logs for demonstration and testing.
    """
    base_time = datetime.now() - timedelta(minutes=65)

    return [
        {
            "participant_id": "conf/123/participants/001",
            "display_name": "Rahul Sharma",
            "email": "rahul.sharma@college.edu",
            "earliest_join": (base_time + timedelta(minutes=1)).strftime("%H:%M:%S"),
            "latest_leave": (base_time + timedelta(minutes=59)).strftime("%H:%M:%S"),
            "duration_minutes": 58.0,
            "duration_seconds": 3480,
            "session_count": 1
        },
        {
            "participant_id": "conf/123/participants/002",
            "display_name": "Priya Patel",
            "email": "priya.patel@college.edu",
            "earliest_join": (base_time + timedelta(minutes=5)).strftime("%H:%M:%S"),
            "latest_leave": (base_time + timedelta(minutes=47)).strftime("%H:%M:%S"),
            "duration_minutes": 42.0,
            "duration_seconds": 2520,
            "session_count": 2
        },
        {
            "participant_id": "conf/123/participants/003",
            "display_name": "Amit Kumar",
            "email": "amit.kumar@college.edu",
            "earliest_join": (base_time + timedelta(minutes=2)).strftime("%H:%M:%S"),
            "latest_leave": (base_time + timedelta(minutes=14)).strftime("%H:%M:%S"),
            "duration_minutes": 12.0,
            "duration_seconds": 720,
            "session_count": 1
        },
        {
            "participant_id": "conf/123/participants/005",
            "display_name": "Rohan Gupta",
            "email": "rohan.gupta@college.edu",
            "earliest_join": (base_time + timedelta(minutes=0)).strftime("%H:%M:%S"),
            "latest_leave": (base_time + timedelta(minutes=60)).strftime("%H:%M:%S"),
            "duration_minutes": 60.0,
            "duration_seconds": 3600,
            "session_count": 1
        }
    ]
