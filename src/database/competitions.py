from .connection import get_connection


COMPETITION_STATUS_SETUP = 0
COMPETITION_STATUS_REGISTRATION = 1
COMPETITION_STATUS_PRIMARY_PROTOCOLS = 2
COMPETITION_STATUS_SECONDARY_PROTOCOLS = 3

COMPETITION_STATUSES = {
    COMPETITION_STATUS_SETUP: "Настройка соревнования",
    COMPETITION_STATUS_REGISTRATION: "Регистрация",
    COMPETITION_STATUS_PRIMARY_PROTOCOLS: "Первичные протоколы",
    COMPETITION_STATUS_SECONDARY_PROTOCOLS: "Вторичные протоколы",
}


def get_competition_status_name(status: int) -> str:
    return COMPETITION_STATUSES.get(status, "Неизвестно")


def get_competitions() -> list[tuple[int, str]]:
    with get_connection() as conn:
        return conn.execute("""
            SELECT id, name
            FROM competitions
            ORDER BY id DESC
        """).fetchall()


def create_competition(name: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO competitions (name, status)
            VALUES (?, 0)
        """, (name.strip(),))

        return cursor.lastrowid

def get_competition(competition_id: int):
    with get_connection() as conn:
        return conn.execute("""
            SELECT id, name, status
            FROM competitions
            WHERE id = ?
        """, (competition_id,)).fetchone()


def update_competition_status(competition_id: int, status: int):
    with get_connection() as conn:
        conn.execute("""
            UPDATE competitions
            SET status = ?
            WHERE id = ?
        """, (status, competition_id))
