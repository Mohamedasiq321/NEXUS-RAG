from dataclasses import dataclass, field


@dataclass
class AgentState:
    """
    Shared state passed through the NEXUS-RAG agent workflow.
    """

    original_query: str

    route: str = ""
    route_reason: str = ""

    retrieval_query: str = ""

    subqueries: list[str] = field(default_factory=list)

    evidence: list[dict] = field(default_factory=list)

    evidence_sufficient: bool = False

    answer: str = ""

    citations: list[dict] = field(default_factory=list)

    verification_passed: bool = False
    verification_reason: str = ""

    iteration: int = 0