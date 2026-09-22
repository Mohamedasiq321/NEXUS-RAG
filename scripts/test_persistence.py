from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.ingestion.loaders.txt_loader import load_txt
from app.ingestion.processors.chunker import create_chunks
from app.retrieval.embedding_service import EmbeddingService
from app.storage.document_repository import DocumentRepository
from app.storage.chunk_repository import ChunkRepository


BASE_DIR = Path(__file__).resolve().parent.parent

file_path = (
    BASE_DIR
    / "data"
    / "documents"
    / "sample"
    / "remote_work_policy.txt"
)


# 1. Load document
document = load_txt(str(file_path))

# 2. Create structure-aware chunks
chunks = create_chunks(document)

# 3. Generate embeddings
embedding_service = EmbeddingService()
texts = [chunk.content for chunk in chunks]
embeddings = embedding_service.embed_texts(texts)

# 4. Save document
document_repository = DocumentRepository()
document_repository.save(document)

# 5. Save chunks + embeddings
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