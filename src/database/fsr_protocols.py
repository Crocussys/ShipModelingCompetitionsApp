from .connection import get_connection


FSR_PROTOCOL_NOT_FILLED = 0
FSR_PROTOCOL_ACCEPTED = 1

FSR_PROTOCOL_STATUSES = {
    FSR_PROTOCOL_NOT_FILLED: "Не заполнен",
    FSR_PROTOCOL_ACCEPTED: "Принят",
}


def get_fsr_protocol_status_name(status: int) -> str:
    return FSR_PROTOCOL_STATUSES.get(status, "Неизвестно")


def generate_fsr_protocols_for_competition(competition_id: int):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM fsr_protocols
            WHERE id IN (
                SELECT fp.id
                FROM fsr_protocols fp
                JOIN competition_team_participant_ships ctps
                    ON ctps.id = fp.competition_team_participant_ship_id
                JOIN ships s ON s.id = ctps.ship_id
                JOIN ship_categories sc ON sc.id = s.category_id
                JOIN competition_team_participants ctp
                    ON ctp.id = ctps.competition_team_participant_id
                JOIN competition_teams ct
                    ON ct.id = ctp.competition_team_id
                WHERE ct.competition_id = ?
                  AND sc.protocol_3 = 0
            )
        """, (competition_id,))

        registered_ships = conn.execute("""
            SELECT ctps.id
            FROM competition_team_participant_ships ctps
            JOIN ships s ON s.id = ctps.ship_id
            JOIN ship_categories sc ON sc.id = s.category_id
            JOIN competition_team_participants ctp
                ON ctp.id = ctps.competition_team_participant_id
            JOIN competition_teams ct
                ON ct.id = ctp.competition_team_id
            WHERE ct.competition_id = ?
              AND sc.protocol_3 = 1
        """, (competition_id,)).fetchall()

        for (registered_ship_id,) in registered_ships:
            conn.execute("""
                INSERT OR IGNORE INTO fsr_protocols (
                    competition_team_participant_ship_id,
                    status
                )
                VALUES (?, 0)
            """, (registered_ship_id,))


def get_fsr_protocols(
    competition_id: int,
    search: str = "",
    category_id: int | None = None,
    group_id: int | None = None,
):
    search = search.strip().casefold()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                fp.id,
                p.full_name,
                s.name,
                s.model,
                sc.name,
                g.name,
                fp.status,
                s.category_id,
                ctp.group_id
            FROM fsr_protocols fp
            JOIN competition_team_participant_ships ctps
                ON ctps.id = fp.competition_team_participant_ship_id
            JOIN ships s ON s.id = ctps.ship_id
            JOIN ship_categories sc ON sc.id = s.category_id
            JOIN competition_team_participants ctp
                ON ctp.id = ctps.competition_team_participant_id
            JOIN participants p ON p.id = ctp.participant_id
            JOIN groups g ON g.id = ctp.group_id
            JOIN competition_teams ct
                ON ct.id = ctp.competition_team_id
            WHERE ct.competition_id = ?
            ORDER BY sc.name, g.name, p.full_name
        """, (competition_id,)).fetchall()

    if search:
        rows = [
            row for row in rows
            if search in row[1].casefold()
            or search in row[2].casefold()
            or search in row[3].casefold()
        ]

    if category_id is not None:
        rows = [row for row in rows if row[7] == category_id]

    if group_id is not None:
        rows = [row for row in rows if row[8] == group_id]

    return rows


def get_fsr_protocol(protocol_id: int):
    with get_connection() as conn:
        return conn.execute("""
            SELECT
                fp.id,
                p.full_name,
                s.name,
                s.model,
                sc.name,
                g.name
            FROM fsr_protocols fp
            JOIN competition_team_participant_ships ctps
                ON ctps.id = fp.competition_team_participant_ship_id
            JOIN ships s ON s.id = ctps.ship_id
            JOIN ship_categories sc ON sc.id = s.category_id
            JOIN competition_team_participants ctp
                ON ctp.id = ctps.competition_team_participant_id
            JOIN participants p ON p.id = ctp.participant_id
            JOIN groups g ON g.id = ctp.group_id
            WHERE fp.id = ?
        """, (protocol_id,)).fetchone()


def get_fsr_results(protocol_id: int):
    with get_connection() as conn:
        return conn.execute("""
            SELECT attempt, laps, seconds
            FROM fsr_results
            WHERE fsr_protocol_id = ?
            ORDER BY attempt
        """, (protocol_id,)).fetchall()


def save_fsr_result(
    protocol_id: int,
    attempt: int,
    laps: int,
    seconds: int,
):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO fsr_results (
                fsr_protocol_id,
                attempt,
                laps,
                seconds
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT (fsr_protocol_id, attempt)
            DO UPDATE SET
                laps = excluded.laps,
                seconds = excluded.seconds
        """, (
            protocol_id,
            attempt,
            laps,
            seconds,
        ))


def update_fsr_protocol_status(protocol_id: int, status: int):
    with get_connection() as conn:
        conn.execute("""
            UPDATE fsr_protocols
            SET status = ?
            WHERE id = ?
        """, (status, protocol_id))
