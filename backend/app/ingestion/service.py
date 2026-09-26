from pathlib import Path

from app.ingestion.loaders.txt_loader import load_txt
from app.ingestion.loaders.pdf_loader import load_pdf
from app.ingestion.processors.chunker import create_chunks
from app.retrieval.embedding_service import EmbeddingService
from app.storage.chunk_repository import ChunkRepository
from app.storage.document_repository import DocumentRepository
from app.ingestion.loaders.docx_loader import load_docx

class DocumentIngestionService:
    def __init__(self):
        self.document_repository = DocumentRepository()
        self.chunk_repository = ChunkRepository()
        self.embedding_service = EmbeddingService()

    def ingest(self, file_path: str) -> dict:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        extension = path.suffix.lower()

        # Select the appropriate document loader
        if extension == ".txt":
            document = load_txt(str(path))
        elif extension == ".pdf":
            document = load_pdf(str(path))
        elif extension == ".docx":
            document = load_docx(str(path))
        else:
            raise ValueError(
                "Currently supported file types: .txt, .pdf, .docx"
            )

        # Prevent duplicate documents
        existing_document = self.document_repository.find_by_content_hash(
            document.content_hash
        )

        if existing_document:
            return {
                "document_id": existing_document.document_id,
                "file_name": existing_document.file_name,
                "file_type": existing_document.file_type,
                "chunk_count": self._count_chunks(
                    existing_document.document_id
                ),
                "embedding_dimension": self.embedding_service.dimension(),
                "source": existing_document.source,
                "version": existing_document.version,
                "duplicate": True,
                "message": "This document is already indexed.",
            }

        # Structure-aware chunking
        chunks = create_chunks(document)

        if not chunks:
            raise ValueError(
                "No usable chunks were created from the document."
            )

        # Generate embeddings
        texts = [chunk.content for chunk in chunks]
        embeddings = self.embedding_service.embed_texts(texts)

        # Store document and chunks
        self.document_repository.save(document)
        self.chunk_repository.save_many(chunks, embeddings)

        return {
            "document_id": document.document_id,
            "file_name": document.file_name,
            "file_type": document.file_type,
            "chunk_count": len(chunks),
            "embedding_dimension": self.embedding_service.dimension(),
            "source": document.source,
            "version": document.version,
            "duplicate": False,
            "message": "Document indexed successfully.",
        }

    def _count_chunks(self, document_id: str) -> int:
        from app.database.connection import get_connection

        query = """
        SELECT COUNT(*)
        FROM chunks
        WHERE document_id = %s;
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (document_id,))
                row = cursor.fetchone()

        return int(row[0])