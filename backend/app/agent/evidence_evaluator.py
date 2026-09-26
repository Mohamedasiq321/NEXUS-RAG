from dataclasses import dataclass


@dataclass
class EvidenceEvaluation:
    sufficient: bool
    confidence: float
    reason: str


class EvidenceEvaluator:
    """
    Evaluates whether retrieved evidence is sufficient
    to proceed toward answer generation.
    """

    def __init__(
        self,
        minimum_score: float = 0.70,
        minimum_evidence: int = 1,
    ):
        self.minimum_score = minimum_score
        self.minimum_evidence = minimum_evidence

    def _get_score(self, item: dict) -> float:
        """
        Use the reranker score when available.
        Fall back to the generic score field for compatibility
        with earlier retrieval components.
        """

        if item.get("rerank_score") is not None:
            return float(item["rerank_score"])

        if item.get("score") is not None:
            return float(item["score"])

        if item.get("similarity") is not None:
            return float(item["similarity"])

        return 0.0

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

        scored_evidence = [
            (item, self._get_score(item))
            for item in evidence
        ]

        strong_evidence = [
            (item, score)
            for item, score in scored_evidence
            if score >= self.minimum_score
        ]

        if len(strong_evidence) >= self.minimum_evidence:
            best_score = max(
                score
                for _, score in strong_evidence
            )

            return EvidenceEvaluation(
                sufficient=True,
                confidence=min(best_score, 1.0),
                reason=(
                    f"{len(strong_evidence)} evidence item(s) "
                    "meet the minimum confidence threshold."
                ),
            )

        best_score = max(
            score
            for _, score in scored_evidence
        )

        return EvidenceEvaluation(
            sufficient=False,
            confidence=min(best_score, 1.0),
            reason=(
                "Retrieved evidence does not contain enough "
                "high-confidence supporting material."
            ),
        )