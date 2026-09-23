from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.agent.query_refiner import QueryRefiner


refiner = QueryRefiner()

queries = [
    "What is the company's annual bonus policy?",
    "What is the employee leave policy?",
    "What are the general company rules?",
]

for query in queries:

    result = refiner.refine(query)

    print("=" * 90)
    print(f"Original Query : {result.original_query}")
    print(f"Refined Query  : {result.refined_query}")
    print(f"Reason         : {result.reason}")

print("=" * 90)
print("Query refinement test completed!")