class QueryTransformer:
    """
    Transforms user queries into retrieval-oriented queries.

    This first implementation uses deterministic query expansion.
    A model-based transformer can be plugged in later without
    changing the retrieval architecture.
    """

    EXPANSIONS = {
        "work from home": "remote work",
        "working from home": "remote work",
        "wfh": "remote work",
        "home working": "remote work",
        "remote working": "remote work",
    }

    def transform(self, query: str) -> str:
        cleaned_query = " ".join(query.strip().split())

        if not cleaned_query:
            raise ValueError("Query cannot be empty.")

        transformed_query = cleaned_query.lower()

        for phrase, replacement in self.EXPANSIONS.items():
            transformed_query = transformed_query.replace(
                phrase,
                replacement,
            )

        return transformed_query