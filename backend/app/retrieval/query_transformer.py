class QueryTransformer:
    """
    Converts natural-language queries into retrieval-oriented
    queries using deterministic normalization and synonym expansion.

    The original wording is preserved whenever possible so that
    lexical retrieval remains effective while semantic synonyms
    are also available.
    """

    PHRASE_EXPANSIONS = {
        "work from home": "remote work",
        "working from home": "remote work",
        "work-from-home": "remote work",
        "wfh": "remote work",
        "home working": "remote work",
        "remote working": "remote work",
        "remote-work": "remote work",
    }

    TERM_EXPANSIONS = {
        "staff": "employees",
        "worker": "employees",
        "workers": "employees",
        "personnel": "employees",
        "dept": "department",
        "depts": "departments",
        "mgr": "manager",
        "managers": "manager",
        "remote days": "remote days per week",
    }

    def transform(self, query: str) -> str:
        cleaned_query = " ".join(query.strip().split())

        if not cleaned_query:
            raise ValueError("Query cannot be empty.")

        transformed_query = cleaned_query.lower()

        # Normalize punctuation variants.
        transformed_query = (
            transformed_query
            .replace("–", "-")
            .replace("—", "-")
        )

        expansions = []

        # Preserve the original phrase and append its retrieval synonym.
        for phrase in sorted(
            self.PHRASE_EXPANSIONS,
            key=len,
            reverse=True,
        ):
            if phrase in transformed_query:
                replacement = self.PHRASE_EXPANSIONS[phrase]

                if replacement not in transformed_query:
                    expansions.append(replacement)

        # Apply safe terminology normalization.
        for term in sorted(
            self.TERM_EXPANSIONS,
            key=len,
            reverse=True,
        ):
            replacement = self.TERM_EXPANSIONS[term]

            if term in transformed_query:
                transformed_query = transformed_query.replace(
                    term,
                    replacement,
                )

        # Add semantic expansions without destroying the original query.
        if expansions:
            transformed_query = (
                f"{transformed_query} "
                + " ".join(dict.fromkeys(expansions))
            )

        transformed_query = " ".join(
            transformed_query.split()
        )

        return transformed_query