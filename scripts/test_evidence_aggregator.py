from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.retrieval.multi_hop_retriever import MultiHopRetriever
from app.retrieval.evidence_aggregator import EvidenceAggregator


retriever = MultiHopRetriever()
aggregator = EvidenceAggregator()

query = (
    "Who is eligible for remote work "
    "and what approval is required for exceptions?"
)

hops = retriever.search(
    query,
    top_k=2,
)

evidence = aggregator.aggregate(
    hops,
    top_k=5,
)

print("Evidence aggregation working!")
print("=" * 90)
print(f"Original Query: {query}")
print("=" * 90)

for rank, item in enumerate(evidence, start=1):

    print(f"Evidence Rank : {rank}")
    print(f"Section       : {item.section}")
    print(f"Score         : {item.score:.6f}")
    print(f"Source Hops   : {item.source_hops}")
    print(f"Content       : {item.content}")
    print("-" * 90)

print("Evidence aggregation test completed!")
