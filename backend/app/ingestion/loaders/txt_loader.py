import hashlib
import re
from pathlib import Path
from uuid import uuid4

from app.models.document import Document


def extract_metadata(content: str) -> dict[str, str]:
    metadata = {}

    version_match = re.search(
        r"^Version:\s*(.+)$",
        content,
        re.MULTILINE | re.IGNORECASE,
    )

    source_match = re.search(
        r"^Source:\s*(.+)$",
        content,
        re.MULTILINE | re.IGNORECASE,
    )

    policy_id_match = re.search(
        r"^Policy ID:\s*(.+)$",
        content,
        re.MULTILINE | re.IGNORECASE,
    )

    effective_date_match = re.search(
        r"^Effective Date:\s*(.+)$",
        content,
        re.MULTILINE | re.IGNORECASE,
    )

    department_match = re.search(
        r"^Department:\s*(.+)$",
        content,
        re.MULTILINE | re.IGNORECASE,
    )

    if version_match:
        metadata["version"] = version_match.group(1).strip()

    if source_match:
        metadata["source"] = source_match.group(1).strip()

    if policy_id_match:
        metadata["policy_id"] = policy_id_match.group(1).strip()

    if effective_date_match:
        metadata["effective_date"] = effective_date_match.group(1).strip()

    if department_match:
        metadata["department"] = department_match.group(1).strip()

    return metadata


def load_txt(file_path: str) -> Document:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() != ".txt":
        raise ValueError("Expected a .txt file")

    content = path.read_text(encoding="utf-8")
    content_hash = hashlib.sha256(
    content.encode("utf-8")
).hexdigest()

    extracted_metadata = extract_metadata(content)

    return Document(
        document_id=str(uuid4()),
        file_name=path.name,
        file_type="txt",
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