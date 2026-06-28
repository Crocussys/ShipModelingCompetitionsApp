from .connection import get_connection


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


def create_stand_protocol(
    competition_id: int,
    judge_id: int,
    category_id: int,
    group_id: int,
    status: int = STAND_PROTOCOL_NOT_PRINTED,
) -> int:
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO stand_protocols (
                competition_id,
                judge_id,
                category_id,
                group_id,
                status
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            competition_id,
            judge_id,
            category_id,
            group_id,
            status,
        ))

        return cursor.lastrowid


def create_stand_result(
    stand_protocol_id: int,
    competition_team_participant_ship_id: int,
    execution_score: int,
    impression_score: int,
    work_volume_score: int,
    compliance_score: int,
) -> int:
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO stand_results (
                stand_protocol_id,
                competition_team_participant_ship_id,
                execution_score,
                impression_score,
                work_volume_score,
                compliance_score
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            stand_protocol_id,
            competition_team_participant_ship_id,
            execution_score,
            impression_score,
            work_volume_score,
            compliance_score,
        ))

        return cursor.lastrowid