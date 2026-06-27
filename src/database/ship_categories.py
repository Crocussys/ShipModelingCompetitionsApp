from .connection import get_connection


def get_ship_categories(search: str = ""):
    search = search.strip().casefold()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, name
            FROM ship_categories
            ORDER BY name
        """).fetchall()

    if not search:
        return rows

    return [
        row for row in rows
        if search in row[1].casefold()
    ]

def create_ship_category(name: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO ship_categories (name)
            VALUES (?)
        """, (name.strip(),))

        return cursor.lastrowid


def update_ship_category(category_id: int, name: str):
    with get_connection() as conn:
        conn.execute("""
            UPDATE ship_categories
            SET name = ?
            WHERE id = ?
        """, (name.strip(), category_id))


def delete_ship_category(category_id: int):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM ship_categories
            WHERE id = ?
        """, (category_id,))
