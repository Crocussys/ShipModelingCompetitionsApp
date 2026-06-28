from config import get_database_path
from .connection import get_connection


def database_exists() -> bool:
    db_path = get_database_path()
    return db_path.exists() and db_path.is_file()


def init_database():
    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS competitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS judges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL UNIQUE,
                short_name TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS competition_judges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judge_id INTEGER NOT NULL,
                competition_id INTEGER NOT NULL,
                role INTEGER NOT NULL DEFAULT 3,

                UNIQUE (judge_id, competition_id),

                FOREIGN KEY (judge_id)
                    REFERENCES judges(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (competition_id)
                    REFERENCES competitions(id)
                    ON DELETE CASCADE
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS ship_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS districts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_name TEXT NOT NULL UNIQUE,
                organization TEXT NOT NULL,
                district_id INTEGER NOT NULL,

                FOREIGN KEY (district_id)
                    REFERENCES districts(id)
                    ON DELETE RESTRICT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS competition_teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                competition_id INTEGER NOT NULL,
                coach TEXT NOT NULL DEFAULT '',

                UNIQUE (team_id, competition_id),

                FOREIGN KEY (team_id)
                    REFERENCES teams(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (competition_id)
                    REFERENCES competitions(id)
                    ON DELETE CASCADE
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                birth_date TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS competition_team_participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id INTEGER NOT NULL,
                competition_team_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,

                UNIQUE (
                    participant_id,
                    competition_team_id,
                    group_id
                ),

                FOREIGN KEY (participant_id)
                    REFERENCES participants(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (competition_team_id)
                    REFERENCES competition_teams(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (group_id)
                    REFERENCES groups(id)
                    ON DELETE RESTRICT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS ships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL DEFAULT '',
                model TEXT NOT NULL DEFAULT '',
                category_id INTEGER NOT NULL,
                scale TEXT NOT NULL DEFAULT '',

                FOREIGN KEY (category_id)
                    REFERENCES ship_categories(id)
                    ON DELETE RESTRICT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS competition_team_participant_ships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ship_id INTEGER NOT NULL,
                competition_team_participant_id INTEGER NOT NULL,
                channel TEXT NOT NULL DEFAULT '',

                UNIQUE (ship_id, competition_team_participant_id),

                FOREIGN KEY (ship_id)
                    REFERENCES ships(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (competition_team_participant_id)
                    REFERENCES competition_team_participants(id)
                    ON DELETE CASCADE
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS stand_protocols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competition_judge_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                status INTEGER NOT NULL DEFAULT 0
                    CHECK (status IN (0, 1, 2)),

                FOREIGN KEY (competition_judge_id)
                    REFERENCES competition_judges(id)
                    ON DELETE RESTRICT,

                FOREIGN KEY (category_id)
                    REFERENCES ship_categories(id)
                    ON DELETE RESTRICT,

                FOREIGN KEY (group_id)
                    REFERENCES groups(id)
                    ON DELETE RESTRICT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS stand_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stand_protocol_id INTEGER NOT NULL,
                competition_team_participant_ship_id INTEGER NOT NULL,

                execution_score INTEGER NOT NULL CHECK (execution_score BETWEEN 0 AND 100),
                impression_score INTEGER NOT NULL CHECK (impression_score BETWEEN 0 AND 100),
                work_volume_score INTEGER NOT NULL CHECK (work_volume_score BETWEEN 0 AND 100),
                compliance_score INTEGER NOT NULL CHECK (compliance_score BETWEEN 0 AND 100),

                UNIQUE (
                    stand_protocol_id,
                    competition_team_participant_ship_id
                ),

                FOREIGN KEY (stand_protocol_id)
                    REFERENCES stand_protocols(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (competition_team_participant_ship_id)
                    REFERENCES competition_team_participant_ships(id)
                    ON DELETE CASCADE
            )
        """)


def ensure_database(create_if_missing: bool) -> bool:
    if database_exists():
        init_database()
        return True

    if not create_if_missing:
        return False

    init_database()
    return True
