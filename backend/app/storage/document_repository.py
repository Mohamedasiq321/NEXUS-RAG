from psycopg.types.json import Jsonb

from app.database.connection import get_connection
from app.models.document import Document


class DocumentRepository:

    def find_by_content_hash(
        self,
        content_hash: str,
    ) -> Document | None:

        query = """
        SELECT
            document_id,
            file_name,
            file_type,
            source,
            version,
            metadata,
            created_at
        FROM documents
        WHERE content_hash = %s
        LIMIT 1;
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (content_hash,),
                )

                row = cursor.fetchone()

        if not row:
            return None

        return Document(
            document_id=str(row[0]),
            file_name=row[1],
            file_type=row[2],
            content="",
            source=row[3] or "",
            version=row[4] or "",
            content_hash=content_hash,
            metadata=row[5] or {},
            created_at=row[6],
        )

    def save(self, document: Document) -> None:

        query = """
        INSERT INTO documents (
            document_id,
            file_name,
            file_type,
            source,
            version,
            content_hash,
            metadata,
            created_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        ON CONFLICT (document_id) DO NOTHING;
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        document.document_id,
                        document.file_name,
                        document.file_type,
                        document.source,
                        document.version,
                        document.content_hash,
                        Jsonb(document.metadata),
                        document.created_at,
                    ),
                )

            connection.commit()