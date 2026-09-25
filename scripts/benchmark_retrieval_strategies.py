import json
from pathlib import Path
import sys


BACKEND_DIR = (
    Path(__file__).resolve().parent.parent / "backend"
)

sys.path.insert(0, str(BACKEND_DIR))


from app.evaluation.metrics import (
    recall_at_k,
    reciprocal_rank,
    ndcg_at_k,
)
from app.retrieval.rag_retriever import RAGRetriever
from app.retrieval.dense_retriever import DenseRetriever
from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.reranker import Reranker


PROJECT_ROOT = Path(__file__).resolve().parent.parent

EVALUATION_FILE = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "rag_eval.json"
)

TOP_K = 5
CANDIDATE_K = 8


def load_dataset():
    with open(
        EVALUATION_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def evaluate_strategy(
    strategy_name,
    search_function,
    dataset,
):
    recall_scores = []
    mrr_scores = []
    ndcg_scores = []

    print()
    print("=" * 90)
    print(strategy_name)
    print("=" * 90)

    for item in dataset:

        query = item["query"]
        relevant_sections = item[
            "relevant_sections"
        ]

        results = search_function(query)

        retrieved_sections = [
            result["section"]
            for result in results
        ]

        recall = recall_at_k(
            retrieved_sections,
            relevant_sections,
            TOP_K,
        )

        mrr = reciprocal_rank(
            retrieved_sections,
            relevant_sections,
        )

        ndcg = ndcg_at_k(
            retrieved_sections,
            relevant_sections,
            TOP_K,
        )

        recall_scores.append(recall)
        mrr_scores.append(mrr)
        ndcg_scores.append(ndcg)

        print()
        print(f"Query: {query}")
        print(
            f"Retrieved: {retrieved_sections}"
        )
        print(
            f"Recall@{TOP_K}: {recall:.4f} | "
            f"MRR: {mrr:.4f} | "
            f"NDCG@{TOP_K}: {ndcg:.4f}"
        )

    return {
        "recall": sum(recall_scores)
        / len(recall_scores),
        "mrr": sum(mrr_scores)
        / len(mrr_scores),
        "ndcg": sum(ndcg_scores)
        / len(ndcg_scores),
    }


def main():

    dataset = load_dataset()

    print(
        "NEXUS-RAG RETRIEVAL STRATEGY BENCHMARK"
    )
    print("=" * 90)

    print("Loading retrieval components...")

    dense = DenseRetriever()
    bm25 = BM25Retriever()
    hybrid = HybridRetriever()
    reranker = Reranker()
    rag_retriever = RAGRetriever()

    results = {}

    # -----------------------------------------------------
    # Dense Retrieval
    # -----------------------------------------------------

    results["Dense"] = evaluate_strategy(
        "DENSE RETRIEVAL",
        lambda query: dense.search(
            query,
            top_k=TOP_K,
        ),
        dataset,
    )

    # -----------------------------------------------------
    # BM25 Retrieval
    # -----------------------------------------------------

    results["BM25"] = evaluate_strategy(
        "BM25 RETRIEVAL",
        lambda query: bm25.search(
            query,
            top_k=TOP_K,
        ),
        dataset,
    )

    # -----------------------------------------------------
    # Hybrid Retrieval + RRF
    # -----------------------------------------------------

    results["Hybrid"] = evaluate_strategy(
        "HYBRID RETRIEVAL + RRF",
        lambda query: hybrid.search(
            query,
            top_k=TOP_K,
        ),
        dataset,
    )

    # -----------------------------------------------------
    # Hybrid + Reranking
    # -----------------------------------------------------

    def hybrid_reranked_search(query):

        candidates = hybrid.search(
            query,
            top_k=CANDIDATE_K,
        )

        return reranker.rerank(
            query,
            candidates,
            top_k=TOP_K,
        )

    results["Hybrid + Reranking"] = (
        evaluate_strategy(
            "HYBRID + CROSS-ENCODER RERANKING",
            hybrid_reranked_search,
            dataset,
        )
    )
    # -----------------------------------------------------
    # Adaptive RAG Retrieval
    # -----------------------------------------------------

    results["Adaptive RAG"] = evaluate_strategy(
        "ADAPTIVE RAG RETRIEVAL",
        lambda query: rag_retriever.search(
            query=query,
            candidate_k=CANDIDATE_K,
            top_k=TOP_K,
        ),
        dataset,
    )
    # -----------------------------------------------------
    # Final comparison
    # -----------------------------------------------------

    print()
    print("=" * 90)
    print("FINAL BENCHMARK")
    print("=" * 90)

    print(
        f"{'Strategy':<30}"
        f"{'Recall@5':>12}"
        f"{'MRR':>12}"
        f"{'NDCG@5':>12}"
    )

    print("-" * 66)

    for strategy, metrics in results.items():

        print(
            f"{strategy:<30}"
            f"{metrics['recall']:>12.4f}"
            f"{metrics['mrr']:>12.4f}"
            f"{metrics['ndcg']:>12.4f}"
        )

    print()
    print(
        "Retrieval strategy benchmark completed!"
    )


if __name__ == "__main__":
    main()