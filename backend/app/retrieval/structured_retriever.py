import re

from app.database.connection import get_connection


class StructuredRetriever:
    """
    Deterministic row-level retrieval for structured documents.

    Structured retrieval is intentionally separate from semantic
    retrieval because structured questions often require exact
    condition matching.

    Example:

        Query:
            "Which employees are approved for 3 remote days per week?"

        Required conditions:
            remote_days_per_week = 3
            status = Approved

        A row is an exact structured match only when ALL extracted
        conditions are satisfied.
    """

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:

        conditions = self._extract_conditions(query)

        if not conditions:
            return []

        query_sql = """
        SELECT
            chunk_id,
            document_id,
            chunk_index,
            section,
            content,
            metadata
        FROM chunks
        WHERE metadata->>'structured_data' = 'true'
        ORDER BY chunk_index;
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_sql)
                rows = cursor.fetchall()

        results = []

        for row in rows:
            chunk_id = row[0]
            document_id = row[1]
            chunk_index = row[2]
            section = row[3]
            content = row[4]
            metadata = row[5] or {}

            matched_conditions = self._match_conditions(
                content=content,
                metadata=metadata,
                conditions=conditions,
            )

            matched_count = len(matched_conditions)
            required_count = len(conditions)

            # -----------------------------------------------------
            # Exact structured matching
            #
            # Every extracted condition must match.
            # -----------------------------------------------------
            if matched_count != required_count:
                continue

            results.append(
                {
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "chunk_index": chunk_index,
                    "section": section,
                    "content": content,
                    "metadata": metadata,

                    # Exact structured match score.
                    "score": float(matched_count),

                    # Explicit structured retrieval metadata.
                    "structured_match": True,
                    "structured_exact_match": True,
                    "matched_conditions": matched_conditions,
                    "matched_condition_count": matched_count,
                    "required_condition_count": required_count,
                }
            )

        # ---------------------------------------------------------
        # Deterministic ranking
        #
        # Exact matches have already passed the AND filter.
        # Prefer more specific matches first, then stable row order.
        # ---------------------------------------------------------
        results.sort(
            key=lambda result: (
                result["matched_condition_count"],
                -result["chunk_index"],
            ),
            reverse=True,
        )

        return results[:top_k]

    def _extract_conditions(
        self,
        query: str,
    ) -> dict[str, str]:

        query_lower = " ".join(
            query.lower().split()
        )

        conditions: dict[str, str] = {}

        # ---------------------------------------------------------
        # Remote-days condition
        #
        # Supports:
        #   "3 remote days"
        #   "3 remote days per week"
        #   "3 days per week"
        #   "remote days: 3"
        #   "remote_days_per_week: 3"
        # ---------------------------------------------------------

        days_patterns = [
            r"\b(\d+)\s+(?:remote\s+)?days?(?:\s+per\s+week)?\b",
            r"\bremote[\s_]+days[\s_]+per[\s_]+week\s*[:=]?\s*(\d+)\b",
        ]

        for pattern in days_patterns:
            match = re.search(
                pattern,
                query_lower,
            )

            if match:
                conditions[
                    "remote_days_per_week"
                ] = match.group(1)
                break

        # ---------------------------------------------------------
        # Status conditions
        # ---------------------------------------------------------

        if re.search(
            r"\bnot\s+eligible\b",
            query_lower,
        ):
            conditions["status"] = "Not Eligible"

        elif re.search(
            r"\bapproved\b",
            query_lower,
        ):
            conditions["status"] = "Approved"

        elif re.search(
            r"\bpending\b",
            query_lower,
        ):
            conditions["status"] = "Pending"

        elif re.search(
            r"\brejected\b",
            query_lower,
        ):
            conditions["status"] = "Rejected"

        return conditions

    def _match_conditions(
        self,
        content: str,
        metadata: dict,
        conditions: dict[str, str],
    ) -> dict[str, str]:

        content_lower = content.lower()

        matched_conditions: dict[str, str] = {}

        for field, expected_value in conditions.items():

            # -----------------------------------------------------
            # Remote days
            # -----------------------------------------------------
            if field == "remote_days_per_week":

                expected_number = str(
                    expected_value
                )

                pattern = (
                    rf"\bremote_days_per_week\s*:\s*"
                    rf"{re.escape(expected_number)}\b"
                )

                if re.search(
                    pattern,
                    content_lower,
                ):
                    matched_conditions[field] = (
                        expected_value
                    )

            # -----------------------------------------------------
            # Status
            # -----------------------------------------------------
            elif field == "status":

                expected_status = (
                    expected_value.lower()
                )

                pattern = (
                    r"\bstatus\s*:\s*"
                    rf"{re.escape(expected_status)}\b"
                )

                if re.search(
                    pattern,
                    content_lower,
                ):
                    matched_conditions[field] = (
                        expected_value
                    )

        return matched_conditions