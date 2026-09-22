from dataclasses import dataclass


@dataclass
class QueryRoute:
    route: str
    reason: str


class QueryRouter:
    """
    Routes queries to an appropriate retrieval strategy.

    Initial implementation uses deterministic rules.
    A model-based router can be introduced later.
    """

    def route(self, query: str) -> QueryRoute:
        cleaned_query = " ".join(query.strip().split())

        if not cleaned_query:
            raise ValueError("Query cannot be empty.")

        words = cleaned_query.lower().split()

        multi_aspect_indicators = {
            "and",
            "also",
            "both",
            "compare",
            "difference",
            "differences",
            "multiple",
            "requirements",
            "restrictions",
        }

        if len(words) > 15 or any(
            indicator in words
            for indicator in multi_aspect_indicators
        ):
            return QueryRoute(
                route="complex",
                reason="Query contains multiple aspects or is relatively long.",
            )

        return QueryRoute(
            route="standard",
            reason="Query appears to require standard retrieval.",
        )