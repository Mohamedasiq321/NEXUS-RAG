import json
from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.retrieval.rag_retriever import RAGRetriever
from app.evaluation.metrics import (
    recall_at_k,
    reciprocal_rank,
    ndcg_at_k,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

EVALUATION_FILE = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "rag_eval.json"
)

TOP_K = 5
CANDIDATE_K = 8


def load_evaluation_dataset():
    with open(
        EVALUATION_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main():
    dataset = load_evaluation_dataset()

    retriever = RAGRetriever()

    recall_scores = []
    mrr_scores = []
    ndcg_scores = []

    print("NEXUS-RAG RETRIEVAL EVALUATION")
    print("=" * 90)

    for item in dataset:

        query = item["query"]
        relevant_sections = item["relevant_sections"]

        results = retriever.search(
            query=query,
            candidate_k=CANDIDATE_K,
            top_k=TOP_K,
        )

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
            f"Relevant: {relevant_sections}"
        )

        print(
            f"Retrieved: {retrieved_sections}"
        )

        print(
            f"Recall@{TOP_K}: "
            f"{recall:.4f}"
        )

        print(
            f"MRR: "
            f"{mrr:.4f}"
        )

        print(
            f"NDCG@{TOP_K}: "
            f"{ndcg:.4f}"
        )

    print()
    print("=" * 90)
    print("OVERALL RESULTS")
    print("=" * 90)

    avg_recall = (
        sum(recall_scores)
        / len(recall_scores)
    )

    avg_mrr = (
        sum(mrr_scores)
        / len(mrr_scores)
    )

    avg_ndcg = (
        sum(ndcg_scores)
        / len(ndcg_scores)
    )

    print(
        f"Average Recall@{TOP_K}: "
        f"{avg_recall:.4f}"
    )

    print(
        f"Average MRR: "
        f"{avg_mrr:.4f}"
    )

    print(
        f"Average NDCG@{TOP_K}: "
        f"{avg_ndcg:.4f}"
    )

    print()
    print(
        "Retrieval evaluation completed!"
    )


if __name__ == "__main__":
    main()