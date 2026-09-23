from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.agent.answer_context import AnswerContextBuilder
from app.agent.controller import AgentController
from app.generation.ollama_generator import OllamaAnswerGenerator
from app.agent.answer_verifier import AnswerVerifier
from app.agent.citation_manager import CitationManager

controller = AgentController(
    max_iterations=2,
    minimum_evidence=2,
)

builder = AnswerContextBuilder()
generator = OllamaAnswerGenerator(
    model="qwen2.5:1.5b",
)

verifier = AnswerVerifier()

citation_manager = CitationManager()

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
citation_attachment = citation_manager.attach(
    result.answer,
    result.citations,
)

verification = verifier.verify(
    citation_attachment.answer,
    citation_attachment.citations,
)

print("ANSWER")
print("=" * 90)
print(citation_attachment.answer)

print("=" * 90)
print("VERIFICATION")
print("=" * 90)
print(f"Passed           : {verification.passed}")
print(f"Cited IDs        : {verification.cited_ids}")
print(f"Invalid citations: {verification.invalid_citations}")
print(f"Reason           : {verification.reason}")

print("=" * 90)
print(f"Grounded : {result.grounded}")
print(
    f"Citations: {len(citation_attachment.citations)}"
)
print("=" * 90)

print("Local generation test completed!")