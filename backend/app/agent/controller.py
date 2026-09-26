
from app.agent.evidence_evaluator import EvidenceEvaluator
from app.agent.query_refiner import QueryRefiner
from app.agent.state import AgentState
from app.retrieval.evidence_aggregator import EvidenceAggregator
from app.retrieval.multi_hop_retriever import MultiHopRetriever


class AgentController:
    """
    Controls the NEXUS-RAG agentic retrieval workflow.

    Workflow:
        Query
          ↓
        Multi-hop retrieval
          ↓
        Evidence aggregation
          ↓
        Adaptive evidence evaluation
          ↓
        Query refinement if evidence is insufficient
          ↓
        Controlled retry

    The controller adapts the required evidence count:
        - Simple / single-hop query → 1 strong evidence item
        - Multi-hop query → 2 strong evidence items

    Set minimum_evidence explicitly to override the adaptive behavior.
    """

    def __init__(
        self,
        max_iterations: int = 2,
        minimum_evidence: int | None = None,
    ):
        self.retriever = MultiHopRetriever()
        self.aggregator = EvidenceAggregator()
        self.refiner = QueryRefiner()

        self.max_iterations = max_iterations
        self.minimum_evidence = minimum_evidence

        # Default evaluator.
        # The required evidence count is updated adaptively
        # inside run() based on query complexity.
        self.evaluator = EvidenceEvaluator(
            minimum_evidence=1,
        )

    def run(self, query: str) -> AgentState:
        state = AgentState(
            original_query=query,
        )

        current_query = query

        print("\n" + "=" * 70)
        print("NEXUS-RAG AGENT DEBUG")
        print("=" * 70)
        print(f"Original Query: {query}")

        while state.iteration < self.max_iterations:

            state.iteration += 1

            print("\n" + "-" * 70)
            print(f"RETRIEVAL ITERATION {state.iteration}")
            print("-" * 70)
            print(f"Current Query: {current_query}")

            # ---------------------------------------------------------
            # 1. RETRIEVE EVIDENCE
            # ---------------------------------------------------------
            hops = self.retriever.search(
                current_query,
                top_k=3,
            )

            print(f"\nHops Retrieved: {len(hops)}")

            # Store subqueries from the current retrieval pass
            state.subqueries = [
                hop.query
                for hop in hops
            ]

            for hop in hops:
                print(
                    f"\n  Hop {hop.hop_number}"
                    f" | Query: {hop.query}"
                    f" | Results: {len(hop.results)}"
                )

                for rank, result in enumerate(
                    hop.results,
                    start=1,
                ):
                    print(
                        f"    {rank}. "
                        f"Section={result.get('section')} | "
                        f"RerankScore={result.get('rerank_score')} | "
                        f"Similarity={result.get('similarity')}"
                    )

            # ---------------------------------------------------------
            # 2. AGGREGATE EVIDENCE
            # ---------------------------------------------------------
            evidence = self.aggregator.aggregate(
                hops,
                top_k=5,
            )

            print(f"\nAggregated Evidence: {len(evidence)}")

            for rank, item in enumerate(
                evidence,
                start=1,
            ):
                print(
                    f"  {rank}. "
                    f"Section={item.section} | "
                    f"Score={item.score:.6f} | "
                    f"Hops={item.source_hops}"
                )

            # Convert Evidence objects into agent state dictionaries
            state.evidence = [
                {
                    "chunk_id": item.chunk_id,
                    "document_id": item.document_id,
                    "section": item.section,
                    "content": item.content,
                    "score": item.score,
                    "source_hops": item.source_hops,
                }
                for item in evidence
            ]

            # ---------------------------------------------------------
            # 3. DETERMINE REQUIRED EVIDENCE
            # ---------------------------------------------------------
            if self.minimum_evidence is not None:
                required_evidence = self.minimum_evidence
                requirement_mode = "explicit override"
            else:
                # Single-hop/simple query:
                # one strong source can be sufficient.
                #
                # Multi-hop query:
                # require multiple independent strong sources.
                required_evidence = (
                    2
                    if len(hops) > 1
                    else 1
                )
                requirement_mode = "adaptive"

            self.evaluator = EvidenceEvaluator(
                minimum_evidence=required_evidence,
            )

            print("\nEvidence Requirement:")
            print(f"  Mode: {requirement_mode}")
            print(f"  Required Strong Evidence: {required_evidence}")
            print(
                f"  Minimum Score: "
                f"{self.evaluator.minimum_score}"
            )

            # ---------------------------------------------------------
            # 4. EVALUATE EVIDENCE
            # ---------------------------------------------------------
            evaluation = self.evaluator.evaluate(
                state.evidence,
            )

            state.evidence_sufficient = evaluation.sufficient

            print("\nEvidence Evaluation:")
            print(f"  Sufficient: {evaluation.sufficient}")
            print(f"  Confidence: {evaluation.confidence:.6f}")
            print(f"  Reason: {evaluation.reason}")

            # ---------------------------------------------------------
            # 5. STOP WHEN EVIDENCE IS SUFFICIENT
            # ---------------------------------------------------------
            if evaluation.sufficient:
                print("\n✓ Evidence accepted.")
                print("Proceeding to answer generation.")
                break

            print("\n✗ Evidence rejected.")

            # ---------------------------------------------------------
            # 6. STOP IF RETRY BUDGET IS EXHAUSTED
            # ---------------------------------------------------------
            if state.iteration >= self.max_iterations:
                print(
                    "Retry budget exhausted. "
                    "Returning insufficient-evidence state."
                )
                break

            # ---------------------------------------------------------
            # 7. REFINE QUERY
            # ---------------------------------------------------------
            refinement = self.refiner.refine(
                current_query,
            )

            print("\nQuery Refinement:")
            print(f"  Previous: {current_query}")
            print(f"  Refined:  {refinement.refined_query}")

            current_query = refinement.refined_query

        state.retrieval_query = current_query

        print("\n" + "=" * 70)
        print("FINAL AGENT STATE")
        print("=" * 70)
        print(f"Iterations: {state.iteration}")
        print(f"Evidence Count: {len(state.evidence)}")
        print(
            f"Evidence Sufficient: "
            f"{state.evidence_sufficient}"
        )
        print(f"Retrieval Query: {state.retrieval_query}")
        print("=" * 70 + "\n")

        return state

