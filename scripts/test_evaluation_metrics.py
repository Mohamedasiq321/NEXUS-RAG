from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.evaluation.metrics import (
    recall_at_k,
    reciprocal_rank,
    ndcg_at_k,
)


print("NEXUS-RAG EVALUATION METRICS TEST")
print("=" * 90)


retrieved = [
    "2. Remote Work Allowance",
    "1. Eligibility",
    "3. Equipment",
    "5. Exceptions",
]

relevant = [
    "1. Eligibility",
]


# ---------------------------------------------------------
# Recall@K
# ---------------------------------------------------------

recall = recall_at_k(
    retrieved,
    relevant,
    k=3,
)

print("RECALL@3")
print("=" * 90)
print(f"Recall@3: {recall}")


# ---------------------------------------------------------
# MRR
# ---------------------------------------------------------

mrr = reciprocal_rank(
    retrieved,
    relevant,
)

print()
print("MRR")
print("=" * 90)
print(f"MRR: {mrr}")


# ---------------------------------------------------------
# NDCG@K
# ---------------------------------------------------------

ndcg = ndcg_at_k(
    retrieved,
    relevant,
    k=3,
)

print()
print("NDCG@3")
print("=" * 90)
print(f"NDCG@3: {ndcg}")


# ---------------------------------------------------------
# Assertions
# ---------------------------------------------------------

assert recall == 1.0
assert mrr == 0.5
assert ndcg > 0.0


print()
print("=" * 90)
print("All evaluation metric tests passed!")