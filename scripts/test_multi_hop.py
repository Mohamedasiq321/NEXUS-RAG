from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.retrieval.multi_hop_retriever import MultiHopRetriever


retriever = MultiHopRetriever()

query = (
    "Who is eligible for remote work "
    "and what approval is required for exceptions?"
)

hops = retriever.search(
    query,
    top_k=2,
)

print("Automatic multi-hop retrieval working!")
print("=" * 90)
print(f"Original Query: {query}")
print("=" * 90)

for hop in hops:
    print(f"Hop {hop.hop_number}")
    print(f"Query: {hop.query}")
    print("-" * 90)

    for rank, result in enumerate(
        hop.results,
        start=1,
    ):
        print(f"Rank    : {rank}")
        print(f"Section : {result['section']}")
        print(f"Score   : {result['rerank_score']:.6f}")
        print(f"Content : {result['content']}")
        print("-" * 90)

print("Automatic multi-hop retrieval test completed!")