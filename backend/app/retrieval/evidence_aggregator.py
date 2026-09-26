from dataclasses import dataclass

from app.retrieval.multi_hop_retriever import RetrievalHop


@dataclass
class Evidence:
    chunk_id: str
    document_id: str
    section: str
    content: str
    score: float
    source_hops: list[int]
    structured_match: bool = False
    structured_exact_match: bool = False
    matched_conditions: dict[str, str] | None = None


class EvidenceAggregator:
    """
    Aggregates evidence retrieved across multiple retrieval hops.

    Duplicate chunks are merged while preserving:
    - hop numbers
    - structured retrieval metadata
    - exact condition matches
    """

    def aggregate(
        self,
        hops: list[RetrievalHop],
        top_k: int = 5,
    ) -> list[Evidence]:

        evidence_map: dict[str, Evidence] = {}

        for hop in hops:
            for result in hop.results:

                chunk_id = str(result["chunk_id"])

                score = float(
                    result.get(
                        "rerank_score",
                        result.get("score", 0.0),
                    )
                )

                structured_match = bool(
                    result.get(
                        "structured_match",
                        False,
                    )
                )

                structured_exact_match = bool(
                    result.get(
                        "structured_exact_match",
                        False,
                    )
                )

                matched_conditions = result.get(
                    "matched_conditions"
                )

                if chunk_id not in evidence_map:

                    evidence_map[chunk_id] = Evidence(
                        chunk_id=chunk_id,
                        document_id=str(
                            result["document_id"]
                        ),
                        section=result["section"],
                        content=result["content"],
                        score=score,
                        source_hops=[
                            hop.hop_number
                        ],
                        structured_match=structured_match,
                        structured_exact_match=(
                            structured_exact_match
                        ),
                        matched_conditions=(
                            matched_conditions
                        ),
                    )

                else:

                    evidence = evidence_map[chunk_id]

                    evidence.score = max(
                        evidence.score,
                        score,
                    )

                    evidence.structured_match = (
                        evidence.structured_match
                        or structured_match
                    )

                    evidence.structured_exact_match = (
                        evidence.structured_exact_match
                        or structured_exact_match
                    )

                    if matched_conditions:
                        if evidence.matched_conditions is None:
                            evidence.matched_conditions = {}

                        evidence.matched_conditions.update(
                            matched_conditions
                        )

                    if (
                        hop.hop_number
                        not in evidence.source_hops
                    ):
                        evidence.source_hops.append(
                            hop.hop_number
                        )

        # ---------------------------------------------------------
        # Rank evidence
        #
        # Exact structured matches receive priority for
        # structured queries, while retrieval score remains
        # the secondary ranking signal.
        # ---------------------------------------------------------
        ranked_evidence = sorted(
            evidence_map.values(),
            key=lambda evidence: (
                evidence.structured_exact_match,
                evidence.score,
            ),
            reverse=True,
        )

        return ranked_evidence[:top_k]