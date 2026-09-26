from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.query_router import QueryRouter
from app.retrieval.query_transformer import QueryTransformer
from app.retrieval.reranker import Reranker
from app.retrieval.structured_retriever import StructuredRetriever


class RAGRetriever:
    def __init__(self):
        self.query_router = QueryRouter()
        self.query_transformer = QueryTransformer()
        self.hybrid_retriever = HybridRetriever()
        self.reranker = Reranker()
        self.structured_retriever = StructuredRetriever()

    def search(
        self,
        query: str,
        candidate_k: int = 5,
        top_k: int = 3,
    ) -> list[dict]:

        # ---------------------------------------------------------
        # 1. Query routing
        # ---------------------------------------------------------
        route = self.query_router.route(query)

        # ---------------------------------------------------------
        # 2. Query transformation
        # ---------------------------------------------------------
        transformed_query = self.query_transformer.transform(query)

        # ---------------------------------------------------------
        # 3. Adaptive retrieval depth
        # ---------------------------------------------------------
        if route.route == "complex":
            candidate_k = max(candidate_k, 8)
            top_k = max(top_k, 5)

        # ---------------------------------------------------------
        # 4. Hybrid retrieval
        #    Dense + BM25 + RRF
        # ---------------------------------------------------------
        hybrid_results = self.hybrid_retriever.search(
            transformed_query,
            top_k=candidate_k,
        )

        # ---------------------------------------------------------
        # 5. Structured retrieval
        #    Deterministic row-level retrieval for CSV data
        # ---------------------------------------------------------
        structured_results = self.structured_retriever.search(
            query,
            top_k=top_k,
        )

        # ---------------------------------------------------------
        # 6. Combine retrieval results
        # ---------------------------------------------------------
        candidates = hybrid_results + structured_results

        # ---------------------------------------------------------
        # 7. Deduplicate candidates by chunk_id
        # ---------------------------------------------------------
        unique_candidates = {}

        for result in candidates:
            chunk_id = str(result["chunk_id"])

            if chunk_id not in unique_candidates:
                unique_candidates[chunk_id] = result
                continue

            existing = unique_candidates[chunk_id]

            existing_score = max(
                existing.get("score", 0.0),
                existing.get("rerank_score", 0.0),
            )

            new_score = max(
                result.get("score", 0.0),
                result.get("rerank_score", 0.0),
            )

            if new_score > existing_score:
                unique_candidates[chunk_id] = result

        candidates = list(unique_candidates.values())

        # ---------------------------------------------------------
        # 8. Rerank combined evidence
        # ---------------------------------------------------------
        results = self.reranker.rerank(
            transformed_query,
            candidates,
            top_k=top_k,
        )

        # ---------------------------------------------------------
        # 9. Preserve structured retrieval information
        # ---------------------------------------------------------
        for result in results:
            result["original_query"] = query
            result["retrieval_query"] = transformed_query
            result["route"] = route.route
            result["route_reason"] = route.reason

            # Make sure this field always exists.
            result["structured_match"] = result.get(
                "structured_match",
                False,
            )

        return results