from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.agent.claim_extractor import ClaimExtractor
from app.agent.claim_verifier import ClaimVerifier


extractor = ClaimExtractor()
verifier = ClaimVerifier()


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
        "citation_id": "S4",
        "section": "5. Exceptions",
        "content": (
            "Certain roles may require regular physical presence "
            "at company facilities. Exceptions to the standard "
            "remote work allowance require approval from the "
            "department head."
        ),
    },
]


print("NEXUS-RAG CLAIM VERIFIER TEST")
print("=" * 90)


# ---------------------------------------------------------
# Supported claims
# ---------------------------------------------------------

supported_answer = (
    "Employees who have completed their probation period "
    "may be eligible for remote work [S1]. "
    "Exceptions to the standard remote work allowance "
    "require approval from the department head [S4]."
)

claims = extractor.extract(supported_answer)

print("SUPPORTED CLAIMS")
print("=" * 90)

verification_1 = verifier.verify(
    claims[0],
    "S1",
    citations,
)

verification_2 = verifier.verify(
    claims[1],
    "S4",
    citations,
)

for result in [
    verification_1,
    verification_2,
]:
    print(
        f"{result.claim_id}: "
        f"supported={result.supported}, "
        f"citation={result.citation_id}, "
        f"score={result.overlap_score}"
    )
    print(f"Reason: {result.reason}")
    print()


# ---------------------------------------------------------
# Hallucinated claim
# ---------------------------------------------------------

print("=" * 90)
print("HALLUCINATED CLAIM")
print("=" * 90)

hallucinated_answer = (
    "Employees can work remotely five days per week [S1]."
)

hallucinated_claim = extractor.extract(
    hallucinated_answer
)[0]

hallucination_result = verifier.verify(
    hallucinated_claim,
    "S1",
    citations,
)

print(
    f"{hallucination_result.claim_id}: "
    f"supported={hallucination_result.supported}, "
    f"citation={hallucination_result.citation_id}, "
    f"score={hallucination_result.overlap_score}"
)

print(
    f"Reason: {hallucination_result.reason}"
)


# ---------------------------------------------------------
# Final assertions
# ---------------------------------------------------------

print("=" * 90)
print("TEST RESULT")
print("=" * 90)

supported_tests_passed = (
    verification_1.supported
    and verification_2.supported
)

hallucination_rejected = (
    not hallucination_result.supported
)

print(
    f"Supported claims accepted : "
    f"{supported_tests_passed}"
)

print(
    f"Hallucinated claim rejected: "
    f"{hallucination_rejected}"
)

assert supported_tests_passed, (
    "Supported claims should have passed verification."
)

assert hallucination_rejected, (
    "Hallucinated claim should have been rejected."
)

print()
print("All claim verification tests passed!")