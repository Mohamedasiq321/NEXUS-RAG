from dataclasses import dataclass
import re


@dataclass
class VerificationResult:
    passed: bool
    reason: str
    cited_ids: list[str]
    invalid_citations: list[str]


class AnswerVerifier:
    """
    Verifies that a generated answer uses only valid
    citation identifiers supplied by the retrieval layer.

    Initial implementation is deterministic and
    model-agnostic.
    """

    CITATION_PATTERN = re.compile(r"\[(S\d+)\]")

    def verify(
        self,
        answer: str,
        citations: list[dict],
    ) -> VerificationResult:

        if not answer.strip():
            return VerificationResult(
                passed=False,
                reason="Generated answer is empty.",
                cited_ids=[],
                invalid_citations=[],
            )

        available_ids = {
            citation["citation_id"]
            for citation in citations
        }

        cited_ids = self.CITATION_PATTERN.findall(answer)

        invalid_citations = [
            citation_id
            for citation_id in cited_ids
            if citation_id not in available_ids
        ]

        if invalid_citations:
            return VerificationResult(
                passed=False,
                reason=(
                    "Answer contains citation identifiers "
                    "that are not present in the retrieved evidence."
                ),
                cited_ids=cited_ids,
                invalid_citations=invalid_citations,
            )

        if not cited_ids:
            return VerificationResult(
                passed=False,
                reason=(
                    "Answer does not contain any citation "
                    "to the retrieved evidence."
                ),
                cited_ids=[],
                invalid_citations=[],
            )

        return VerificationResult(
            passed=True,
            reason=(
                "All cited evidence identifiers are valid."
            ),
            cited_ids=cited_ids,
            invalid_citations=[],
        )