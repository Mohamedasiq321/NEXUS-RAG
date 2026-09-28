from dataclasses import dataclass


@dataclass
class QueryRoute:
    route: str
    reason: str
    query_type: str = "semantic"


class QueryRouter:
    """
    Determines the retrieval characteristics of a user query.

    route:
        - standard
        - complex

    query_type:
        - semantic
        - structured
        - hybrid

    The routing logic is deterministic and explainable.
    """

    STRUCTURED_INDICATORS = {
        "employee",
        "employees",
        "employee_id",
        "department",
        "departments",
        "role",
        "roles",
        "status",
        "approved",
        "pending",
        "rejected",
        "eligible",
        "not eligible",
        "remote days",
        "remote day",
        "days per week",
        "records",
        "record",
        "rows",
        "row",
        "csv",
        "table",
        "dataset",
    }

    COMPLEX_INDICATORS = {
        "and",
        "also",
        "both",
        "compare",
        "comparison",
        "difference",
        "differences",
        "multiple",
        "requirements",
        "restrictions",
        "versus",
        "vs",
        "while",
        "whereas",
        "between",
        "across",
    }

    SEMANTIC_INDICATORS = {
        "why",
        "explain",
        "explanation",
        "describe",
        "overview",
        "policy",
        "rule",
        "rules",
        "guideline",
        "guidelines",
        "security",
        "exception",
        "exceptions",
        "purpose",
    }

    def route(self, query: str) -> QueryRoute:
        cleaned_query = " ".join(query.strip().split())

        if not cleaned_query:
            raise ValueError("Query cannot be empty.")

        normalized_query = cleaned_query.lower()
        words = normalized_query.split()

        structured_matches = self._find_matches(
            normalized_query,
            self.STRUCTURED_INDICATORS,
        )

        complex_matches = self._find_matches(
            normalized_query,
            self.COMPLEX_INDICATORS,
        )

        semantic_matches = self._find_matches(
            normalized_query,
            self.SEMANTIC_INDICATORS,
        )

        is_long_query = len(words) > 15
        is_multi_aspect = bool(complex_matches)
        has_structured_intent = bool(structured_matches)
        has_semantic_intent = bool(semantic_matches)

        # Structured + multiple aspects = hybrid complex query.
        if has_structured_intent and (
            is_multi_aspect or is_long_query
        ):
            return QueryRoute(
                route="complex",
                reason=(
                    "Query combines structured data conditions "
"with multiple aspects or a longer formulation."
                ),
                query_type="hybrid",
            )

        # Structured-only query.
        if has_structured_intent:
            return QueryRoute(
                route="standard",
                reason=(
                    "Query contains structured-data indicators "
                    "such as employee, status, department, role, "
                    "or numeric record conditions."
                ),
                query_type="structured",
            )

        # Complex semantic query.
        if is_long_query or is_multi_aspect:
            return QueryRoute(
                route="complex",
                reason=(
                    "Query contains multiple aspects or is "
                    "relatively long."
                ),
                query_type="semantic",
            )

        # Standard semantic query.
        if has_semantic_intent:
            return QueryRoute(
                route="standard",
                reason=(
                    "Query appears to request semantic information "
                    "such as policy, explanation, rules, or context."
                ),
                query_type="semantic",
            )

        return QueryRoute(
            route="standard",
            reason="Query appears to require standard retrieval.",
            query_type="semantic",
        )

    @staticmethod
    def _find_matches(
        query: str,
        indicators: set[str],
    ) -> list[str]:
        words = set(query.split())
        matches = []

        for indicator in indicators:
            if " " in indicator:
                if indicator in query:
                    matches.append(indicator)
            elif indicator in words:
                matches.append(indicator)

        return matches