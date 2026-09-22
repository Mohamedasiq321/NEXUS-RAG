from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.agent.state import AgentState


state = AgentState(
    original_query=(
        "Who is eligible for remote work "
        "and what approval is required for exceptions?"
    )
)

state.route = "complex"
state.route_reason = "Query contains multiple aspects."
state.retrieval_query = state.original_query
state.subqueries = [
    "Who is eligible for remote work",
    "what approval is required for exceptions",
]

state.iteration = 1

print("Agent state working!")
print("=" * 80)
print(f"Original Query : {state.original_query}")
print(f"Route          : {state.route}")
print(f"Subqueries     : {state.subqueries}")
print(f"Iteration      : {state.iteration}")
print("=" * 80)
print("Agent state test completed!")