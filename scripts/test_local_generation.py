from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.agent.answer_context import AnswerContextBuilder
from app.agent.controller import AgentController
from app.generation.ollama_generator import OllamaAnswerGenerator


controller = AgentController(
    max_iterations=2,
    minimum_evidence=2,
)

builder = AnswerContextBuilder()
generator = OllamaAnswerGenerator(
    model="qwen2.5:1.5b",
)


query = (
    "Who is eligible for remote work "
    "and what approval is required for exceptions?"
)

print("Running NEXUS-RAG local generation pipeline...")
print("=" * 90)

state = controller.run(query)

print(f"Retrieval Iteration : {state.iteration}")
print(f"Evidence Count      : {len(state.evidence)}")
print(f"Evidence Sufficient : {state.evidence_sufficient}")

context = builder.build(state)

print(f"Context Grounded    : {context.grounded}")
print(f"Citations           : {len(context.citations)}")

print("=" * 90)
print("Generating answer with local Ollama model...")
print("=" * 90)

result = generator.generate(context)

print("ANSWER")
print("=" * 90)
print(result.answer)

print("=" * 90)
print(f"Grounded : {result.grounded}")
print(f"Citations: {len(result.citations)}")
print("=" * 90)

print("Local generation test completed!")