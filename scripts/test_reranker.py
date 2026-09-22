from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.reranker import Reranker


query = "How many days can employees work remotely?"

hybrid_retriever = HybridRetriever()
reranker = Reranker()

candidates = hybrid_retriever.search(
    query,
    top_k=5,
)

results = reranker.rerank(
    query,
    candidates,
    top_k=5,
)

print("Hybrid retrieval + RRF + reranking working!")
print("=" * 90)
print(f"Query: {query}")
print("=" * 90)

for rank, result in enumerate(results, start=1):
    print(f"Final Rank  : {rank}")
    print(f"Section     : {result['section']}")
    print(f"Dense Rank  : {result['dense_rank']}")
    print(f"BM25 Rank   : {result['bm25_rank']}")
    print(f"RRF Score   : {result['rrf_score']:.6f}")
    print(f"Rerank Score: {result['rerank_score']:.6f}")
    print(f"Content     : {result['content']}")
    print("-" * 90)