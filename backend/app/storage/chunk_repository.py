from psycopg.types.json import Jsonb

from app.database.connection import get_connection
from app.models.chunk import DocumentChunk

class ChunkRepository:
    def save_many(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError(
                "The number of chunks must match the number of embeddings."
            )

        query = """
        INSERT INTO chunks (
            chunk_id,
            document_id,
            chunk_index,
            section,
            content,
            metadata,
            embedding
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s::vector
        )
        ON CONFLICT (chunk_id) DO NOTHING;
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                for chunk, embedding in zip(chunks, embeddings):
                    vector = "[" + ",".join(map(str, embedding)) + "]"

                    cursor.execute(
                        query,
                        (
                            chunk.chunk_id,
                            chunk.document_id,
                            chunk.chunk_index,
                            chunk.section,
                            chunk.content,
                            Jsonb(chunk.metadata),
                            vector,
                        ),
                    )

            connection.commit()