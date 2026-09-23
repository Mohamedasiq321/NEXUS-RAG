from dataclasses import dataclass


@dataclass
class QueryRefinement:
    original_query: str
    refined_query: str
    reason: str


class QueryRefiner:
    """
    Generates a deterministic retrieval refinement when
    the initial evidence is insufficient.

    This is intentionally model-agnostic so an LLM planner
    can replace it later without changing the controller.
    """

    REFINEMENTS = {
        "bonus": "employee bonus compensation incentive policy",
        "salary": "employee salary compensation pay policy",
        "leave": "employee leave vacation time-off policy",
        "vacation": "employee vacation leave time-off policy",
        "insurance": "employee health insurance benefits policy",
        "benefits": "employee benefits policy",
        "promotion": "employee promotion career advancement policy",
    }

    def refine(self, query: str) -> QueryRefinement:
        cleaned_query = " ".join(query.strip().split())

        if not cleaned_query:
            raise ValueError("Query cannot be empty.")

        lowered = cleaned_query.lower()

        for keyword, expansion in self.REFINEMENTS.items():
            if keyword in lowered:
                return QueryRefinement(
                    original_query=cleaned_query,
                    refined_query=(
                        f"{cleaned_query} {expansion}"
                    ),
                    reason=(
                        f"Expanded the query using the "
                        f"domain concept '{keyword}'."
                    ),
                )

        return QueryRefinement(
            original_query=cleaned_query,
            refined_query=(
                f"{cleaned_query} policy requirements "
                "rules guidelines"
            ),
            reason=(
                "Added policy-oriented retrieval terms "
                "to improve lexical and semantic matching."
            ),
        )