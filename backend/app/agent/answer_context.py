
from dataclasses import dataclass

from app.agent.state import AgentState


@dataclass
class AnswerContext:
    query: str
    context: str
    citations: list[dict]
    grounded: bool


class AnswerContextBuilder:
    """
    Builds a controlled context package for answer generation.

    Only evidence that passed the agent's sufficiency check
    is allowed into the generation context.
    """

    def build(self, state: AgentState) -> AnswerContext:

        if not state.evidence_sufficient:
            return AnswerContext(
                query=state.original_query,
                context="",
                citations=[],
                grounded=False,
            )

        context_blocks = []
        citations = []

        for index, evidence in enumerate(
            state.evidence,
            start=1,
        ):
            citation_id = f"S{index}"

            context_blocks.append(
                f"[{citation_id}] "
                f"Section: {evidence['section']}\n"
                f"{evidence['content']}"
            )

            citations.append(
                {
                    "citation_id": citation_id,
                    "chunk_id": evidence["chunk_id"],
                    "document_id": evidence["document_id"],
                    "section": evidence["section"],
                    "content": evidence["content"],
                    "source_hops": evidence["source_hops"],
                    "score": evidence["score"],
                    "structured_match": evidence.get(
                        "structured_match",
                        False,
                    ),
                    "structured_exact_match": evidence.get(
                        "structured_exact_match",
                        False,
                    ),
                    "matched_conditions": evidence.get(
                        "matched_conditions",
                        {},
                    ),
                }
            )

        context = "\n\n".join(context_blocks)

       

        return AnswerContext(
            query=state.original_query,
            context=context,
            citations=citations,
            grounded=True,
        )
