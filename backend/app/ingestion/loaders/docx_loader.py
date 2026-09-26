import hashlib
import re
from pathlib import Path
from uuid import uuid4

from docx import Document as DocxDocument

from app.models.document import Document


def extract_metadata(content: str) -> dict[str, str]:
    metadata = {}

    patterns = {
        "version": r"^Version:\s*(.+)$",
        "source": r"^Source:\s*(.+)$",
        "policy_id": r"^Policy ID:\s*(.+)$",
        "effective_date": r"^Effective Date:\s*(.+)$",
        "department": r"^Department:\s*(.+)$",
    }

    for key, pattern in patterns.items():
        match = re.search(
            pattern,
            content,
            re.MULTILINE | re.IGNORECASE,
        )

        if match:
            metadata[key] = match.group(1).strip()

    return metadata


def load_docx(file_path: str) -> Document:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if path.suffix.lower() != ".docx":
        raise ValueError("Expected a .docx file")

    doc = DocxDocument(str(path))

    paragraphs = []

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    content = "\n".join(paragraphs).strip()

    if not content:
        raise ValueError(
            "No extractable text found in the DOCX file."
        )

    content_hash = hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()

    extracted_metadata = extract_metadata(content)

    extracted_metadata["paragraph_count"] = len(paragraphs)

    return Document(
        document_id=str(uuid4()),
        file_name=path.name,
        file_type="docx",
        content=content,
        source=extracted_metadata.get("source", ""),
        version=extracted_metadata.get("version", ""),
        content_hash=content_hash,
        metadata={
            **extracted_metadata,
            "file_size_bytes": path.stat().st_size,
            "file_path": str(path),
        },
    )