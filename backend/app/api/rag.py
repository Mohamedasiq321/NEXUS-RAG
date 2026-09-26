from pydantic import BaseModel
from fastapi import APIRouter

from app.agent.controller import AgentController
from app.agent.answer_context import AnswerContextBuilder
from app.agent.answer_verifier import AnswerVerifier
from app.agent.citation_manager import CitationManager
from app.agent.claim_extractor import ClaimExtractor
from app.agent.claim_verifier import ClaimVerifier
from app.generation.ollama_generator import OllamaAnswerGenerator


router = APIRouter(
    prefix="/api/rag",
    tags=["RAG"],
)


# =============================================================
# Request / Response Models
# =============================================================


class RAGQueryRequest(BaseModel):
    query: str


class CitationResponse(BaseModel):
    citation_id: str
    section: str
    chunk_id: str
    document_id: str


class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    grounded: bool
    verification_passed: bool
    claims_supported: bool
    citations: list[CitationResponse]


# =============================================================
# Components
# =============================================================


controller = AgentController(
    max_iterations=2,
    minimum_evidence=None,
)

context_builder = AnswerContextBuilder()

generator = OllamaAnswerGenerator(
    model="qwen2.5:1.5b",
)

answer_verifier = AnswerVerifier()
citation_manager = CitationManager()
claim_extractor = ClaimExtractor()
claim_verifier = ClaimVerifier()


# =============================================================
# RAG Query Endpoint
# =============================================================


@router.post(
    "/query",
    response_model=RAGQueryResponse,
)
def query_rag(
    request: RAGQueryRequest,
):

    # ---------------------------------------------------------
    # 1. Agentic retrieval
    # ---------------------------------------------------------

    state = controller.run(
        request.query
    )

    # ---------------------------------------------------------
    # 2. Build grounded answer context
    # ---------------------------------------------------------

    context = context_builder.build(
        state
    )

    # ---------------------------------------------------------
    # If retrieval did not provide sufficient evidence,
    # stop here and return a grounded refusal.
    # ---------------------------------------------------------

    if not context.grounded:
        return RAGQueryResponse(
            query=request.query,
            answer=(
                "I don't have sufficient evidence "
                "in the available knowledge base "
                "to answer this question."
            ),
            grounded=False,
            verification_passed=False,
            claims_supported=False,
            citations=[],
        )

    # ---------------------------------------------------------
    # 3. Generate answer
    # ---------------------------------------------------------

    result = generator.generate(
        context
    )

    # ---------------------------------------------------------
    # 4. Attach deterministic citations
    # ---------------------------------------------------------

    citation_attachment = citation_manager.attach(
        result.answer,
        result.citations,
    )

    # ---------------------------------------------------------
    # 5. Verify citation placement
    # ---------------------------------------------------------

    verification = answer_verifier.verify(
        citation_attachment.answer,
        citation_attachment.citations,
    )

    # ---------------------------------------------------------
    # 6. Extract claims
    # ---------------------------------------------------------

    claims = claim_extractor.extract(
        citation_attachment.answer,
    )

    # ---------------------------------------------------------
    # 7. Verify every claim against all evidence
    #    that supports that claim.
    #
    # This is important for claims such as:
    #
    # "EMP005 and EMP001 are approved..."
    #
    # where one claim depends on two separate rows.
    # ---------------------------------------------------------

    claim_results = []

    for claim in claims:

        supporting_citations = _find_claim_citations(
            claim.text,
            citation_attachment.citations,
        )

        # -----------------------------------------------------
        # No supporting citation found
        # -----------------------------------------------------

        if not supporting_citations:

            claim_results.append(
                claim_verifier.verify(
                    claim,
                    "",
                    citation_attachment.citations,
                )
            )

            continue

        # -----------------------------------------------------
        # One supporting citation
        # -----------------------------------------------------

        if len(supporting_citations) == 1:

            citation_id = supporting_citations[0][
                "citation_id"
            ]

            claim_results.append(
                claim_verifier.verify(
                    claim,
                    citation_id,
                    citation_attachment.citations,
                )
            )

            continue

        # -----------------------------------------------------
        # Multiple supporting citations
        #
        # Example:
        #
        # EMP005 → S1
        # EMP001 → S2
        #
        # The claim must be verified against both.
        # -----------------------------------------------------

        combined_citation_id = (
            "__combined_claim_evidence__"
        )

        combined_citation = {
            "citation_id": combined_citation_id,
            "section": "Combined Evidence",
            "chunk_id": "combined",
            "document_id": "combined",
            "content": "\n".join(
                str(
                    citation.get(
                        "content",
                        "",
                    )
                )
                for citation in supporting_citations
            ),
            "structured_match": any(
                citation.get(
                    "structured_match",
                    False,
                )
                for citation in supporting_citations
            ),
            "structured_exact_match": all(
                citation.get(
                    "structured_exact_match",
                    False,
                )
                for citation in supporting_citations
            ),
            "matched_conditions": {},
        }

        verification_citations = (
            citation_attachment.citations
            + [combined_citation]
        )

        claim_results.append(
            claim_verifier.verify(
                claim,
                combined_citation_id,
                verification_citations,
            )
        )

    # ---------------------------------------------------------
    # 8. Overall claim verification
    # ---------------------------------------------------------

    claims_supported = (
        len(claim_results) == len(claims)
        and len(claims) > 0
        and all(
            item.supported
            for item in claim_results
        )
    )

    # ---------------------------------------------------------
    # 9. Final verification status
    #
    # The answer is considered verified only when:
    #
    #   - citation placement passes
    #   - every extracted claim is supported
    # ---------------------------------------------------------

    verification_passed = (
        verification.passed
        and claims_supported
    )

    grounded = (
        result.grounded
        and verification_passed
    )

    # ---------------------------------------------------------
    # 10. Build API citation response
    # ---------------------------------------------------------

    citations = [
        CitationResponse(
            citation_id=item["citation_id"],
            section=item["section"],
            chunk_id=str(
                item["chunk_id"]
            ),
            document_id=str(
                item["document_id"]
            ),
        )
        for item in citation_attachment.citations
    ]

    # ---------------------------------------------------------
    # 11. Return final RAG response
    # ---------------------------------------------------------

    return RAGQueryResponse(
        query=request.query,
        answer=citation_attachment.answer,
        grounded=grounded,
        verification_passed=verification_passed,
        claims_supported=claims_supported,
        citations=citations,
    )


