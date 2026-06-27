import sqlite3

from config import get_database_path


def get_connection():
    conn = sqlite3.connect(get_database_path())
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
