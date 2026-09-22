from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database.connection import get_connection


with get_connection() as connection:
    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM documents WHERE file_name = %s",
            ("remote_work_policy.txt",),
        )

    connection.commit()

print("Sample test documents removed successfully.")