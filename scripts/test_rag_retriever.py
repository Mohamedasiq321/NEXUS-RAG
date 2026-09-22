from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.retrieval.rag_retriever import RAGRetriever


retriever = RAGRetriever()

query = "Can I work from home?"

results = retriever.search(
    query,
    candidate_k=5,
    top_k=3,
)

print("End-to-end retrieval pipeline working!")
print("=" * 90)
print(f"Original Query  : {query}")
print("=" * 90)

for rank, result in enumerate(results, start=1):
    print(f"Final Rank      : {rank}")
    print(f"Section         : {result['section']}")
    print(f"Original Query  : {result['original_query']}")
    print(f"Retrieval Query : {result['retrieval_query']}")
    print(f"RRF Score       : {result['rrf_score']:.6f}")
    print(f"Rerank Score    : {result['rerank_score']:.6f}")
    print(f"Content         : {result['content']}")
    print("-" * 90)