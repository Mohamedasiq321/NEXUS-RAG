from dataclasses import dataclass

from app.retrieval.query_decomposer import QueryDecomposer
from app.retrieval.rag_retriever import RAGRetriever


@dataclass
class RetrievalHop:
    hop_number: int
    query: str
    results: list[dict]


class MultiHopRetriever:
    def __init__(self):
        self.decomposer = QueryDecomposer()
        self.retriever = RAGRetriever()

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[RetrievalHop]:

        subqueries = self.decomposer.decompose(query)

        hops = []

        for hop_number, subquery in enumerate(
            subqueries,
            start=1,
        ):
            results = self.retriever.search(
                subquery,
                candidate_k=5,
                top_k=top_k,
            )

            hops.append(
                RetrievalHop(
                    hop_number=hop_number,
                    query=subquery,
                    results=results,
                )
            )

        return hops