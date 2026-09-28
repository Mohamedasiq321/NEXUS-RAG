import re
from uuid import uuid4

from app.models.chunk import DocumentChunk
from app.models.document import Document


def split_into_sections(content: str) -> list[tuple[str, str]]:
    pattern = r"(?m)^(?P<header>\d+\.\s+.+)$"

    matches = list(re.finditer(pattern, content))

    if not matches:
        return [("General", content.strip())]

    sections = []

    preamble = content[:matches[0].start()].strip()

    if preamble:
        sections.append(("Document Information", preamble))

    for index, match in enumerate(matches):
        header = match.group("header").strip()

        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)

        section_content = content[start:end].strip()
        section_content = re.sub(
            r"(?mi)^Source:\s*.+$",
            "",
            section_content,
        ).strip()

        sections.append(
            (
                header,
                section_content,
            )
        )

    return sections


def create_chunks(document: Document) -> list[DocumentChunk]:
    if document.file_type == "csv":
        return create_csv_chunks(document)

    sections = split_into_sections(document.content)

    chunks = []

    for index, (section, content) in enumerate(sections):
        if not content:
            continue

        chunk = DocumentChunk(
            chunk_id=str(uuid4()),
            document_id=document.document_id,
            content=content,
            chunk_index=index,
            section=section,
            metadata={
                "file_name": document.file_name,
                "file_type": document.file_type,
                "source": document.source,
                "version": document.version,
                **document.metadata,
            },
        )

        chunks.append(chunk)

    return chunks
    sections = split_into_sections(document.content)

    chunks = []

    for index, (section, content) in enumerate(sections):
        if not content:
            continue

        chunk = DocumentChunk(
            chunk_id=str(uuid4()),
            document_id=document.document_id,
            content=content,
            chunk_index=index,
            section=section,
            metadata={
                "file_name": document.file_name,
                "file_type": document.file_type,
                "source": document.source,
                "version": document.version,
                **document.metadata,
            },
        )

        chunks.append(chunk)

    return chunks

def create_csv_chunks(document: Document) -> list[DocumentChunk]:
    chunks = []

    rows = [
        line.strip()
        for line in document.content.splitlines()
        if line.strip()
    ]

    for index, row_content in enumerate(rows):
        row_number = index + 2

        row_metadata = {
            "file_name": document.file_name,
            "file_type": document.file_type,
            "source": document.source,
            "version": document.version,
            "row_number": row_number,
            **document.metadata,
        }

        # Extract structured fields from the row text.
        # Example:
        # "Row 2: id: EMP001; department: Engineering; ..."
        field_text = row_content.split(":", 1)[1].strip()

        for field in field_text.split(";"):
            if ":" not in field:
                continue

            key, value = field.split(":", 1)

            key = key.strip()
            value = value.strip()

            if key and value:
                row_metadata[key] = value

        chunk = DocumentChunk(
            chunk_id=str(uuid4()),
            document_id=document.document_id,
            content=row_content,
            chunk_index=index,
            section=f"Row {row_number}",
            metadata=row_metadata,
        )

        chunks.append(chunk)

    return chunks