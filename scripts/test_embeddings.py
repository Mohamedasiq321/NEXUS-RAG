from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.ingestion.loaders.txt_loader import load_txt
from app.ingestion.processors.chunker import create_chunks
from app.retrieval.embedding_service import EmbeddingService


BASE_DIR = Path(__file__).resolve().parent.parent

file_path = (
    BASE_DIR
    / "data"
    / "documents"
    / "sample"
    / "remote_work_policy.txt"
)

# Load document
document = load_txt(str(file_path))

# Create chunks
chunks = create_chunks(document)

# Create embedding service
embedding_service = EmbeddingService()

# Extract chunk texts
texts = [chunk.content for chunk in chunks]

# Generate embeddings
embeddings = embedding_service.embed_texts(texts)

print("Embedding pipeline working!")
print("=" * 60)
print(f"Document      : {document.file_name}")
print(f"Total chunks  : {len(chunks)}")
print(f"Embeddings    : {len(embeddings)}")
print(f"Dimension     : {embedding_service.dimension()}")
print("=" * 60)

for chunk, embedding in zip(chunks, embeddings):
    print(
        f"Chunk {chunk.chunk_index} | "
        f"{chunk.section} | "
        f"Vector size: {len(embedding)}"
    )

print("=" * 60)
print("First chunk first 5 values:")
print(embeddings[0][:5])