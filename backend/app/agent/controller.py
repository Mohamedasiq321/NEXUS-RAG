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
        Evidence evaluation
          ↓
        Query refinement if evidence is insufficient
          ↓
        Controlled retry
    """

    def __init__(
        self,
        max_iterations: int = 2,
        minimum_evidence: int = 2,
    ):
        self.retriever = MultiHopRetriever()
        self.aggregator = EvidenceAggregator()
        self.evaluator = EvidenceEvaluator(
            minimum_evidence=minimum_evidence,
        )
        self.refiner = QueryRefiner()

        self.max_iterations = max_iterations

    def run(self, query: str) -> AgentState:
        state = AgentState(
            original_query=query,
        )

        current_query = query

        while state.iteration < self.max_iterations:

            state.iteration += 1

            # Retrieve evidence
            hops = self.retriever.search(
                current_query,
                top_k=3,
            )

            # Store subqueries from the current retrieval pass
            state.subqueries = [
                hop.query
                for hop in hops
            ]

            # Aggregate evidence
            evidence = self.aggregator.aggregate(
                hops,
                top_k=5,
            )

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

            # Evaluate evidence quality
            evaluation = self.evaluator.evaluate(
                state.evidence,
            )

            state.evidence_sufficient = evaluation.sufficient

            # Stop when evidence is sufficient
            if evaluation.sufficient:
                break

            # Stop if retry budget is exhausted
            if state.iteration >= self.max_iterations:
                break

            # Refine the query before the next retrieval attempt
            refinement = self.refiner.refine(
                current_query,
            )

            current_query = refinement.refined_query

        state.retrieval_query = current_query

        return state