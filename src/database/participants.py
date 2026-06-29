from .connection import get_connection


def get_participants(search: str = ""):
    search = search.strip().casefold()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, full_name, birth_date
            FROM participants
            ORDER BY full_name
        """).fetchall()

    if not search:
        return rows

    return [
        row for row in rows
        if search in row[1].casefold()
    ]


def get_competition_participants(
    competition_id: int,
    search: str = "",
    group_id: int | None = None,
    competition_team_id: int | None = None,
):
    search = search.strip().casefold()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                ctp.id,
                p.id AS participant_id,
                p.full_name,
                p.birth_date,
                g.name AS group_name,
                t.short_name AS team_short_name,
                ctp.group_id,
                ctp.competition_team_id
            FROM competition_team_participants ctp
            JOIN participants p ON p.id = ctp.participant_id
            JOIN groups g ON g.id = ctp.group_id
            JOIN competition_teams ct ON ct.id = ctp.competition_team_id
            JOIN teams t ON t.id = ct.team_id
            WHERE ct.competition_id = ?
            ORDER BY p.full_name
        """, (competition_id,)).fetchall()

    if search:
        rows = [
            row for row in rows
            if search in row[2].casefold()
        ]

    if group_id is not None:
        rows = [
            row for row in rows
            if row[6] == group_id
        ]

    if competition_team_id is not None:
        rows = [
            row for row in rows
            if row[7] == competition_team_id
        ]

    return rows


def create_participant(full_name: str, birth_date: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO participants (full_name, birth_date)
            VALUES (?, ?)
        """, (full_name.strip(), birth_date.strip()))

        return cursor.lastrowid


def update_participant(participant_id: int, full_name: str, birth_date: str):
    with get_connection() as conn:
        conn.execute("""
            UPDATE participants
            SET full_name = ?,
                birth_date = ?
            WHERE id = ?
        """, (full_name.strip(), birth_date.strip(), participant_id))


def delete_participant(participant_id: int):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM participants
            WHERE id = ?
        """, (participant_id,))


def is_participant_registered(participant_id: int, competition_id: int) -> bool:
    with get_connection() as conn:
        row = conn.execute("""
            SELECT 1
            FROM competition_team_participants ctp
            JOIN competition_teams ct ON ct.id = ctp.competition_team_id
            WHERE ctp.participant_id = ?
              AND ct.competition_id = ?
        """, (participant_id, competition_id)).fetchone()

        return row is not None


def register_participant(
    participant_id: int,
    competition_team_id: int,
    group_id: int,
) -> int:
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO competition_team_participants (
                participant_id,
                competition_team_id,
                group_id
            )
            VALUES (?, ?, ?)
        """, (participant_id, competition_team_id, group_id))

        return cursor.lastrowid


def remove_participant_registration(registration_id: int):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM competition_team_participants
            WHERE id = ?
        """, (registration_id,))

def get_registered_participants_for_combo(competition_id: int):
    with get_connection() as conn:
        return conn.execute("""
            SELECT
                ctp.id,
                p.full_name || ' — ' || t.short_name
            FROM competition_team_participants ctp
            JOIN participants p ON p.id = ctp.participant_id
            JOIN competition_teams ct ON ct.id = ctp.competition_team_id
            JOIN teams t ON t.id = ct.team_id
            WHERE ct.competition_id = ?
            ORDER BY p.full_name
        """, (competition_id,)).fetchall()


def get_registered_participants_for_combo(
    competition_id: int,
    competition_team_id: int | None = None,
    group_id: int | None = None,
):
    with get_connection() as conn:
        query = """
            SELECT
                ctp.id,
                p.full_name
            FROM competition_team_participants ctp
            JOIN participants p ON p.id = ctp.participant_id
            JOIN competition_teams ct ON ct.id = ctp.competition_team_id
            WHERE ct.competition_id = ?
        """

        params = [competition_id]

        if competition_team_id is not None:
            query += " AND ctp.competition_team_id = ?"
            params.append(competition_team_id)

        if group_id is not None:
            query += " AND ctp.group_id = ?"
            params.append(group_id)

        query += " ORDER BY p.full_name"

        return conn.execute(query, params).fetchall()
