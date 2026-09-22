from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database.connection import get_connection
from app.database.schema import SCHEMA_SQL


def initialize_database():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(SCHEMA_SQL)

        connection.commit()


if __name__ == "__main__":
    initialize_database()
    print("Database schema initialized successfully!")