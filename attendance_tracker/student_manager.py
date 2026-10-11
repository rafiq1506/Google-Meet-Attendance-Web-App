from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd


class StudentManager:
    """
    Manages loading, validating, and searching the class roster.
    Supports CSV and Excel (.xlsx, .xls) files.
    """

    def __init__(self, roster_path: Optional[Path] = None):
        self.students: List[Dict[str, str]] = []
        if roster_path:
            self.load_roster(roster_path)

    def load_roster(self, file_path: Path) -> List[Dict[str, str]]:
        """
        Loads the student roster from a CSV or Excel file.
        Normalized column headers expected: 'roll_no', 'name', 'email'.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Roster file not found: {path}")

        if path.suffix.lower() in [".xlsx", ".xls"]:
            df = pd.read_excel(path)
        elif path.suffix.lower() == ".csv":
            df = pd.read_csv(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}. Use CSV or XLSX.")

        # Normalize column names
        normalized_cols = {col: str(col).strip().lower().replace(" ", "_").replace(".", "") for col in df.columns}
        df = df.rename(columns=normalized_cols)

        # Find mappings for Roll No, Name, and Email
        roll_col = next((c for c in df.columns if "roll" in c or "id" in c), "roll_no")
        name_col = next((c for c in df.columns if "name" in c or "student" in c), "name")
        email_col = next((c for c in df.columns if "email" in c or "mail" in c), "email")

        self.students = []
        for _, row in df.iterrows():
            roll_val = str(row.get(roll_col, "")).strip()
            name_val = str(row.get(name_col, "")).strip()
            email_val = str(row.get(email_col, "")).strip().lower()

            # Skip empty rows
            if not roll_val and not name_val:
                continue

            self.students.append({
                "roll_no": roll_val if roll_val != "nan" else "",
                "name": name_val if name_val != "nan" else "",
                "email": email_val if email_val != "nan" else ""
            })

        return self.students

    def get_all_students(self) -> List[Dict[str, str]]:
        return self.students
