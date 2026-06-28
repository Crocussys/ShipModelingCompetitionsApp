from .connection import get_connection
from .judges import JUDGE_ROLE_MAIN, JUDGE_ROLE_JUDGE


START_PROTOCOL_NOT_PRINTED = 0
START_PROTOCOL_GIVEN = 1
START_PROTOCOL_ACCEPTED = 2

START_PROTOCOL_STATUSES = {
    START_PROTOCOL_NOT_PRINTED: "Не распечатан",
    START_PROTOCOL_GIVEN: "Отдан",
    START_PROTOCOL_ACCEPTED: "Принят",
}


START_SCORE_MAXIMUMS = {
    "forward_gate_1": 6,
    "forward_gate_2": 9,
    "forward_gate_3": 6,
    "forward_gate_4": 6,
    "forward_gate_5": 9,
    "forward_gate_6": 6,
    "forward_gate_7": 6,
    "forward_gate_8": 9,
    "forward_gate_9": 6,
    "forward_gate_10": 6,
    "forward_gate_11": 9,
    "reverse": 12,
    "mooring": 10,
}


def get_start_protocol_status_name(status: int) -> str:
    return START_PROTOCOL_STATUSES.get(status, "Неизвестно")


def generate_start_protocols_for_competition(competition_id: int):
    with get_connection() as conn:
        start_judges = conn.execute("""
            SELECT id
            FROM competition_judges
            WHERE competition_id = ?
              AND role IN (?, ?)
        """, (
            competition_id,
            JUDGE_ROLE_MAIN,
            JUDGE_ROLE_JUDGE,
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

        for (competition_judge_id,) in start_judges:
            for category_id, group_id in category_group_pairs:
                conn.execute("""
                    INSERT OR IGNORE INTO start_protocols (
                        competition_judge_id,
                        category_id,
                        group_id,
                        status
                    )
                    VALUES (?, ?, ?, ?)
                """, (
                    competition_judge_id,
                    category_id,
                    group_id,
                    START_PROTOCOL_NOT_PRINTED,
                ))


def get_start_protocols(
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
            FROM start_protocols sp
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
            or start_protocol_has_participant(row[0], search)
        ]

    if category_id is not None:
        rows = [
            row for row in rows
            if row[5] == category_id
        ]

    if group_id is not None:
        rows = [
            row for row in rows
            if row[6] == group_id
        ]

    return rows


def start_protocol_has_participant(protocol_id: int, search: str) -> bool:
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT p.full_name
            FROM start_protocols sp
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


def update_start_protocol_status(protocol_id: int, status: int):
    with get_connection() as conn:
        conn.execute("""
            UPDATE start_protocols
            SET status = ?
            WHERE id = ?
        """, (status, protocol_id))


def get_start_protocol(protocol_id: int):
    with get_connection() as conn:
        return conn.execute("""
            SELECT
                sp.id,
                j.full_name AS judge_full_name,
                sc.name AS category_name,
                g.name AS group_name,
                cj.competition_id
            FROM start_protocols sp
            JOIN competition_judges cj ON cj.id = sp.competition_judge_id
            JOIN judges j ON j.id = cj.judge_id
            JOIN ship_categories sc ON sc.id = sp.category_id
            JOIN groups g ON g.id = sp.group_id
            WHERE sp.id = ?
        """, (protocol_id,)).fetchone()


def get_main_judge_full_name(competition_id: int) -> str:
    with get_connection() as conn:
        row = conn.execute("""
            SELECT j.full_name
            FROM competition_judges cj
            JOIN judges j ON j.id = cj.judge_id
            WHERE cj.competition_id = ?
              AND cj.role = ?
            ORDER BY j.full_name
            LIMIT 1
        """, (competition_id, JUDGE_ROLE_MAIN)).fetchone()

    return row[0] if row else ""


def get_start_protocol_ships(protocol_id: int):
    with get_connection() as conn:
        return conn.execute("""
            SELECT
                ctps.id,
                p.full_name,
                t.id AS team_id,
                t.organization,
                s.model,
                s.scale,
                ctps.channel
            FROM start_protocols sp
            JOIN competition_judges cj ON cj.id = sp.competition_judge_id
            JOIN competition_team_participant_ships ctps
            JOIN ships s ON s.id = ctps.ship_id
            JOIN competition_team_participants ctp
                ON ctp.id = ctps.competition_team_participant_id
            JOIN participants p ON p.id = ctp.participant_id
            JOIN competition_teams ct ON ct.id = ctp.competition_team_id
            JOIN teams t ON t.id = ct.team_id
            WHERE sp.id = ?
              AND ct.competition_id = cj.competition_id
              AND s.category_id = sp.category_id
              AND ctp.group_id = sp.group_id
            ORDER BY t.id, p.full_name
        """, (protocol_id,)).fetchall()


def save_start_result(
    start_protocol_id: int,
    registered_ship_id: int,
    attempt: int,
    forward_gate_1: int,
    forward_gate_2: int,
    forward_gate_3: int,
    forward_gate_4: int,
    forward_gate_5: int,
    forward_gate_6: int,
    forward_gate_7: int,
    forward_gate_8: int,
    forward_gate_9: int,
    forward_gate_10: int,
    forward_gate_11: int,
    reverse: int,
    mooring: int,
):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO start_results (
                start_protocol_id,
                competition_team_participant_ship_id,
                attempt,

                forward_gate_1,
                forward_gate_2,
                forward_gate_3,
                forward_gate_4,
                forward_gate_5,
                forward_gate_6,
                forward_gate_7,
                forward_gate_8,
                forward_gate_9,
                forward_gate_10,
                forward_gate_11,

                reverse,
                mooring
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT (
                start_protocol_id,
                competition_team_participant_ship_id,
                attempt
            )
            DO UPDATE SET
                forward_gate_1 = excluded.forward_gate_1,
                forward_gate_2 = excluded.forward_gate_2,
                forward_gate_3 = excluded.forward_gate_3,
                forward_gate_4 = excluded.forward_gate_4,
                forward_gate_5 = excluded.forward_gate_5,
                forward_gate_6 = excluded.forward_gate_6,
                forward_gate_7 = excluded.forward_gate_7,
                forward_gate_8 = excluded.forward_gate_8,
                forward_gate_9 = excluded.forward_gate_9,
                forward_gate_10 = excluded.forward_gate_10,
                forward_gate_11 = excluded.forward_gate_11,

                reverse = excluded.reverse,
                mooring = excluded.mooring
        """, (
            start_protocol_id,
            registered_ship_id,
            attempt,

            forward_gate_1,
            forward_gate_2,
            forward_gate_3,
            forward_gate_4,
            forward_gate_5,
            forward_gate_6,
            forward_gate_7,
            forward_gate_8,
            forward_gate_9,
            forward_gate_10,
            forward_gate_11,

            reverse,
            mooring,
        ))


def get_main_judge_short_name(competition_id: int) -> str:
    with get_connection() as conn:
        row = conn.execute("""
            SELECT j.short_name
            FROM competition_judges cj
            JOIN judges j ON j.id = cj.judge_id
            WHERE cj.competition_id = ?
              AND cj.role = ?
            ORDER BY j.full_name
            LIMIT 1
        """, (competition_id, JUDGE_ROLE_MAIN)).fetchone()

    return row[0] if row else ""


def get_start_result_values(protocol_id: int, registered_ship_id: int, attempt: int):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT
                forward_gate_1,
                forward_gate_2,
                forward_gate_3,
                forward_gate_4,
                forward_gate_5,
                forward_gate_6,
                forward_gate_7,
                forward_gate_8,
                forward_gate_9,
                forward_gate_10,
                forward_gate_11,
                reverse,
                mooring
            FROM start_results
            WHERE start_protocol_id = ?
              AND competition_team_participant_ship_id = ?
              AND attempt = ?
        """, (
            protocol_id,
            registered_ship_id,
            attempt,
        )).fetchone()

    return row


def delete_start_result(
    start_protocol_id: int,
    registered_ship_id: int,
    attempt: int,
):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM start_results
            WHERE start_protocol_id = ?
              AND competition_team_participant_ship_id = ?
              AND attempt = ?
        """, (
            start_protocol_id,
            registered_ship_id,
            attempt,
        ))
