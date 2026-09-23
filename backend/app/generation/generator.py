from dataclasses import dataclass

from app.agent.answer_context import AnswerContext


@dataclass
class GeneratedAnswer:
    answer: str
    citations: list[dict]
    grounded: bool


class AnswerGenerator:
    """
    Provider-agnostic answer generation interface.

    The initial implementation is deterministic so the
    generation contract can be tested before connecting
    an actual LLM provider.
    """

    def generate(
        self,
        context: AnswerContext,
    ) -> GeneratedAnswer:

        if not context.grounded:
            return GeneratedAnswer(
                answer=(
                    "I don't have sufficient evidence in the "
                    "available knowledge base to answer this question."
                ),
                citations=[],
                grounded=False,
            )

        answer_parts = []

        for citation in context.citations:
            citation_id = citation["citation_id"]

            matching_block = self._find_context_block(
                context.context,
                citation_id,
            )

            if matching_block:
                answer_parts.append(
                    f"[{citation_id}] {matching_block}"
                )

        answer = (
            "Based on the available evidence:\n\n"
            + "\n\n".join(answer_parts)
        )

        return GeneratedAnswer(
            answer=answer,
            citations=context.citations,
            grounded=True,
        )

    @staticmethod
    def _find_context_block(
        context: str,
        citation_id: str,
    ) -> str:

        marker = f"[{citation_id}]"

        for block in context.split("\n\n"):
            if block.startswith(marker):
                lines = block.split("\n", maxsplit=1)

                if len(lines) == 2:
                    return lines[1]

        return ""