from .connection import get_connection
from .judges import JUDGE_ROLE_STAND_MAIN, JUDGE_ROLE_STAND_JUDGE


STAND_PROTOCOL_NOT_PRINTED = 0
STAND_PROTOCOL_GIVEN = 1
STAND_PROTOCOL_ACCEPTED = 2

STAND_PROTOCOL_STATUSES = {
    STAND_PROTOCOL_NOT_PRINTED: "Не распечатан",
    STAND_PROTOCOL_GIVEN: "Отдан",
    STAND_PROTOCOL_ACCEPTED: "Принят",
}


def get_stand_protocol_status_name(status: int) -> str:
    return STAND_PROTOCOL_STATUSES.get(status, "Неизвестно")


def update_stand_protocol_status(protocol_id: int, status: int):
    with get_connection() as conn:
        conn.execute("""
            UPDATE stand_protocols
            SET status = ?
            WHERE id = ?
        """, (status, protocol_id))


def generate_stand_protocols_for_competition(competition_id: int):
    with get_connection() as conn:
        stand_judges = conn.execute("""
            SELECT id
            FROM competition_judges
            WHERE competition_id = ?
              AND role IN (?, ?)
        """, (
            competition_id,
            JUDGE_ROLE_STAND_MAIN,
            JUDGE_ROLE_STAND_JUDGE,
        )).fetchall()

        category_group_pairs = conn.execute("""
            SELECT DISTINCT
                s.category_id,
                ctp.group_id
            FROM competition_team_participant_ships ctps
            JOIN ships s ON s.id = ctps.ship_id
            JOIN competition_team_participants ctp
                ON ctp.id = ctps.competition_team_participant_id
            JOIN competition_teams ct
                ON ct.id = ctp.competition_team_id
            WHERE ct.competition_id = ?
        """, (competition_id,)).fetchall()

        for (competition_judge_id,) in stand_judges:
            for category_id, group_id in category_group_pairs:
                conn.execute("""
                    INSERT OR IGNORE INTO stand_protocols (
                        competition_judge_id,
                        category_id,
                        group_id,
                        status
                    )
                    VALUES (?, ?, ?, 0)
                """, (
                    competition_judge_id,
                    category_id,
                    group_id,
                ))


def get_stand_protocols(
    competition_id: int,
    search: str = "",
    category_id: int | None = None,
    group_id: int | None = None,
):
    search = search.strip().casefold()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                sp.id,
                j.full_name,
                sc.name AS category_name,
                g.name AS group_name,
                sp.status,
                sp.category_id,
                sp.group_id
            FROM stand_protocols sp
            JOIN competition_judges cj ON cj.id = sp.competition_judge_id
            JOIN judges j ON j.id = cj.judge_id
            JOIN ship_categories sc ON sc.id = sp.category_id
            JOIN groups g ON g.id = sp.group_id
            WHERE cj.competition_id = ?
            ORDER BY sc.name, g.name, j.full_name
        """, (competition_id,)).fetchall()

    if search:
        rows = [
            row for row in rows
            if search in row[1].casefold()
            or stand_protocol_has_participant(row[0], search)
        ]

    if category_id is not None:
        rows = [row for row in rows if row[5] == category_id]

    if group_id is not None:
        rows = [row for row in rows if row[6] == group_id]

    return rows


def stand_protocol_has_participant(protocol_id: int, search: str) -> bool:
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT p.full_name
            FROM stand_protocols sp
            JOIN competition_judges cj ON cj.id = sp.competition_judge_id
            JOIN competition_team_participant_ships ctps
            JOIN ships s ON s.id = ctps.ship_id
            JOIN competition_team_participants ctp
                ON ctp.id = ctps.competition_team_participant_id
            JOIN participants p ON p.id = ctp.participant_id
            JOIN competition_teams ct ON ct.id = ctp.competition_team_id
            WHERE sp.id = ?
              AND ct.competition_id = cj.competition_id
              AND s.category_id = sp.category_id
              AND ctp.group_id = sp.group_id
        """, (protocol_id,)).fetchall()

    return any(search in full_name.casefold() for (full_name,) in rows)


def get_stand_protocol(protocol_id: int):
    with get_connection() as conn:
        return conn.execute("""
            SELECT
                sp.id,
                j.full_name AS judge_full_name,
                sc.name AS category_name,
                g.name AS group_name,
                cj.competition_id
            FROM stand_protocols sp
            JOIN competition_judges cj ON cj.id = sp.competition_judge_id
            JOIN judges j ON j.id = cj.judge_id
            JOIN ship_categories sc ON sc.id = sp.category_id
            JOIN groups g ON g.id = sp.group_id
            WHERE sp.id = ?
        """, (protocol_id,)).fetchone()


def get_main_stand_judge_full_name(competition_id: int) -> str:
    with get_connection() as conn:
        row = conn.execute("""
            SELECT j.full_name
            FROM competition_judges cj
            JOIN judges j ON j.id = cj.judge_id
            WHERE cj.competition_id = ?
              AND cj.role = 2
            ORDER BY j.full_name
            LIMIT 1
        """, (competition_id,)).fetchone()

    return row[0] if row else ""


def get_stand_protocol_ships(protocol_id: int):
    with get_connection() as conn:
        return conn.execute("""
            SELECT
                ctps.id,
                p.full_name,
                t.id AS team_id,
                s.scale,
                sr.execution_score,
                sr.impression_score,
                sr.work_volume_score,
                sr.compliance_score
            FROM stand_protocols sp
            JOIN competition_judges cj ON cj.id = sp.competition_judge_id
            JOIN competition_team_participant_ships ctps
            JOIN ships s ON s.id = ctps.ship_id
            JOIN competition_team_participants ctp
                ON ctp.id = ctps.competition_team_participant_id
            JOIN participants p ON p.id = ctp.participant_id
            JOIN competition_teams ct ON ct.id = ctp.competition_team_id
            JOIN teams t ON t.id = ct.team_id
            LEFT JOIN stand_results sr
                ON sr.stand_protocol_id = sp.id
            AND sr.competition_team_participant_ship_id = ctps.id
            WHERE sp.id = ?
            AND ct.competition_id = cj.competition_id
            AND s.category_id = sp.category_id
            AND ctp.group_id = sp.group_id
            ORDER BY p.full_name
        """, (protocol_id,)).fetchall()


def save_stand_result(
    stand_protocol_id: int,
    registered_ship_id: int,
    execution_score: int,
    impression_score: int,
    work_volume_score: int,
    compliance_score: int,
):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO stand_results (
                stand_protocol_id,
                competition_team_participant_ship_id,
                execution_score,
                impression_score,
                work_volume_score,
                compliance_score
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (
                stand_protocol_id,
                competition_team_participant_ship_id
            )
            DO UPDATE SET
                execution_score = excluded.execution_score,
                impression_score = excluded.impression_score,
                work_volume_score = excluded.work_volume_score,
                compliance_score = excluded.compliance_score
        """, (
            stand_protocol_id,
            registered_ship_id,
            execution_score,
            impression_score,
            work_volume_score,
            compliance_score,
        ))
