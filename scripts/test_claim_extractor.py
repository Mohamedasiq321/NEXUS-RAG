from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.agent.claim_extractor import ClaimExtractor


extractor = ClaimExtractor()


answer = (
    "Employees who have completed their probation period "
    "may be eligible for remote work [S1]. "
    "Exceptions to the standard remote work allowance "
    "require approval from the department head [S4]."
)


claims = extractor.extract(answer)


print("Claim extractor test")
print("=" * 80)

for claim in claims:
    print(
        f"{claim.claim_id}: {claim.text}"
    )

print("=" * 80)
print(f"Claims extracted: {len(claims)}")
print("Claim extractor test completed!")