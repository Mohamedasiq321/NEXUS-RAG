from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Document:
    document_id: str
    file_name: str
    file_type: str
    content: str

    source: str = ""
    version: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(default_factory=datetime.utcnow)