from dataclasses import dataclass


@dataclass
class RetrievalMetrics:
    recall_at_k: float
    mrr: float
    ndcg_at_k: float


def recall_at_k(
    retrieved_sections: list[str],
    relevant_sections: list[str],
    k: int,
) -> float:
    """
    Measures whether at least one relevant section
    appears in the top-k retrieved results.
    """

    if not relevant_sections:
        return 0.0

    top_k = retrieved_sections[:k]

    relevant = set(relevant_sections)

    return (
        1.0
        if any(section in relevant for section in top_k)
        else 0.0
    )


def reciprocal_rank(
    retrieved_sections: list[str],
    relevant_sections: list[str],
) -> float:
    """
    Measures how high the first relevant result appears.

    Example:
        relevant result at rank 1 -> 1.0
        rank 2 -> 0.5
        rank 3 -> 0.333...
    """

    relevant = set(relevant_sections)

    for rank, section in enumerate(
        retrieved_sections,
        start=1,
    ):
        if section in relevant:
            return 1.0 / rank

    return 0.0


def ndcg_at_k(
    retrieved_sections: list[str],
    relevant_sections: list[str],
    k: int,
) -> float:
    """
    Computes normalized discounted cumulative gain.

    Relevant sections receive relevance = 1.
    Non-relevant sections receive relevance = 0.
    """

    if not relevant_sections:
        return 0.0

    top_k = retrieved_sections[:k]
    relevant = set(relevant_sections)

    dcg = 0.0

    for rank, section in enumerate(
        top_k,
        start=1,
    ):
        if section in relevant:
            dcg += 1.0 / _log2(rank + 1)

    ideal_hits = min(
        len(relevant_sections),
        k,
    )

    idcg = sum(
        1.0 / _log2(rank + 1)
        for rank in range(1, ideal_hits + 1)
    )

    if idcg == 0:
        return 0.0

    return dcg / idcg


def _log2(value: int) -> float:
    """
    Small internal log2 helper.
    """

    import math

    return math.log2(value)