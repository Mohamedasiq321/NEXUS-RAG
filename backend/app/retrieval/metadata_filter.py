import re


class MetadataFilterExtractor:
    """
    Extract deterministic metadata filters from natural-language queries.

    Supported CSV fields:
    - department
    - role
    - status
    - remote_days_per_week
    - id
    """

    STATUS_VALUES = {
        "approved": "Approved",
        "pending": "Pending",
        "rejected": "Rejected",
        "not eligible": "Not Eligible",
    }

    DEPARTMENTS = {
        "engineering",
        "finance",
        "human resources",
        "operations",
        "sales",
    }

    ROLES = {
        "software engineer",
        "financial analyst",
        "hr executive",
        "operations manager",
        "ml engineer",
        "sales executive",
    }

    def extract(self, query: str) -> dict[str, str]:
        normalized = " ".join(query.strip().lower().split())

        if not normalized:
            return {}

        filters: dict[str, str] = {}

        # Remote days per week
        remote_days_match = re.search(
            r"\b(\d+)\s+remote\s+days?(?:\s+per\s+week)?\b",
            normalized,
        )

        if remote_days_match:
            filters["remote_days_per_week"] = remote_days_match.group(1)

        # Status
        for phrase, value in self.STATUS_VALUES.items():
            if phrase in normalized:
                filters["status"] = value
                break

        # Employee ID
        employee_id_match = re.search(
            r"\bemp\d+\b",
            normalized,
            re.IGNORECASE,
        )

        if employee_id_match:
            filters["id"] = employee_id_match.group(0).upper()

        # Department
        for department in sorted(
            self.DEPARTMENTS,
            key=len,
            reverse=True,
        ):
            if department in normalized:
                filters["department"] = department.title()

                if department == "human resources":
                    filters["department"] = "Human Resources"

                break

        # Role
        for role in sorted(
            self.ROLES,
            key=len,
            reverse=True,
        ):
            if role in normalized:
                filters["role"] = role.title()

                if role == "ml engineer":
                    filters["role"] = "ML Engineer"
                elif role == "hr executive":
                    filters["role"] = "HR Executive"

                break

        return filters