from datetime import datetime
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from dateutil import parser
from attendance_tracker.auth import get_credentials


class GoogleMeetService:
    """
    Client for interacting with the Google Meet REST API v2.
    Retrieves conference records, participants, and their join/leave sessions.
    """

    def __init__(self, creds=None):
        self.creds = creds or get_credentials()
        self.service = build("meet", "v2", credentials=self.creds)

    def list_conference_records(self, page_size: int = 10) -> List[Dict[str, Any]]:
        """
        Lists past Google Meet conference records.
        Returns a list of conference record objects with meeting ID, start time, end time.
        """
        records = []
        request = self.service.conferenceRecords().list(pageSize=page_size)
        while request is not None:
            response = request.execute()
            records.extend(response.get("conferenceRecords", []))
            request = self.service.conferenceRecords().list_next(request, response)
        return records

    def get_conference_record(self, conference_record_name: str) -> Dict[str, Any]:
        """
        Retrieves details for a specific conference record.
        e.g. conference_record_name: 'conferenceRecords/abc-defg-hij'
        """
        return self.service.conferenceRecords().get(name=conference_record_name).execute()

    def find_record_by_meeting_code(self, meeting_code: str) -> Optional[Dict[str, Any]]:
        """
        Finds the latest or active conference record for a given meeting code (e.g. 'byi-jwrf-sso').
        """
        clean_code = meeting_code.replace("https://meet.google.com/", "").strip("/").strip()
        records = self.list_conference_records(page_size=20)
        
        for rec in records:
            space_name = rec.get("space")  # e.g., 'spaces/AjL_U7moYLgB'
            if space_name:
                try:
                    space_info = self.service.spaces().get(name=space_name).execute()
                    space_code = space_info.get("meetingCode", "")
                    space_uri = space_info.get("meetingUri", "")
                    if clean_code in (space_code, space_uri) or space_code == clean_code:
                        return rec
                except Exception:
                    continue
        return None

    def resolve_record_id(self, input_identifier: str) -> str:
        """
        Resolves an input string (which could be a meeting code or full conferenceRecord ID)
        to a valid 'conferenceRecords/...' identifier.
        """
        identifier = input_identifier.strip()
        if identifier.startswith("conferenceRecords/"):
            return identifier

        # Treat as meeting code
        print(f"[*] Looking up conference record for meeting code '{identifier}'...")
        rec = self.find_record_by_meeting_code(identifier)
        if rec:
            rec_id = rec.get("name")
            print(f"[+] Found conference record: {rec_id}")
            return rec_id
        
        # Fallback: if not found via spaces lookup, check list_conference_records
        records = self.list_conference_records(page_size=5)
        if records:
            latest = records[0].get("name")
            print(f"[!] Warning: Could not explicitly map '{identifier}' to space. Using most recent record: {latest}")
            return latest

        raise ValueError(f"No active or past conference record found for meeting code: '{identifier}'")

    def get_participants_with_sessions(self, conference_record_name: str) -> List[Dict[str, Any]]:
        """
        Retrieves all participants for a conference record, along with their
        detailed session timestamps (join time, leave time, duration).
        """
        participants = []
        req = self.service.conferenceRecords().participants().list(parent=conference_record_name)
        
        while req is not None:
            resp = req.execute()
            raw_participants = resp.get("participants", [])

            for p in raw_participants:
                p_name = p.get("name")  # e.g., 'conferenceRecords/.../participants/...'
                display_name = p.get("signedinUser", {}).get("displayName") or p.get("anonymousUser", {}).get("displayName") or "Unknown"
                user_email = p.get("signedinUser", {}).get("user", "")  # User resource or email if resolved
                
                # Fetch participant sessions (handles disconnects and multiple join/leaves)
                sessions = self._get_participant_sessions(p_name)
                
                total_duration_seconds = 0
                earliest_join: Optional[datetime] = None
                latest_leave: Optional[datetime] = None

                for s in sessions:
                    start_time_str = s.get("startTime")
                    end_time_str = s.get("endTime")

                    if start_time_str:
                        start_dt = parser.isoparse(start_time_str)
                        if earliest_join is None or start_dt < earliest_join:
                            earliest_join = start_dt

                    if end_time_str:
                        end_dt = parser.isoparse(end_time_str)
                        if latest_leave is None or end_dt > latest_leave:
                            latest_leave = end_dt
                    elif start_time_str:
                        # If session ended without explicit endTime, fallback to start_dt
                        end_dt = start_dt
                    else:
                        continue

                    if start_time_str and end_time_str:
                        duration_sec = max(0, (end_dt - start_dt).total_seconds())
                        total_duration_seconds += duration_sec

                participants.append({
                    "participant_id": p_name,
                    "display_name": display_name,
                    "email": user_email,
                    "earliest_join": earliest_join.isoformat() if earliest_join else None,
                    "latest_leave": latest_leave.isoformat() if latest_leave else None,
                    "duration_minutes": round(total_duration_seconds / 60.0, 2),
                    "duration_seconds": int(total_duration_seconds),
                    "session_count": len(sessions),
                    "sessions": sessions
                })

            req = self.service.conferenceRecords().participants().list_next(req, resp)

        return participants

    def _get_participant_sessions(self, participant_name: str) -> List[Dict[str, Any]]:
        """
        Helper method to list all sessions for a specific participant.
        """
        sessions = []
        req = self.service.conferenceRecords().participants().participantSessions().list(parent=participant_name)
        while req is not None:
            resp = req.execute()
            sessions.extend(resp.get("participantSessions", []))
            req = self.service.conferenceRecords().participants().participantSessions().list_next(req, resp)
        return sessions
