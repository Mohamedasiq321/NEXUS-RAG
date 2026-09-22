from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.retrieval.dense_retriever import DenseRetriever


retriever = DenseRetriever()

query = "How many days can employees work remotely?"

results = retriever.search(query, top_k=3)

print("Dense retrieval working!")
print("=" * 70)
print(f"Query: {query}")
print("=" * 70)

for rank, result in enumerate(results, start=1):
    print(f"Rank       : {rank}")
    print(f"Section    : {result['section']}")
    print(f"Similarity: {result['similarity']:.4f}")
    print(f"Content    : {result['content']}")
    print("-" * 70)