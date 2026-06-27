from .connection import get_connection


def get_ships(search: str = "", category_id: int | None = None):
    search = search.strip().casefold()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                s.id,
                s.name,
                s.model,
                s.category_id,
                sc.name AS category_name,
                s.scale
            FROM ships s
            JOIN ship_categories sc ON sc.id = s.category_id
            ORDER BY s.name, s.model
        """).fetchall()

    if search:
        rows = [
            row for row in rows
            if search in row[1].casefold()
            or search in row[2].casefold()
        ]

    if category_id is not None:
        rows = [
            row for row in rows
            if row[3] == category_id
        ]

    return rows


def create_ship(name: str, model: str, category_id: int, scale: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO ships (name, model, category_id, scale)
            VALUES (?, ?, ?, ?)
        """, (
            name.strip(),
            model.strip(),
            category_id,
            scale.strip(),
        ))

        return cursor.lastrowid


def update_ship(ship_id: int, name: str, model: str, category_id: int, scale: str):
    with get_connection() as conn:
        conn.execute("""
            UPDATE ships
            SET name = ?,
                model = ?,
                category_id = ?,
                scale = ?
            WHERE id = ?
        """, (
            name.strip(),
            model.strip(),
            category_id,
            scale.strip(),
            ship_id,
        ))


def delete_ship(ship_id: int):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM ships
            WHERE id = ?
        """, (ship_id,))


def is_ship_registered(ship_id: int, competition_id: int) -> bool:
    with get_connection() as conn:
        row = conn.execute("""
            SELECT 1
            FROM competition_team_participant_ships ctps
            JOIN competition_team_participants ctp
                ON ctp.id = ctps.competition_team_participant_id
            JOIN competition_teams ct
                ON ct.id = ctp.competition_team_id
            WHERE ctps.ship_id = ?
              AND ct.competition_id = ?
        """, (ship_id, competition_id)).fetchone()

        return row is not None


def get_registered_ships(
    competition_id: int,
    search: str = "",
    category_id: int | None = None,
):
    search = search.strip().casefold()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                ctps.id AS registration_id,
                s.id AS ship_id,
                p.full_name,
                s.name,
                s.model,
                s.category_id,
                sc.name AS category_name,
                s.scale,
                ctps.channel
            FROM competition_team_participant_ships ctps
            JOIN ships s ON s.id = ctps.ship_id
            JOIN ship_categories sc ON sc.id = s.category_id
            JOIN competition_team_participants ctp
                ON ctp.id = ctps.competition_team_participant_id
            JOIN participants p ON p.id = ctp.participant_id
            JOIN competition_teams ct ON ct.id = ctp.competition_team_id
            WHERE ct.competition_id = ?
            ORDER BY p.full_name, s.name, s.model
        """, (competition_id,)).fetchall()

    if search:
        rows = [
            row for row in rows
            if search in row[2].casefold()
            or search in row[3].casefold()
            or search in row[4].casefold()
        ]

    if category_id is not None:
        rows = [
            row for row in rows
            if row[5] == category_id
        ]

    return rows


def register_ship(
    ship_id: int,
    competition_team_participant_id: int,
    channel: str,
) -> int:
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO competition_team_participant_ships (
                ship_id,
                competition_team_participant_id,
                channel
            )
            VALUES (?, ?, ?)
        """, (
            ship_id,
            competition_team_participant_id,
            channel.strip(),
        ))

        return cursor.lastrowid


def remove_ship_registration(registration_id: int):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM competition_team_participant_ships
            WHERE id = ?
        """, (registration_id,))
