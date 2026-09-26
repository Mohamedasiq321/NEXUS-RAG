from pydantic import BaseModel
from fastapi import APIRouter

from app.agent.controller import AgentController
from app.agent.answer_context import AnswerContextBuilder
from app.agent.answer_verifier import AnswerVerifier
from app.agent.citation_manager import CitationManager
from app.agent.claim_extractor import ClaimExtractor
from app.agent.claim_verifier import ClaimVerifier
from app.generation.ollama_generator import (
    OllamaAnswerGenerator,
)


router = APIRouter(
    prefix="/api/rag",
    tags=["RAG"],
)


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


@router.post(
    "/query",
    response_model=RAGQueryResponse,
)
def query_rag(
    request: RAGQueryRequest,
):

    state = controller.run(
        request.query
    )

    context = context_builder.build(
        state
    )

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

    result = generator.generate(
        context
    )

    citation_attachment = (
        citation_manager.attach(
            result.answer,
            result.citations,
        )
    )

    verification = answer_verifier.verify(
        citation_attachment.answer,
        citation_attachment.citations,
    )

    claims = claim_extractor.extract(
        citation_attachment.answer,
    )

    citation_ids = (
        answer_verifier.CITATION_PATTERN.findall(
            citation_attachment.answer
        )
    )

    claim_results = []

    for index, claim in enumerate(claims):

        if not citation_ids:
            break

        citation_id = citation_ids[
            min(
                index,
                len(citation_ids) - 1,
            )
        ]

        claim_result = (
            claim_verifier.verify(
                claim,
                citation_id,
                citation_attachment.citations,
            )
        )

        claim_results.append(
            claim_result
        )

    claims_supported = (
        len(claim_results) == len(claims)
        and all(
            item.supported
            for item in claim_results
        )
    )

    citations = [
        CitationResponse(
            citation_id=item["citation_id"],
            section=item["section"],
            chunk_id=str(item["chunk_id"]),
            document_id=str(
                item["document_id"]
            ),
        )
        for item in citation_attachment.citations
    ]

    return RAGQueryResponse(
        query=request.query,
        answer=citation_attachment.answer,
        grounded=result.grounded,
        verification_passed=verification.passed,
        claims_supported=claims_supported,
        citations=citations,
    )