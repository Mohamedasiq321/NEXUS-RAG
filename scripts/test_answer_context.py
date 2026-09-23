from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.agent.answer_context import AnswerContextBuilder
from app.agent.controller import AgentController


controller = AgentController()

builder = AnswerContextBuilder()

query = (
    "Who is eligible for remote work "
    "and what approval is required for exceptions?"
)

state = controller.run(query)

answer_context = builder.build(state)

print("Answer context builder working!")
print("=" * 90)

print(f"Query     : {answer_context.query}")
print(f"Grounded  : {answer_context.grounded}")
print(f"Citations : {len(answer_context.citations)}")

print("=" * 90)
print("CONTEXT")
print("=" * 90)

print(answer_context.context)

print("=" * 90)
print("CITATIONS")
print("=" * 90)

for citation in answer_context.citations:
    print(citation)

print("=" * 90)
print("Answer context test completed!")