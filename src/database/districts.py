from .connection import get_connection


def get_districts(search: str = ""):
    search = search.strip().casefold()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, name
            FROM districts
            ORDER BY name
        """).fetchall()

    if not search:
        return rows

    return [
        row for row in rows
        if search in row[1].casefold()
    ]


def create_district(name: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO districts (name)
            VALUES (?)
        """, (name.strip(),))

        return cursor.lastrowid


def update_district(city_id: int, name: str):
    with get_connection() as conn:
        conn.execute("""
            UPDATE districts
            SET name = ?
            WHERE id = ?
        """, (name.strip(), city_id))


def delete_district(city_id: int):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM districts
            WHERE id = ?
        """, (city_id,))
        