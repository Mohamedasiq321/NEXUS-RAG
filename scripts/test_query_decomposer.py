from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.retrieval.query_decomposer import QueryDecomposer


decomposer = QueryDecomposer()

queries = [
    "Who is eligible for remote work and what approval is required for exceptions?",
    "How many days can employees work remotely?",
]

for query in queries:
    subqueries = decomposer.decompose(query)

    print(f"Original Query: {query}")
    print("Subqueries:")

    for index, subquery in enumerate(subqueries, start=1):
        print(f"  {index}. {subquery}")

    print("-" * 70)

print("Query decomposition working!")