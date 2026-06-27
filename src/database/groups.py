from .connection import get_connection


def get_groups(search: str = ""):
    search = search.strip().casefold()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, name
            FROM groups
            ORDER BY name
        """).fetchall()

    if not search:
        return rows

    return [
        row for row in rows
        if search in row[1].casefold()
    ]


def create_group(name: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO groups (name)
            VALUES (?)
        """, (name.strip(),))

        return cursor.lastrowid


def update_group(group_id: int, name: str):
    with get_connection() as conn:
        conn.execute("""
            UPDATE groups
            SET name = ?
            WHERE id = ?
        """, (name.strip(), group_id))


def delete_group(group_id: int):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM groups
            WHERE id = ?
        """, (group_id,))
