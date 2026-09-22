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


class EvidenceAggregator:
    """
    Aggregates evidence retrieved across multiple retrieval hops.

    Duplicate chunks are merged while preserving the hop numbers
    that contributed the evidence.
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
                score = float(result["rerank_score"])

                if chunk_id not in evidence_map:
                    evidence_map[chunk_id] = Evidence(
                        chunk_id=chunk_id,
                        document_id=str(result["document_id"]),
                        section=result["section"],
                        content=result["content"],
                        score=score,
                        source_hops=[hop.hop_number],
                    )

                else:
                    evidence = evidence_map[chunk_id]

                    evidence.score = max(
                        evidence.score,
                        score,
                    )

                    if hop.hop_number not in evidence.source_hops:
                        evidence.source_hops.append(
                            hop.hop_number
                        )

        ranked_evidence = sorted(
            evidence_map.values(),
            key=lambda evidence: evidence.score,
            reverse=True,
        )

        return ranked_evidence[:top_k]