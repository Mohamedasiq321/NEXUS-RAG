import hashlib
import re
from pathlib import Path
from uuid import uuid4

from pypdf import PdfReader

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


def load_pdf(file_path: str) -> Document:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if path.suffix.lower() != ".pdf":
        raise ValueError("Expected a .pdf file")

    reader = PdfReader(str(path))

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):
        text = page.extract_text() or ""

        if text.strip():
            pages.append(
                f"Page {page_number}\n{text.strip()}"
            )

    content = "\n\n".join(pages).strip()

    if not content:
        raise ValueError(
            "No extractable text found in the PDF."
        )

    content_hash = hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()

    extracted_metadata = extract_metadata(
        content
    )

    extracted_metadata["page_count"] = len(
        reader.pages
    )

    return Document(
        document_id=str(uuid4()),
        file_name=path.name,
        file_type="pdf",
        content=content,
        source=extracted_metadata.get(
            "source",
            "",
        ),
        version=extracted_metadata.get(
            "version",
            "",
        ),
        content_hash=content_hash,
        metadata={
            **extracted_metadata,
            "file_size_bytes": path.stat().st_size,
            "file_path": str(path),
        },
    )