from rank_bm25 import BM25Okapi

from app.database.connection import get_connection


class BM25Retriever:
    def __init__(self):
        self.documents = []
        self.bm25 = None

        self._load_chunks()

    def _load_chunks(self):
        query = """
        SELECT
            chunk_id,
            document_id,
            chunk_index,
            section,
            content,
            metadata
        FROM chunks
        ORDER BY document_id, chunk_index;
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()

        self.documents = [
            {
                "chunk_id": row[0],
                "document_id": row[1],
                "chunk_index": row[2],
                "section": row[3],
                "content": row[4],
                "metadata": row[5],
            }
            for row in rows
        ]

        tokenized_documents = [
            document["content"].lower().split()
            for document in self.documents
        ]

        if tokenized_documents:
            self.bm25 = BM25Okapi(tokenized_documents)

    @staticmethod
    def _matches_metadata(
        metadata: dict,
        metadata_filters: dict[str, str],
    ) -> bool:
        for key, expected_value in metadata_filters.items():
            actual_value = metadata.get(key)

            if actual_value is None:
                return False

            if str(actual_value).strip().lower() != str(
                expected_value
            ).strip().lower():
                return False

        return True

    def search(
        self,
        query: str,
        top_k: int = 5,
        metadata_filters: dict[str, str] | None = None,
    ) -> list[dict]:
        if not self.documents or self.bm25 is None:
            return []

        tokenized_query = query.lower().split()

        scores = self.bm25.get_scores(tokenized_query)

        filters = metadata_filters or {}

        candidate_indices = [
            index
            for index, document in enumerate(self.documents)
            if self._matches_metadata(
                document["metadata"],
                filters,
            )
        ]

        ranked_indices = sorted(
            candidate_indices,
            key=lambda index: scores[index],
            reverse=True,
        )[:top_k]

        results = []

        for index in ranked_indices:
            document = self.documents[index].copy()
            document["score"] = float(scores[index])
            results.append(document)

        return results