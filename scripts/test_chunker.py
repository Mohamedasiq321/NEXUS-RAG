from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.ingestion.loaders.txt_loader import load_txt
from app.ingestion.processors.chunker import create_chunks


BASE_DIR = Path(__file__).resolve().parent.parent

file_path = (
    BASE_DIR
    / "data"
    / "documents"
    / "sample"
    / "remote_work_policy.txt"
)

document = load_txt(str(file_path))

chunks = create_chunks(document)

print(f"Document: {document.file_name}")
print(f"Total chunks: {len(chunks)}")
print("=" * 60)

for chunk in chunks:
    print(f"Chunk index : {chunk.chunk_index}")
    print(f"Chunk ID    : {chunk.chunk_id}")
    print(f"Section     : {chunk.section}")
    print(f"Characters  : {len(chunk.content)}")
    print(f"Metadata    : {chunk.metadata}")
    print(f"Content     : {chunk.content[:150]}")
    print("-" * 60)