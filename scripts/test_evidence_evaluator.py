from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.agent.evidence_evaluator import EvidenceEvaluator


evaluator = EvidenceEvaluator()

strong_evidence = [
    {
        "section": "1. Eligibility",
        "score": 0.998978,
        "content": "Employees who completed probation may be eligible.",
    },
    {
        "section": "5. Exceptions",
        "score": 0.918808,
        "content": "Exceptions require department head approval.",
    },
]

weak_evidence = [
    {
        "section": "Document Information",
        "score": 0.31,
        "content": "General company policy information.",
    },
]


print("Testing strong evidence...")
strong_result = evaluator.evaluate(strong_evidence)

print(f"Sufficient : {strong_result.sufficient}")
print(f"Confidence : {strong_result.confidence:.6f}")
print(f"Reason     : {strong_result.reason}")

print("\n" + "=" * 80)

print("Testing weak evidence...")
weak_result = evaluator.evaluate(weak_evidence)

print(f"Sufficient : {weak_result.sufficient}")
print(f"Confidence : {weak_result.confidence:.6f}")
print(f"Reason     : {weak_result.reason}")

print("\n" + "=" * 80)
print("Evidence evaluator test completed!")