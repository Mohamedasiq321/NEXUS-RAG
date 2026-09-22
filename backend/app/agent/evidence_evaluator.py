from dataclasses import dataclass


@dataclass
class EvidenceEvaluation:
    sufficient: bool
    confidence: float
    reason: str


class EvidenceEvaluator:
    """
    Evaluates whether the retrieved evidence is sufficient
    to proceed toward answer generation.
    """

    def __init__(
        self,
        minimum_score: float = 0.70,
        minimum_evidence: int = 2,
    ):
        self.minimum_score = minimum_score
        self.minimum_evidence = minimum_evidence

    def evaluate(
        self,
        evidence: list[dict],
    ) -> EvidenceEvaluation:

        if not evidence:
            return EvidenceEvaluation(
                sufficient=False,
                confidence=0.0,
                reason="No evidence was retrieved.",
            )

        strong_evidence = [
            item
            for item in evidence
            if item.get("score", 0.0) >= self.minimum_score
        ]

        if len(strong_evidence) >= self.minimum_evidence:
            confidence = min(
                strong_evidence[0]["score"],
                1.0,
            )

            return EvidenceEvaluation(
                sufficient=True,
                confidence=confidence,
                reason=(
                    f"{len(strong_evidence)} evidence items "
                    "meet the minimum confidence threshold."
                ),
            )

        best_score = max(
            item.get("score", 0.0)
            for item in evidence
        )

        return EvidenceEvaluation(
            sufficient=False,
            confidence=min(best_score, 1.0),
            reason=(
                "Retrieved evidence does not contain enough "
                "high-confidence supporting material."
            ),
        )