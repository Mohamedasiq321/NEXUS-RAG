from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.query_router import QueryRouter
from app.retrieval.query_transformer import QueryTransformer
from app.retrieval.reranker import Reranker


class RAGRetriever:
    def __init__(self):
        self.query_router = QueryRouter()
        self.query_transformer = QueryTransformer()
        self.hybrid_retriever = HybridRetriever()
        self.reranker = Reranker()

    def search(
        self,
        query: str,
        candidate_k: int = 5,
        top_k: int = 3,
    ) -> list[dict]:

        route = self.query_router.route(query)

        transformed_query = self.query_transformer.transform(query)

        # Adaptive retrieval depth based on query complexity
        if route.route == "complex":
            candidate_k = max(candidate_k, 8)
            top_k = max(top_k, 5)

        candidates = self.hybrid_retriever.search(
            transformed_query,
            top_k=candidate_k,
        )

        results = self.reranker.rerank(
            transformed_query,
            candidates,
            top_k=top_k,
        )

        for result in results:
            result["original_query"] = query
            result["retrieval_query"] = transformed_query
            result["route"] = route.route
            result["route_reason"] = route.reason

        return results