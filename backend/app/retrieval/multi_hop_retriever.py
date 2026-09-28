from dataclasses import dataclass

from app.retrieval.metadata_filter import MetadataFilterExtractor
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
        self.metadata_filter_extractor = MetadataFilterExtractor()

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[RetrievalHop]:

        subqueries = self.decomposer.decompose(query)

        # Extract constraints ONCE from the original query.
        #
        # These constraints must survive query decomposition.
        # Example:
        #
        # "Which Engineering employees have 3 remote days
        #  and are approved?"
        #
        # Every hop must retain:
        # department = Engineering
        # remote_days_per_week = 3
        # status = Approved
        metadata_filters = (
            self.metadata_filter_extractor.extract(query)
        )

        retrieval_top_k = top_k

        lowered_query = query.lower()

        structured_indicators = [
            "employee",
            "employees",
            "row",
            "rows",
            "department",
            "departments",
            "role",
            "roles",
            "approved",
            "not eligible",
            "status",
            "remote days",
            "remote day",
        ]

        if any(
            indicator in lowered_query
            for indicator in structured_indicators
        ):
            retrieval_top_k = max(
                top_k,
                6,
            )

        hops = []

        for hop_number, subquery in enumerate(
            subqueries,
            start=1,
        ):

            results = self.retriever.search(
                subquery,
                candidate_k=6,
                top_k=retrieval_top_k,
                metadata_filters=metadata_filters,
            )

            hops.append(
                RetrievalHop(
                    hop_number=hop_number,
                    query=subquery,
                    results=results,
                )
            )

        return hops