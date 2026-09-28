from dataclasses import dataclass

from app.evaluation.metrics import (
    RetrievalMetrics,
    ndcg_at_k,
    recall_at_k,
    reciprocal_rank,
)
from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.dense_retriever import DenseRetriever
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.rag_retriever import RAGRetriever


@dataclass
class EvaluationQuery:
    query: str
    relevant_sections: list[str]


@dataclass
class EvaluationResult:
    query: str
    retrieved_sections: list[str]
    relevant_sections: list[str]
    metrics: RetrievalMetrics


class RetrievalEvaluator:
    def __init__(self):
        self.dense_retriever = DenseRetriever()
        self.bm25_retriever = BM25Retriever()
        self.hybrid_retriever = HybridRetriever()
        self.rag_retriever = RAGRetriever()

    def evaluate_strategy(
        self,
        strategy: str,
        dataset: list[EvaluationQuery],
        k: int = 5,
    ) -> dict:
        query_results = []

        for item in dataset:
            retrieved = self._retrieve(
                strategy=strategy,
                query=item.query,
                top_k=k,
            )

            retrieved_sections = [
                str(result.get("section", ""))
                for result in retrieved
            ]

            metrics = RetrievalMetrics(
                recall_at_k=recall_at_k(
                    retrieved_sections,
                    item.relevant_sections,
                    k,
                ),
                mrr=reciprocal_rank(
                    retrieved_sections,
                    item.relevant_sections,
                ),
                ndcg_at_k=ndcg_at_k(
                    retrieved_sections,
                    item.relevant_sections,
                    k,
                ),
            )

            query_results.append(
                EvaluationResult(
                    query=item.query,
                    retrieved_sections=retrieved_sections,
                    relevant_sections=item.relevant_sections,
                    metrics=metrics,
                )
            )

        if not query_results:
            return {
                "strategy": strategy,
                "query_count": 0,
                "metrics": {
                    "recall_at_k": 0.0,
                    "mrr": 0.0,
                    "ndcg_at_k": 0.0,
                },
                "queries": [],
            }

        count = len(query_results)

        average_recall = (
            sum(
                result.metrics.recall_at_k
                for result in query_results
            )
            / count
        )

        average_mrr = (
            sum(
                result.metrics.mrr
                for result in query_results
            )
            / count
        )

        average_ndcg = (
            sum(
                result.metrics.ndcg_at_k
                for result in query_results
            )
            / count
        )

        return {
            "strategy": strategy,
            "query_count": count,
            "metrics": {
                "recall_at_k": round(average_recall, 4),
                "mrr": round(average_mrr, 4),
                "ndcg_at_k": round(average_ndcg, 4),
            },
            "queries": [
                {
                    "query": result.query,
                    "retrieved_sections": result.retrieved_sections,
                    "relevant_sections": result.relevant_sections,
                    "metrics": {
                        "recall_at_k": round(
                            result.metrics.recall_at_k,
                            4,
                        ),
                        "mrr": round(
                            result.metrics.mrr,
                            4,
                        ),
                        "ndcg_at_k": round(
                            result.metrics.ndcg_at_k,
                            4,
                        ),
                    },
                }
                for result in query_results
            ],
        }

    def evaluate_all(
        self,
        dataset: list[EvaluationQuery],
        k: int = 5,
    ) -> dict:
        strategies = [
            "dense",
            "bm25",
            "hybrid",
            "adaptive",
        ]

        results = [
            self.evaluate_strategy(
                strategy,
                dataset,
                k,
            )
            for strategy in strategies
        ]

        return {
            "k": k,
            "query_count": len(dataset),
            "results": results,
        }

    def _retrieve(
        self,
        strategy: str,
        query: str,
        top_k: int,
    ) -> list[dict]:
        if strategy == "dense":
            return self.dense_retriever.search(
                query,
                top_k=top_k,
            )

        if strategy == "bm25":
            return self.bm25_retriever.search(
                query,
                top_k=top_k,
            )

        if strategy == "hybrid":
            return self.hybrid_retriever.search(
                query,
                top_k=top_k,
            )

        if strategy == "adaptive":
            return self.rag_retriever.search(
                query,
                candidate_k=max(top_k, 6),
                top_k=top_k,
            )

        raise ValueError(
            f"Unsupported evaluation strategy: {strategy}"
        )


def build_default_dataset() -> list[EvaluationQuery]:
    """
    Ground-truth benchmark for the indexed NEXUS remote-work
    policy document.

    Relevant section names are based on the actual sections
    currently stored in the database.
    """

    return [
        EvaluationQuery(
            query="What is the remote work policy?",
            relevant_sections=[
                "Document Information",
            ],
        ),
        EvaluationQuery(
            query="Who is eligible for remote work?",
            relevant_sections=[
                "1. Eligibility",
            ],
        ),
        EvaluationQuery(
            query="How many remote days are allowed per week?",
            relevant_sections=[
                "2. Remote Work Allowance",
            ],
        ),
        EvaluationQuery(
            query="What are the requirements for working remotely?",
            relevant_sections=[
                "1. Eligibility",
                "3. Equipment",
                "4. Security Requirements",
            ],
        ),
        EvaluationQuery(
            query="Can employees work remotely after probation?",
            relevant_sections=[
                "1. Eligibility",
            ],
        ),
        EvaluationQuery(
            query="What conditions can restrict remote work?",
            relevant_sections=[
                "1. Eligibility",
                "5. Exceptions",
            ],
        ),
    ]