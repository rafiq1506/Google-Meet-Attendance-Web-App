import re
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher
from attendance_tracker.config import DEFAULT_MIN_DURATION_MINUTES, DEFAULT_MIN_ATTENDANCE_PERCENT


def clean_name(name: str) -> str:
    """Normalize names for fuzzy matching (removes roll numbers, brackets, punctuation)."""
    name = name.lower().strip()
    name = re.sub(r"\[.*?\]|\(.*?\)", "", name)  # remove parenthesized items like (101)
    name = re.sub(r"[^a-zA-Z\s]", " ", name)
    return " ".join(name.split())


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, clean_name(a), clean_name(b)).ratio()


class AttendanceTracker:
    """
    Matches student records with Google Meet participant logs, computes duration,
    and assigns attendance status (Present / Absent).
    """

    def __init__(
        self,
        students: Optional[List[Dict[str, str]]] = None,
        min_duration_minutes: float = DEFAULT_MIN_DURATION_MINUTES,
        min_attendance_percent: Optional[float] = None,
        total_meeting_duration_minutes: Optional[float] = None
    ):
        self.students = students or []
        self.min_duration_minutes = min_duration_minutes
        self.min_attendance_percent = min_attendance_percent
        self.total_meeting_duration_minutes = total_meeting_duration_minutes

    def process_attendance(self, participants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Compiles attendance report. If student roster is provided, matches participants
        to enrolled students; otherwise, tracks attendees directly from Google Meet.
        """
        effective_min_duration = self.min_duration_minutes
        if self.min_attendance_percent and self.total_meeting_duration_minutes:
            percent_based_duration = (self.min_attendance_percent / 100.0) * self.total_meeting_duration_minutes
            effective_min_duration = max(effective_min_duration, percent_based_duration)

        # Direct Mode: No roster provided. Directly track Google Meet attendees!
        if not self.students:
            results = []
            for p in participants:
                duration_mins = p.get("duration_minutes", 0.0)
                status = "Present" if duration_mins >= effective_min_duration else "Absent"
                results.append({
                    "name": p.get("display_name", "Unknown"),
                    "email": p.get("email", ""),
                    "duration_minutes": duration_mins,
                    "status": status,
                    "join_time": p.get("earliest_join", "-"),
                    "leave_time": p.get("latest_leave", "-"),
                    "session_count": p.get("session_count", 1)
                })
            # Sort by name alphabetically
            results.sort(key=lambda x: x.get("name", "").lower())
            return results

        # Roster Mode: Match against enrolled students list
        unmatched_participants = list(participants)
        results = []

        for student in self.students:
            roll = student.get("roll_no", "")
            s_name = student.get("name", "")
            s_email = student.get("email", "").lower().strip()

            matched_participant = None
            match_index = -1

            # 1. First priority: Exact email match
            if s_email:
                for idx, p in enumerate(unmatched_participants):
                    p_email = p.get("email", "").lower().strip()
                    if p_email and (p_email == s_email or s_email in p_email):
                        matched_participant = p
                        match_index = idx
                        break

            # 2. Second priority: Roll number in display name
            if not matched_participant and roll:
                for idx, p in enumerate(unmatched_participants):
                    p_name = p.get("display_name", "")
                    if roll in p_name:
                        matched_participant = p
                        match_index = idx
                        break

            # 3. Third priority: Fuzzy name matching
            if not matched_participant and s_name:
                best_score = 0.0
                best_idx = -1
                for idx, p in enumerate(unmatched_participants):
                    score = similarity(s_name, p.get("display_name", ""))
                    if score > 0.75 and score > best_score:
                        best_score = score
                        best_idx = idx

                if best_idx != -1:
                    matched_participant = unmatched_participants[best_idx]
                    match_index = best_idx

            if matched_participant:
                duration_mins = matched_participant.get("duration_minutes", 0.0)
                join_time = matched_participant.get("earliest_join", "-")
                leave_time = matched_participant.get("latest_leave", "-")
                session_count = matched_participant.get("session_count", 1)
                # Remove matched participant to avoid double-assignment
                unmatched_participants.pop(match_index)
            else:
                duration_mins = 0.0
                join_time = "-"
                leave_time = "-"
                session_count = 0

            # Determine Present / Absent status
            status = "Present" if duration_mins >= effective_min_duration else "Absent"

            results.append({
                "roll_no": roll,
                "name": s_name,
                "email": s_email,
                "duration_minutes": duration_mins,
                "status": status,
                "join_time": join_time,
                "leave_time": leave_time,
                "session_count": session_count
            })

        return results
