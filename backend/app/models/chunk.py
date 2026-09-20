from dataclasses import dataclass, field
from typing import Any


@dataclass
class DocumentChunk:
    chunk_id: str
    document_id: str
    content: str

    chunk_index: int
    section: str = ""

    metadata: dict[str, Any] = field(default_factory=dict)