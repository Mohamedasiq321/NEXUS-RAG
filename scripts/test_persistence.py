from pathlib import Path
import sys
import uuid

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.ingestion.loaders.txt_loader import load_txt
from app.ingestion.processors.chunker import create_chunks
from app.retrieval.embedding_service import EmbeddingService
from app.storage.document_repository import DocumentRepository
from app.storage.chunk_repository import ChunkRepository
from app.database.connection import get_connection


BASE_DIR = Path(__file__).resolve().parent.parent

file_path = (
    BASE_DIR
    / "data"
    / "documents"
    / "sample"
    / "remote_work_policy.txt"
)


# Remove any previous copy of the sample document
with get_connection() as connection:
    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM documents WHERE file_name = %s",
            ("remote_work_policy.txt",),
        )
    connection.commit()


document = load_txt(str(file_path))

# Use a fresh UUID for this clean test run
document.document_id = str(uuid.uuid4())

chunks = create_chunks(document)

embedding_service = EmbeddingService()

texts = [chunk.content for chunk in chunks]
embeddings = embedding_service.embed_texts(texts)

document_repository = DocumentRepository()
document_repository.save(document)

chunk_repository = ChunkRepository()
chunk_repository.save_many(chunks, embeddings)


print("Persistence pipeline completed successfully!")
print("=" * 60)
print(f"Document      : {document.file_name}")
print(f"Document ID   : {document.document_id}")
print(f"Chunks saved  : {len(chunks)}")
print(f"Embeddings    : {len(embeddings)}")
print(f"Dimension     : {embedding_service.dimension()}")
print("=" * 60)