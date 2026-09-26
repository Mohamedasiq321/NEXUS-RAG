from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.ingestion.service import DocumentIngestionService


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)

ingestion_service = DocumentIngestionService()

SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx", ".csv"}


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A file must be provided.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Supported file types: .txt, .pdf, .docx, .csv",
        )

    try:
        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        with NamedTemporaryFile(
            suffix=extension,
            delete=False,
        ) as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name

        try:
            result = ingestion_service.ingest(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)

        # Preserve the original uploaded filename
        result["file_name"] = file.filename

        if result.get("duplicate"):
            message = "Document already indexed."
        else:
            message = "Document indexed successfully."

        return {
            "message": message,
            "document": result,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document ingestion failed: {str(exc)}",
        ) from exc