# =============================================================
# Claim → Citation Matching
# =============================================================


def _find_claim_citations(
    claim_text: str,
    citations: list[dict],
) -> list[dict]:

    if not citations:
        return []

    import re

    claim_upper = claim_text.upper()

    # ---------------------------------------------------------
    # 1. Exact structured entity matching
    #
    # Example:
    #
    # "EMP005 and EMP001 are approved..."
    #
    # We return BOTH rows instead of only the first match.
    # ---------------------------------------------------------

    employee_ids = {
        employee_id.upper()
        for employee_id in re.findall(
            r"\bEMP\d+\b",
            claim_upper,
        )
    }

    if employee_ids:

        matched_citations = []

        for citation in citations:

            if not citation.get(
                "structured_exact_match",
                False,
            ):
                continue

            evidence_text = " ".join(
                [
                    str(
                        citation.get(
                            "section",
                            "",
                        )
                    ),
                    str(
                        citation.get(
                            "content",
                            "",
                        )
                    ),
                ]
            ).upper()

            # Only select a citation when it contains
            # an employee explicitly mentioned in the claim.
            if any(
                employee_id in evidence_text
                for employee_id in employee_ids
            ):
                matched_citations.append(
                    citation
                )

        if matched_citations:
            return matched_citations

    # ---------------------------------------------------------
    # 2. Lexical fallback
    # ---------------------------------------------------------

    claim_tokens = _tokenize_claim(
        claim_text
    )

    scored_citations = []

    for citation in citations:

        evidence_text = " ".join(
            [
                str(
                    citation.get(
                        "section",
                        "",
                    )
                ),
                str(
                    citation.get(
                        "content",
                        "",
                    )
                ),
            ]
        )

        evidence_tokens = _tokenize_claim(
            evidence_text
        )

        overlap_score = len(
            claim_tokens.intersection(
                evidence_tokens
            )
        )

        if overlap_score > 0:

            scored_citations.append(
                (
                    overlap_score,
                    citation,
                )
            )

    scored_citations.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        citation
        for _, citation in scored_citations
    ]


# =============================================================
# Claim Tokenization
# =============================================================


def _tokenize_claim(
    text: str,
) -> set[str]:

    import re

    stopwords = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "to",
        "of",
        "for",
        "in",
        "on",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "this",
        "that",
        "their",
        "they",
        "them",
        "with",
        "may",
        "must",
        "can",
        "who",
        "what",
        "how",
        "from",
        "as",
        "by",
        "it",
        "its",
        "have",
        "has",
        "had",
    }

    words = re.findall(
        r"\b[a-zA-Z0-9]+\b",
        text.lower(),
    )

    return {
        word
        for word in words
        if word not in stopwords
    }