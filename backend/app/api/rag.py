import re
import time
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel

from app.agent.answer_context import AnswerContextBuilder
from app.agent.answer_verifier import AnswerVerifier
from app.agent.claim_extractor import ClaimExtractor
from app.agent.claim_verifier import ClaimVerifier
from app.agent.citation_manager import CitationManager
from app.agent.controller import AgentController
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


class RAGTelemetry(BaseModel):
    request_id: str

    route: str
    iterations: int
    retrieval_query: str
    subqueries: list[str]

    evidence_count: int
    evidence_sections: list[str]
    structured_evidence_count: int
    evidence_sufficient: bool

    citations_count: int
    claims_count: int
    supported_claims_count: int

    timings_ms: dict[str, float]


class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    grounded: bool
    verification_passed: bool
    claims_supported: bool
    citations: list[CitationResponse]
    telemetry: RAGTelemetry


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
    request_id = str(uuid4())

    total_start = time.perf_counter()

    # ---------------------------------------------------------
    # 1. Agentic retrieval
    # ---------------------------------------------------------

    retrieval_start = time.perf_counter()

    state = controller.run(
        request.query
    )

    retrieval_time_ms = (
        time.perf_counter() - retrieval_start
    ) * 1000

    # ---------------------------------------------------------
    # Build retrieval telemetry
    # ---------------------------------------------------------

    evidence_sections = [
        str(item.get("section", ""))
        for item in state.evidence
        if item.get("section")
    ]

    structured_evidence_count = sum(
        1
        for item in state.evidence
        if item.get("structured_exact_match")
    )

    retrieval_telemetry = {
        "request_id": request_id,
        "route": "agentic",
        "iterations": state.iteration,
        "retrieval_query": state.retrieval_query,
        "subqueries": state.subqueries,
        "evidence_count": len(state.evidence),
        "evidence_sections": evidence_sections,
        "structured_evidence_count": (
            structured_evidence_count
        ),
        "evidence_sufficient": (
            state.evidence_sufficient
        ),
        "citations_count": 0,
        "claims_count": 0,
        "supported_claims_count": 0,
        "timings_ms": {
            "retrieval": round(
                retrieval_time_ms,
                2,
            ),
        },
    }

    # ---------------------------------------------------------
    # 2. Build grounded answer context
    # ---------------------------------------------------------

    context_start = time.perf_counter()

    context = context_builder.build(
        state
    )

    context_time_ms = (
        time.perf_counter() - context_start
    ) * 1000

    retrieval_telemetry["timings_ms"][
        "context_build"
    ] = round(
        context_time_ms,
        2,
    )

    # ---------------------------------------------------------
    # 3. Grounded refusal
    # ---------------------------------------------------------

    if not context.grounded:

        retrieval_telemetry["timings_ms"][
            "total"
        ] = round(
            (time.perf_counter() - total_start)
            * 1000,
            2,
        )

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
            telemetry=RAGTelemetry(
                **retrieval_telemetry
            ),
        )

    # ---------------------------------------------------------
    # 4. Generate answer
    # ---------------------------------------------------------

    generation_start = time.perf_counter()

    result = generator.generate(
        context
    )

    generation_time_ms = (
        time.perf_counter() - generation_start
    ) * 1000

    retrieval_telemetry["timings_ms"][
        "generation"
    ] = round(
        generation_time_ms,
        2,
    )

    # ---------------------------------------------------------
    # 5. Attach deterministic citations
    # ---------------------------------------------------------

    citation_start = time.perf_counter()

    citation_attachment = citation_manager.attach(
        result.answer,
        result.citations,
    )

    citation_time_ms = (
        time.perf_counter() - citation_start
    ) * 1000

    retrieval_telemetry["timings_ms"][
        "citation_attachment"
    ] = round(
        citation_time_ms,
        2,
    )

    # ---------------------------------------------------------
    # 6. Verify citation placement
    # ---------------------------------------------------------

    verification_start = time.perf_counter()

    verification = answer_verifier.verify(
        citation_attachment.answer,
        citation_attachment.citations,
    )

    verification_time_ms = (
        time.perf_counter() - verification_start
    ) * 1000

    retrieval_telemetry["timings_ms"][
        "citation_verification"
    ] = round(
        verification_time_ms,
        2,
    )

    # ---------------------------------------------------------
    # 7. Extract claims
    # ---------------------------------------------------------

    claims = claim_extractor.extract(
        citation_attachment.answer,
    )

    # ---------------------------------------------------------
    # 8. Verify claims
    # ---------------------------------------------------------

    claim_results = []

    for claim in claims:

        supporting_citations = _find_claim_citations(
            claim.text,
            citation_attachment.citations,
        )

        # No supporting citation
        if not supporting_citations:

            claim_results.append(
                claim_verifier.verify(
                    claim,
                    "",
                    citation_attachment.citations,
                )
            )

            continue

        # One supporting citation
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

        # Multiple supporting citations
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
    # 9. Overall claim verification
    # ---------------------------------------------------------

    supported_claims_count = sum(
        1
        for item in claim_results
        if item.supported
    )

    claims_supported = (
        len(claim_results) == len(claims)
        and len(claims) > 0
        and all(
            item.supported
            for item in claim_results
        )
    )

    verification_passed = (
        verification.passed
        and claims_supported
    )

    grounded = (
        result.grounded
        and verification_passed
    )

    # ---------------------------------------------------------
    # 10. Build API citations
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
    # 11. Complete telemetry
    # ---------------------------------------------------------

    retrieval_telemetry[
        "citations_count"
    ] = len(citations)

    retrieval_telemetry[
        "claims_count"
    ] = len(claims)

    retrieval_telemetry[
        "supported_claims_count"
    ] = supported_claims_count

    retrieval_telemetry["timings_ms"][
        "total"
    ] = round(
        (time.perf_counter() - total_start)
        * 1000,
        2,
    )

    # ---------------------------------------------------------
    # 12. Return final response
    # ---------------------------------------------------------

    return RAGQueryResponse(
        query=request.query,
        answer=citation_attachment.answer,
        grounded=grounded,
        verification_passed=verification_passed,
        claims_supported=claims_supported,
        citations=citations,
        telemetry=RAGTelemetry(
            **retrieval_telemetry
        ),
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

    claim_upper = claim_text.upper()

    # ---------------------------------------------------------
    # Structured entity matching
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
    # Lexical fallback
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