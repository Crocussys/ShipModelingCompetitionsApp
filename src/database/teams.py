from .connection import get_connection


def get_teams(search: str = ""):
    search = search.strip().casefold()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT 
                t.id,
                t.short_name,
                t.organization,
                t.district_id,
                d.name AS district_name
            FROM teams t
            JOIN districts d ON d.id = t.district_id
            ORDER BY t.short_name
        """).fetchall()

    if not search:
        return rows

    return [
        row for row in rows
        if search in row[1].casefold()
    ]


def get_teams_for_competition(competition_id: int, search: str = ""):
    search = search.strip().casefold()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                t.id,
                t.short_name,
                t.organization,
                d.name AS district_name,
                ct.coach
            FROM competition_teams ct
            JOIN teams t ON t.id = ct.team_id
            JOIN districts d ON d.id = t.district_id
            WHERE ct.competition_id = ?
            ORDER BY t.short_name
        """, (competition_id,)).fetchall()

    if not search:
        return rows

    return [
        row for row in rows
        if search in row[1].casefold()
    ]


def create_team(short_name: str, organization: str, district_id: int) -> int:
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO teams (short_name, organization, district_id)
            VALUES (?, ?, ?)
        """, (short_name.strip(), organization.strip(), district_id))

        return cursor.lastrowid


def update_team(team_id: int, short_name: str, organization: str, district_id: int):
    with get_connection() as conn:
        conn.execute("""
            UPDATE teams
            SET short_name = ?,
                organization = ?,
                district_id = ?
            WHERE id = ?
        """, (short_name.strip(), organization.strip(), district_id, team_id))


def delete_team(team_id: int):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM teams
            WHERE id = ?
        """, (team_id,))


def assign_team_to_competition(team_id: int, competition_id: int, coach: str = ""):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO competition_teams (team_id, competition_id, coach)
            VALUES (?, ?, ?)
            ON CONFLICT(team_id, competition_id)
            DO UPDATE SET coach = excluded.coach
        """, (team_id, competition_id, coach.strip()))


def remove_team_from_competition(team_id: int, competition_id: int):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM competition_teams
            WHERE team_id = ?
              AND competition_id = ?
        """, (team_id, competition_id))


def is_team_assigned(team_id: int, competition_id: int) -> bool:
    with get_connection() as conn:
        row = conn.execute("""
            SELECT 1
            FROM competition_teams
            WHERE team_id = ?
              AND competition_id = ?
        """, (team_id, competition_id)).fetchone()

        return row is not None
    
def get_registered_competition_teams(competition_id: int):
    with get_connection() as conn:
        return conn.execute("""
            SELECT
                ct.id,
                t.short_name
            FROM competition_teams ct
            JOIN teams t ON t.id = ct.team_id
            WHERE ct.competition_id = ?
            ORDER BY t.short_name
        """, (competition_id,)).fetchall()
