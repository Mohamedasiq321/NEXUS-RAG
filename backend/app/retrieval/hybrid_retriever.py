from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.dense_retriever import DenseRetriever


class HybridRetriever:
    def __init__(self):
        self.dense_retriever = DenseRetriever()
        self.bm25_retriever = BM25Retriever()

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:

        dense_results = self.dense_retriever.search(
            query,
            top_k=top_k,
        )

        bm25_results = self.bm25_retriever.search(
            query,
            top_k=top_k,
        )

        return self._reciprocal_rank_fusion(
            dense_results,
            bm25_results,
            top_k,
        )

    def _reciprocal_rank_fusion(
        self,
        dense_results: list[dict],
        bm25_results: list[dict],
        top_k: int,
        k: int = 60,
    ) -> list[dict]:

        fused_results = {}

        for rank, result in enumerate(dense_results, start=1):
            chunk_id = str(result["chunk_id"])

            if chunk_id not in fused_results:
                fused_results[chunk_id] = {
                    **result,
                    "dense_rank": rank,
                    "bm25_rank": None,
                    "rrf_score": 0.0,
                }

            fused_results[chunk_id]["rrf_score"] += 1 / (k + rank)

        for rank, result in enumerate(bm25_results, start=1):
            chunk_id = str(result["chunk_id"])

            if chunk_id not in fused_results:
                fused_results[chunk_id] = {
                    **result,
                    "dense_rank": None,
                    "bm25_rank": rank,
                    "rrf_score": 0.0,
                }

            else:
                fused_results[chunk_id]["bm25_rank"] = rank

            fused_results[chunk_id]["rrf_score"] += 1 / (k + rank)

        ranked_results = sorted(
            fused_results.values(),
            key=lambda result: result["rrf_score"],
            reverse=True,
        )

        return ranked_results[:top_k]