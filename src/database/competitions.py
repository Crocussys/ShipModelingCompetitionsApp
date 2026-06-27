from .connection import get_connection


def get_competitions() -> list[tuple[int, str]]:
    with get_connection() as conn:
        return conn.execute("""
            SELECT id, name
            FROM competitions
            ORDER BY id DESC
        """).fetchall()


def create_competition(name: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO competitions (name)
            VALUES (?)
        """, (name,))

        return cursor.lastrowid
