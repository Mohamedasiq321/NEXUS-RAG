from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))


from app.agent.answer_context import AnswerContextBuilder
from app.agent.controller import AgentController
from app.agent.answer_verifier import AnswerVerifier
from app.agent.citation_manager import CitationManager
from app.agent.claim_extractor import ClaimExtractor
from app.agent.claim_verifier import ClaimVerifier
from app.generation.ollama_generator import OllamaAnswerGenerator


# ---------------------------------------------------------
# Initialize components
# ---------------------------------------------------------

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

claim_extractor = ClaimExtractor()
claim_verifier = ClaimVerifier()


# ---------------------------------------------------------
# Query
# ---------------------------------------------------------

query = (
    "Who is eligible for remote work "
    "and what approval is required for exceptions?"
)


# ---------------------------------------------------------
# Agentic retrieval
# ---------------------------------------------------------

print("Running NEXUS-RAG local generation pipeline...")
print("=" * 90)

state = controller.run(query)

print(f"Retrieval Iteration : {state.iteration}")
print(f"Evidence Count      : {len(state.evidence)}")
print(f"Evidence Sufficient : {state.evidence_sufficient}")


# ---------------------------------------------------------
# Build answer context
# ---------------------------------------------------------

context = builder.build(state)

print(f"Context Grounded    : {context.grounded}")
print(f"Citations           : {len(context.citations)}")


# ---------------------------------------------------------
# Generate answer
# ---------------------------------------------------------

if not context.grounded:
    print("=" * 90)
    print("Insufficient evidence. Answer generation skipped.")
    sys.exit(0)


print("=" * 90)
print("Generating answer with local Ollama model...")
print("=" * 90)

result = generator.generate(context)


# ---------------------------------------------------------
# Attach deterministic citations
# ---------------------------------------------------------

citation_attachment = citation_manager.attach(
    result.answer,
    result.citations,
)


# ---------------------------------------------------------
# Verify citation identifiers
# ---------------------------------------------------------

verification = verifier.verify(
    citation_attachment.answer,
    citation_attachment.citations,
)


# ---------------------------------------------------------
# Extract claims
# ---------------------------------------------------------

claims = claim_extractor.extract(
    citation_attachment.answer,
)


# ---------------------------------------------------------
# Display answer
# ---------------------------------------------------------

print("ANSWER")
print("=" * 90)
print(citation_attachment.answer)


# ---------------------------------------------------------
# Citation verification
# ---------------------------------------------------------

print("=" * 90)
print("VERIFICATION")
print("=" * 90)

print(f"Passed           : {verification.passed}")
print(f"Cited IDs        : {verification.cited_ids}")
print(f"Invalid citations: {verification.invalid_citations}")
print(f"Reason           : {verification.reason}")


# ---------------------------------------------------------
# Grounding status
# ---------------------------------------------------------

print("=" * 90)

print(f"Grounded : {result.grounded}")
print(
    f"Citations: {len(citation_attachment.citations)}"
)


# ---------------------------------------------------------
# Claim verification
# ---------------------------------------------------------

print("=" * 90)
print("CLAIM VERIFICATION")
print("=" * 90)

citation_ids = verifier.CITATION_PATTERN.findall(
    citation_attachment.answer
)

citation_verifications = []

for index, claim in enumerate(claims):

    if not citation_ids:
        break

    citation_id = citation_ids[
        min(index, len(citation_ids) - 1)
    ]

    claim_result = claim_verifier.verify(
        claim,
        citation_id,
        citation_attachment.citations,
    )

    citation_verifications.append(
        claim_result
    )

    print(
        f"{claim_result.claim_id}: "
        f"supported={claim_result.supported}, "
        f"citation={claim_result.citation_id}, "
        f"score={claim_result.overlap_score}"
    )

    print(
        f"Reason: {claim_result.reason}"
    )


all_claims_supported = (
    len(citation_verifications) == len(claims)
    and all(
        item.supported
        for item in citation_verifications
    )
)

print()
print(
    f"All Claims Supported: {all_claims_supported}"
)


# ---------------------------------------------------------
# Final status
# ---------------------------------------------------------

print("=" * 90)
print("FINAL STATUS")
print("=" * 90)

print(f"Grounded              : {result.grounded}")
print(
    f"Citation Verification : {verification.passed}"
)
print(f"Claims Extracted      : {len(claims)}")
print(
    f"Claims Supported      : "
    f"{all_claims_supported}"
)

print("=" * 90)
print("Local generation test completed!")