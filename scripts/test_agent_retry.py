from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.agent.controller import AgentController


controller = AgentController(
    max_iterations=2,
    minimum_evidence=2,
)

query = "What is the company's annual bonus policy?"

state = controller.run(query)

print("Testing controlled retry behavior!")
print("=" * 90)

print(f"Original Query     : {state.original_query}")
print(f"Final Iteration    : {state.iteration}")
print(f"Retrieval Query    : {state.retrieval_query}")
print(f"Subqueries         : {state.subqueries}")
print(f"Evidence Count     : {len(state.evidence)}")
print(f"Evidence Sufficient: {state.evidence_sufficient}")

print("=" * 90)

for rank, evidence in enumerate(
    state.evidence,
    start=1,
):
    print(f"Evidence Rank : {rank}")
    print(f"Section       : {evidence['section']}")
    print(f"Score         : {evidence['score']:.6f}")
    print(f"Content       : {evidence['content']}")
    print("-" * 90)

print("=" * 90)
print("Retry behavior test completed!")