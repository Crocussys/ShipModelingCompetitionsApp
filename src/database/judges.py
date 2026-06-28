from .connection import get_connection


JUDGE_ROLE_MAIN = 1
JUDGE_ROLE_STAND_MAIN = 2
JUDGE_ROLE_JUDGE = 3
JUDGE_ROLE_STAND_JUDGE = 4
JUDGE_ROLE_SECRETARY = 5

JUDGE_ROLES = {
    JUDGE_ROLE_MAIN: "Главный судья",
    JUDGE_ROLE_STAND_MAIN: "Главный судья стенда",
    JUDGE_ROLE_JUDGE: "Судья",
    JUDGE_ROLE_STAND_JUDGE: "Судья стенда",
    JUDGE_ROLE_SECRETARY: "Секретарь",
}


def get_judges(competition_id: int | None = None, search: str = ""):
    search = search.strip().casefold()

    with get_connection() as conn:
        if competition_id is None:
            rows = conn.execute("""
                SELECT id, full_name, short_name
                FROM judges
                ORDER BY full_name
            """).fetchall()
        else:
            rows = conn.execute("""
                SELECT
                    cj.id AS competition_judge_id,
                    j.id AS judge_id,
                    j.full_name,
                    j.short_name,
                    cj.role
                FROM competition_judges cj
                JOIN judges j ON j.id = cj.judge_id
                WHERE cj.competition_id = ?
                ORDER BY j.full_name
            """, (competition_id,)).fetchall()

    if not search:
        return rows

    if competition_id is None:
        return [
            row for row in rows
            if search in row[1].casefold()
            or search in row[2].casefold()
        ]

    return [
        row for row in rows
        if search in row[2].casefold()
        or search in row[3].casefold()
    ]


def get_judge_role_name(role: int) -> str:
    return JUDGE_ROLES.get(role, "Неизвестно")


def create_judge(full_name: str, short_name: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO judges (full_name, short_name)
            VALUES (?, ?)
        """, (full_name.strip(), short_name.strip()))

        return cursor.lastrowid


def update_judge(judge_id: int, full_name: str, short_name: str):
    with get_connection() as conn:
        conn.execute("""
            UPDATE judges
            SET full_name = ?, short_name = ?
            WHERE id = ?
        """, (full_name.strip(), short_name.strip(), judge_id))


def delete_judge(judge_id: int):
    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        conn.execute("""
            DELETE FROM judges
            WHERE id = ?
        """, (judge_id,))


def assign_judge_to_competition(
    judge_id: int,
    competition_id: int,
    role: int = JUDGE_ROLE_JUDGE,
):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO competition_judges (
                judge_id,
                competition_id,
                role
            )
            VALUES (?, ?, ?)
            ON CONFLICT(judge_id, competition_id)
            DO UPDATE SET role = excluded.role
        """, (judge_id, competition_id, role))


def remove_judge_from_competition(competition_judge_id: int):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM competition_judges
            WHERE id = ?
        """, (competition_judge_id,))


def is_judge_assigned(judge_id: int, competition_id: int) -> bool:
    with get_connection() as conn:
        row = conn.execute("""
            SELECT 1
            FROM competition_judges
            WHERE judge_id = ?
              AND competition_id = ?
        """, (judge_id, competition_id)).fetchone()

        return row is not None

def get_competition_judges_for_combo(competition_id: int):
    with get_connection() as conn:
        return conn.execute("""
            SELECT
                cj.id,
                j.short_name || ' — ' || 
                CASE cj.role
                    WHEN 1 THEN 'Главный судья'
                    WHEN 2 THEN 'Главный судья стенда'
                    WHEN 3 THEN 'Судья'
                    WHEN 4 THEN 'Судья стенда'
                    WHEN 5 THEN 'Секретарь'
                    ELSE 'Неизвестно'
                END
            FROM competition_judges cj
            JOIN judges j ON j.id = cj.judge_id
            WHERE cj.competition_id = ?
            ORDER BY j.full_name
        """, (competition_id,)).fetchall()
