from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.agent.citation_manager import CitationManager


manager = CitationManager()


citations = [
    {
        "citation_id": "S1",
        "section": "1. Eligibility",
        "content": (
            "Employees who have completed their probation period "
            "may be eligible for remote work, subject to their role, "
            "manager approval, and business requirements."
        ),
    },
    {
        "citation_id": "S2",
        "section": "2. Remote Work Allowance",
        "content": (
            "Eligible employees may work remotely for up to "
            "three working days per week."
        ),
    },
    {
        "citation_id": "S3",
        "section": "3. Equipment",
        "content": (
            "Employees approved for remote work may request "
            "company-provided equipment."
        ),
    },
    {
        "citation_id": "S4",
        "section": "5. Exceptions",
        "content": (
            "Exceptions to the standard remote work allowance "
            "require approval from the department head."
        ),
    },
]


answer = (
    "Eligible employees for remote work include those who have "
    "completed their probation period, provided their role allows "
    "for remote work, and their managers approve the request. "
    "Exceptions to the standard remote work allowance require "
    "approval by the department head."
)


result = manager.attach(
    answer,
    citations,
)


print("Citation manager test")
print("=" * 80)
print("ANSWER")
print("=" * 80)
print(result.answer)

print("=" * 80)
print("CITATIONS")
print("=" * 80)

for citation in result.citations:
    print(
        f"{citation['citation_id']} -> "
        f"{citation['section']}"
    )

print("=" * 80)
print("Citation manager test completed!")