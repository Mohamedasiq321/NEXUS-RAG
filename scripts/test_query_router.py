from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.retrieval.query_router import QueryRouter


router = QueryRouter()

queries = [
    "How many days can employees work remotely?",
    "Who is eligible for remote work and what restrictions apply?",
]

for query in queries:
    result = router.route(query)

    print(f"Query  : {query}")
    print(f"Route  : {result.route}")
    print(f"Reason : {result.reason}")
    print("-" * 70)

print("Query routing component working!")