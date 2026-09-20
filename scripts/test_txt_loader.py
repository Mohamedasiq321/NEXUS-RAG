from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.ingestion.loaders.txt_loader import load_txt


BASE_DIR = Path(__file__).resolve().parent.parent

file_path = BASE_DIR / "data" / "documents" / "sample" / "remote_work_policy.txt"

document = load_txt(str(file_path))

print("Document loaded successfully!")
print("-" * 50)
print(f"Document ID : {document.document_id}")
print(f"File name   : {document.file_name}")
print(f"File type   : {document.file_type}")
print(f"Source      : {document.source or 'Not specified'}")
print(f"Version     : {document.version or 'Not specified'}")
print(f"Characters  : {len(document.content)}")
print("-" * 50)
print("Content preview:")
print(document.content[:300])