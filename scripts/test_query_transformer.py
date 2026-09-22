from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.retrieval.query_transformer import QueryTransformer


transformer = QueryTransformer()

queries = [
    "  How many days can employees work remotely?  ",
    "Can I work from home?",
    "Is WFH allowed?",
]

for query in queries:
    transformed = transformer.transform(query)

    print(f"Original   : {query!r}")
    print(f"Transformed: {transformed!r}")
    print("-" * 70)

print("Query transformation component working!")