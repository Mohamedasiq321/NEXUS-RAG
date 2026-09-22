import psycopg

from app.database.config import DATABASE_CONFIG


def get_connection():
    return psycopg.connect(**DATABASE_CONFIG)