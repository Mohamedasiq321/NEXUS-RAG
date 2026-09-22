from app.database.connection import get_connection
from app.retrieval.embedding_service import EmbeddingService


class DenseRetriever:
    def __init__(self):
        self.embedding_service = EmbeddingService()

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        query_embedding = self.embedding_service.embed_text(query)

        vector = "[" + ",".join(map(str, query_embedding)) + "]"

        sql = """
        SELECT
            chunk_id,
            document_id,
            chunk_index,
            section,
            content,
            metadata,
            1 - (embedding <=> %s::vector) AS similarity
        FROM chunks
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    sql,
                    (vector, vector, top_k),
                )

                rows = cursor.fetchall()

        return [
            {
                "chunk_id": row[0],
                "document_id": row[1],
                "chunk_index": row[2],
                "section": row[3],
                "content": row[4],
                "metadata": row[5],
                "similarity": float(row[6]),
            }
            for row in rows
        ]