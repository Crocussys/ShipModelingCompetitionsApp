from .connection import get_connection


def calculate_average(values: list[int | float]) -> float | None:
    values = [value for value in values if value is not None]

    if not values:
        return None

    count = len(values)

    if count == 1:
        return values[0]

    if count == 2:
        return sum(values) / 2

    if count in (3, 4):
        return (sum(values) - min(values)) / (count - 1)

    return (sum(values) - min(values) - max(values)) / (count - 2)


def get_summary_rows(
    competition_id: int,
    search: str = "",
    category_id: int | None = None,
    group_id: int | None = None,
    team_id: int | None = None,
):
    search = search.strip().casefold()

    with get_connection() as conn:
        ships = conn.execute("""
            SELECT
                ctps.id AS registered_ship_id,
                s.id AS ship_id,
                p.full_name AS participant_full_name,
                s.name AS ship_name,
                s.model AS ship_model,
                s.scale,
                ctps.channel,
                sc.name AS category_name,
                g.name AS group_name,
                t.short_name AS team_short_name,
                s.category_id,
                ctp.group_id,
                t.id AS team_id
            FROM competition_team_participant_ships ctps
            JOIN ships s ON s.id = ctps.ship_id
            JOIN ship_categories sc ON sc.id = s.category_id
            JOIN competition_team_participants ctp
                ON ctp.id = ctps.competition_team_participant_id
            JOIN participants p ON p.id = ctp.participant_id
            JOIN groups g ON g.id = ctp.group_id
            JOIN competition_teams ct ON ct.id = ctp.competition_team_id
            JOIN teams t ON t.id = ct.team_id
            WHERE ct.competition_id = ?
            ORDER BY sc.name, g.name, p.full_name
        """, (competition_id,)).fetchall()

        stand_judges = conn.execute("""
            SELECT
                cj.id,
                j.short_name
            FROM competition_judges cj
            JOIN judges j ON j.id = cj.judge_id
            WHERE cj.competition_id = ?
              AND cj.role IN (2, 4)
            ORDER BY j.full_name
        """, (competition_id,)).fetchall()

        rows = []

        for ship in ships:
            (
                registered_ship_id,
                ship_id,
                participant_full_name,
                ship_name,
                ship_model,
                scale,
                channel,
                category_name,
                group_name,
                team_short_name,
                ship_category_id,
                ship_group_id,
                current_team_id,
            ) = ship

            if search:
                if (
                    search not in participant_full_name.casefold()
                    and search not in ship_name.casefold()
                    and search not in ship_model.casefold()
                ):
                    continue

            if category_id is not None and ship_category_id != category_id:
                continue

            if group_id is not None and ship_group_id != group_id:
                continue

            if team_id is not None and current_team_id != team_id:
                continue

            stand_scores = []

            for competition_judge_id, judge_name in stand_judges:
                row = conn.execute("""
                    SELECT
                        sr.execution_score +
                        sr.impression_score +
                        sr.work_volume_score +
                        sr.compliance_score
                    FROM stand_results sr
                    JOIN stand_protocols sp
                        ON sp.id = sr.stand_protocol_id
                    WHERE sp.competition_judge_id = ?
                      AND sr.competition_team_participant_ship_id = ?
                """, (
                    competition_judge_id,
                    registered_ship_id,
                )).fetchone()

                score = row[0] if row else None
                stand_scores.append(score)

            stand_average = calculate_average(stand_scores)

            attempt_scores = []

            for attempt in (1, 2, 3):
                rows_for_attempt = conn.execute("""
                    SELECT
                        r.forward_gate_1 +
                        r.forward_gate_2 +
                        r.forward_gate_3 +
                        r.forward_gate_4 +
                        r.forward_gate_5 +
                        r.forward_gate_6 +
                        r.forward_gate_7 +
                        r.forward_gate_8 +
                        r.forward_gate_9 +
                        r.forward_gate_10 +
                        r.forward_gate_11 +
                        r.reverse +
                        r.mooring
                    FROM start_results r
                    JOIN start_protocols sp
                        ON sp.id = r.start_protocol_id
                    WHERE r.competition_team_participant_ship_id = ?
                      AND r.attempt = ?
                      AND sp.category_id = ?
                      AND sp.group_id = ?
                """, (
                    registered_ship_id,
                    attempt,
                    ship_category_id,
                    ship_group_id,
                )).fetchall()

                judge_attempt_values = [
                    row[0] for row in rows_for_attempt
                    if row[0] is not None
                ]

                attempt_scores.append(
                    calculate_average(judge_attempt_values)
                )

            movement_score = calculate_average(attempt_scores)

            total_score = None
            if stand_average is not None and movement_score is not None:
                total_score = stand_average + movement_score

            rows.append({
                "ship_id": ship_id,
                "participant_full_name": participant_full_name,
                "ship_name": ship_name,
                "ship_model": ship_model,
                "scale": scale,
                "channel": channel,
                "category_name": category_name,
                "group_name": group_name,
                "team_short_name": team_short_name,
                "stand_scores": stand_scores,
                "stand_average": stand_average,
                "attempt_scores": attempt_scores,
                "movement_score": movement_score,
                "total_score": total_score,
            })

    return stand_judges, rows
