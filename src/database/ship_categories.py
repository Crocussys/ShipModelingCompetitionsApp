from .connection import get_connection


def get_ship_categories(search: str = ""):
    search = search.strip().casefold()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                id,
                name,
                protocol_1,
                protocol_2,
                protocol_3
            FROM ship_categories
            ORDER BY name
        """).fetchall()

    if not search:
        return rows

    return [
        row for row in rows
        if search in row[1].casefold()
    ]


def create_ship_category(
    name: str,
    protocol_1: bool = False,
    protocol_2: bool = False,
    protocol_3: bool = False,
) -> int:
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO ship_categories (
                name,
                protocol_1,
                protocol_2,
                protocol_3
            )
            VALUES (?, ?, ?, ?)
        """, (
            name.strip(),
            int(protocol_1),
            int(protocol_2),
            int(protocol_3),
        ))

        return cursor.lastrowid


def update_ship_category(
    category_id: int,
    name: str,
    protocol_1: bool,
    protocol_2: bool,
    protocol_3: bool,
):
    with get_connection() as conn:
        conn.execute("""
            UPDATE ship_categories
            SET name = ?,
                protocol_1 = ?,
                protocol_2 = ?,
                protocol_3 = ?
            WHERE id = ?
        """, (
            name.strip(),
            int(protocol_1),
            int(protocol_2),
            int(protocol_3),
            category_id,
        ))


def delete_ship_category(category_id: int):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM ship_categories
            WHERE id = ?
        """, (category_id,))


def get_protocol_1_categories():
    with get_connection() as conn:
        return conn.execute("""
            SELECT id, name
            FROM ship_categories
            WHERE protocol_1 = 1
            ORDER BY name
        """).fetchall()


def get_protocol_1_or_2_categories():
    with get_connection() as conn:
        return conn.execute("""
            SELECT id, name
            FROM ship_categories
            WHERE protocol_1 = 1 OR protocol_2 = 1
            ORDER BY name
        """).fetchall()


def get_protocol_3_categories():
    with get_connection() as conn:
        return conn.execute("""
            SELECT id, name
            FROM ship_categories
            WHERE protocol_3 = 1
            ORDER BY name
        """).fetchall()
