from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.agent.answer_verifier import AnswerVerifier


verifier = AnswerVerifier()

citations = [
    {
        "citation_id": "S1",
        "section": "1. Eligibility",
    },
    {
        "citation_id": "S2",
        "section": "2. Remote Work Allowance",
    },
]


print("Testing answer verifier...")
print("=" * 70)


supported_answer = (
    "Employees who completed probation may be eligible "
    "for remote work [S1]."
)

result = verifier.verify(
    supported_answer,
    citations,
)

print("Supported answer")
print(f"Passed          : {result.passed}")
print(f"Cited IDs       : {result.cited_ids}")
print(f"Invalid citations: {result.invalid_citations}")
print(f"Reason          : {result.reason}")

print("=" * 70)


invalid_answer = (
    "Employees receive unlimited remote work [S3]."
)

result = verifier.verify(
    invalid_answer,
    citations,
)

print("Invalid citation answer")
print(f"Passed          : {result.passed}")
print(f"Cited IDs       : {result.cited_ids}")
print(f"Invalid citations: {result.invalid_citations}")
print(f"Reason          : {result.reason}")

print("=" * 70)


missing_citation_answer = (
    "Employees who completed probation may be eligible "
    "for remote work."
)

result = verifier.verify(
    missing_citation_answer,
    citations,
)

print("Missing citation answer")
print(f"Passed          : {result.passed}")
print(f"Cited IDs       : {result.cited_ids}")
print(f"Invalid citations: {result.invalid_citations}")
print(f"Reason          : {result.reason}")

print("=" * 70)
print("Answer verifier test completed!")