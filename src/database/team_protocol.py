from .connection import get_connection
from .summary_table import get_summary_rows


def get_team_protocol_groups(competition_id: int, group_id: int | None = None):
    with get_connection() as conn:
        query = """
            SELECT DISTINCT
                ctp.group_id,
                g.name
            FROM competition_team_participants ctp
            JOIN groups g ON g.id = ctp.group_id
            JOIN competition_teams ct ON ct.id = ctp.competition_team_id
            WHERE ct.competition_id = ?
        """

        params = [competition_id]

        if group_id is not None:
            query += " AND ctp.group_id = ?"
            params.append(group_id)

        query += " ORDER BY g.name"

        return conn.execute(query, params).fetchall()


def get_team_protocol_rows(competition_id: int, group_id: int):
    _stand_judges, summary_rows = get_summary_rows(
        competition_id=competition_id,
        group_id=group_id,
    )

    with get_connection() as conn:
        categories = [
            row[0]
            for row in conn.execute("""
                SELECT name
                FROM ship_categories
                WHERE protocol_1 = 1
                OR protocol_2 = 1
                OR protocol_3 = 1
                ORDER BY name
            """)
        ]

    teams = {}

    for row in summary_rows:
        team_key = row["team_short_name"]

        if team_key not in teams:
            teams[team_key] = {
                "district_name": row["district_name"],
                "organization": row["organization"],
                "coach": row["coach"],
                "team_short_name": row["team_short_name"],
                "category_scores": {},
                "total_score": 0,
                "place": "",
            }

        category_name = row["category_name"]
        current_score = row["team_score"] or 0

        old_score = teams[team_key]["category_scores"].get(category_name, 0)

        if current_score > old_score:
            teams[team_key]["category_scores"][category_name] = current_score

    rows = list(teams.values())

    for row in rows:
        row["total_score"] = sum(
            row["category_scores"].get(category_name, 0)
            for category_name in categories
        )

    rows.sort(
        key=lambda row: (
            -row["total_score"],
            row["organization"],
        )
    )

    previous_score = None
    previous_place = None

    for index, row in enumerate(rows, start=1):
        if previous_score is not None and row["total_score"] == previous_score:
            row["place"] = previous_place
        else:
            row["place"] = index
            previous_place = index
            previous_score = row["total_score"]

    rows.sort(key=lambda row: row["place"])

    return categories, rows
