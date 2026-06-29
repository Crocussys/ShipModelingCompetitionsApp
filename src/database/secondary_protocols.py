from .connection import get_connection
from .judges import JUDGE_ROLE_MAIN, JUDGE_ROLE_SECRETARY


def get_secondary_protocol_rows(
    competition_id: int,
    protocol_number: int,
    search: str = "",
    category_id: int | None = None,
    group_id: int | None = None,
):
    search = search.strip().casefold()
    protocol_column = f"protocol_{protocol_number}"

    with get_connection() as conn:
        rows = conn.execute(f"""
            SELECT DISTINCT
                s.category_id,
                sc.name,
                ctp.group_id,
                g.name
            FROM competition_team_participant_ships ctps
            JOIN ships s ON s.id = ctps.ship_id
            JOIN ship_categories sc ON sc.id = s.category_id
            JOIN competition_team_participants ctp
                ON ctp.id = ctps.competition_team_participant_id
            JOIN participants p ON p.id = ctp.participant_id
            JOIN groups g ON g.id = ctp.group_id
            JOIN competition_teams ct ON ct.id = ctp.competition_team_id
            WHERE ct.competition_id = ?
              AND sc.{protocol_column} = 1
            ORDER BY sc.name, g.name
        """, (competition_id,)).fetchall()

    if category_id is not None:
        rows = [row for row in rows if row[0] == category_id]

    if group_id is not None:
        rows = [row for row in rows if row[2] == group_id]

    if search:
        rows = [
            row for row in rows
            if secondary_protocol_has_participant(
                competition_id,
                row[0],
                row[2],
                search,
            )
        ]

    return rows


def secondary_protocol_has_participant(
    competition_id: int,
    category_id: int,
    group_id: int,
    search: str,
) -> bool:
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT p.full_name
            FROM competition_team_participant_ships ctps
            JOIN ships s ON s.id = ctps.ship_id
            JOIN competition_team_participants ctp
                ON ctp.id = ctps.competition_team_participant_id
            JOIN participants p ON p.id = ctp.participant_id
            JOIN competition_teams ct ON ct.id = ctp.competition_team_id
            WHERE ct.competition_id = ?
              AND s.category_id = ?
              AND ctp.group_id = ?
        """, (competition_id, category_id, group_id)).fetchall()

    return any(search in full_name.casefold() for (full_name,) in rows)


def get_secondary_protocol_header_data(
    competition_id: int,
    category_id: int,
    group_id: int,
):
    with get_connection() as conn:
        category = None

        if category_id is not None:
            category = conn.execute("""
                SELECT name FROM ship_categories
                WHERE id = ?
            """, (category_id,)).fetchone()

        group = conn.execute("""
            SELECT name FROM groups
            WHERE id = ?
        """, (group_id,)).fetchone()

        main_judge = conn.execute("""
            SELECT j.short_name
            FROM competition_judges cj
            JOIN judges j ON j.id = cj.judge_id
            WHERE cj.competition_id = ?
              AND cj.role = ?
            ORDER BY j.full_name
            LIMIT 1
        """, (competition_id, JUDGE_ROLE_MAIN)).fetchone()

        secretary = conn.execute("""
            SELECT j.short_name
            FROM competition_judges cj
            JOIN judges j ON j.id = cj.judge_id
            WHERE cj.competition_id = ?
              AND cj.role = ?
            ORDER BY j.full_name
            LIMIT 1
        """, (competition_id, JUDGE_ROLE_SECRETARY)).fetchone()

    return {
        "category_name": category[0] if category else "",
        "group_name": group[0] if group else "",
        "main_judge_short_name": main_judge[0] if main_judge else "",
        "secretary_short_name": secretary[0] if secretary else "",
    }
