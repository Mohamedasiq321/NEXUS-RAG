import hashlib
import json
from pathlib import Path
from uuid import uuid4

import pandas as pd

from app.models.document import Document


def load_csv(file_path: str) -> Document:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if path.suffix.lower() != ".csv":
        raise ValueError("Expected a .csv file")

    dataframe = pd.read_csv(path)

    if dataframe.empty:
        raise ValueError(
            "The CSV file contains no data rows."
        )

    if len(dataframe.columns) == 0:
        raise ValueError(
            "The CSV file contains no columns."
        )

    # Normalize column names
    dataframe.columns = [
        str(column).strip()
        for column in dataframe.columns
    ]

    rows = []

    for row_number, row in dataframe.iterrows():
        row_data = {}

        for column in dataframe.columns:
            value = row[column]

            if pd.isna(value):
                value = ""

            row_data[column] = str(value).strip()

        rows.append(
            {
                "row_number": int(row_number) + 2,
                "data": row_data,
            }
        )

    # Create deterministic textual content from rows.
    # Each row becomes a separate evidence unit.
    row_texts = []

    for row in rows:
        fields = [
            f"{column}: {value}"
            for column, value in row["data"].items()
            if value
        ]

        row_text = (
            f"Row {row['row_number']}: "
            + "; ".join(fields)
        )

        row_texts.append(row_text)

    content = "\n".join(row_texts).strip()

    if not content:
        raise ValueError(
            "No usable data could be extracted from the CSV."
        )

    content_hash = hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()

    metadata = {
        "row_count": len(dataframe),
        "column_count": len(dataframe.columns),
        "columns": list(dataframe.columns),
        "file_size_bytes": path.stat().st_size,
        "file_path": str(path),
        "structured_data": True,
        "row_level_evidence": True,
    }

    return Document(
        document_id=str(uuid4()),
        file_name=path.name,
        file_type="csv",
        content=content,
        source=path.name,
        version="",
        content_hash=content_hash,
        metadata=metadata,
    )