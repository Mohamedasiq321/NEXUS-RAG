from psycopg.types.json import Jsonb

from app.database.connection import get_connection
from app.models.document import Document


class DocumentRepository:
    def save(self, document: Document) -> None:
        query = """
        INSERT INTO documents (
            document_id,
            file_name,
            file_type,
            source,
            version,
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
                        Jsonb(document.metadata),
                        document.created_at,
                    ),
                )

            connection.commit()