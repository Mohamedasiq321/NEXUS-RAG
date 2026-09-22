class QueryDecomposer:
    """
    Decomposes complex questions into smaller retrieval queries.

    Initial implementation uses deterministic rules.
    A model-based planner can be introduced later.
    """

    def decompose(self, query: str) -> list[str]:
        cleaned_query = " ".join(query.strip().split())

        if not cleaned_query:
            raise ValueError("Query cannot be empty.")

        lowered = cleaned_query.lower()

        if " and " in lowered:
            parts = cleaned_query.split(" and ")

            queries = [
                part.strip().rstrip("?")
                for part in parts
                if part.strip()
            ]

            if len(queries) > 1:
                return queries

        return [cleaned_query.rstrip("?")]