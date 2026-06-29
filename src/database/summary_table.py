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
                d.name AS district_name,
                t.organization,
                ct.coach,
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
            JOIN districts d ON d.id = t.district_id
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
                district_name,
                organization,
                coach,
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

            fsr_attempts = conn.execute("""
                SELECT
                    attempt,
                    laps,
                    seconds
                FROM fsr_results fr
                JOIN fsr_protocols fp
                    ON fp.id = fr.fsr_protocol_id
                WHERE fp.competition_team_participant_ship_id = ?
                ORDER BY attempt
            """, (registered_ship_id,)).fetchall()

            laps = ["", "", ""]
            seconds = ["", "", ""]

            total_laps = None

            for attempt, lap_count, second_count in fsr_attempts:
                laps[attempt - 1] = lap_count
                seconds[attempt - 1] = second_count

                if total_laps is None:
                    total_laps = 0

                total_laps += lap_count

            total_score = (
                (stand_average or 0)
                + (movement_score or 0)
                + (total_laps or 0)
            )

            rows.append({
                "ship_id": ship_id,
                "participant_full_name": participant_full_name,
                "ship_name": ship_name,
                "ship_model": ship_model,
                "district_name": district_name,
                "organization": organization,
                "coach": coach,
                "scale": scale,
                "channel": channel,
                "category_name": category_name,
                "group_name": group_name,
                "team_short_name": team_short_name,
                "stand_scores": stand_scores,
                "stand_average": stand_average,
                "attempt_scores": attempt_scores,
                "movement_score": movement_score,
                "laps": laps,
                "seconds": seconds,
                "total_laps": total_laps,
                "total_score": total_score,
            })

    assign_places_and_team_scores(rows)
    
    rows.sort(
        key=lambda row: (
            -row["total_score"],
            row["participant_full_name"],
        )
    )

    return stand_judges, rows


def assign_places_and_team_scores(rows: list[dict]):
    groups = {}

    for row in rows:
        key = (
            row["category_name"],
            row["group_name"],
        )
        groups.setdefault(key, []).append(row)

    for group_rows in groups.values():
        group_rows.sort(
            key=lambda row: (
                -row["total_score"],
                row["participant_full_name"],
            )
        )

        max_score = group_rows[0]["total_score"] if group_rows else 0

        previous_score = None
        previous_place = None

        for index, row in enumerate(group_rows, start=1):
            current_score = row["total_score"]

            if previous_score is not None and current_score == previous_score:
                row["place"] = previous_place
            else:
                row["place"] = index
                previous_place = index
                previous_score = current_score

            if max_score == 0:
                row["team_score"] = 0
            else:
                row["team_score"] = current_score / max_score * 200
