import os


DATABASE_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5433")),
    "dbname": os.getenv("POSTGRES_DB", "nexus_rag"),
    "user": os.getenv("POSTGRES_USER", "nexus"),
    "password": os.getenv(
        "POSTGRES_PASSWORD",
        "nexus_dev_password",
    ),
}