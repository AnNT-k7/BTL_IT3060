"""Create reproducible simulated instances for the timetable demo."""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path


ROOT = Path(__file__).parent / "data"


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def generate(name: str, groups: int, sessions_per_group: int, impossible: bool = False,
             seed: int = 3160, root: Path = ROOT) -> Path:
    out = root / name
    out.mkdir(parents=True, exist_ok=True)
    days = ["T2", "T3", "T4", "T5", "T6"]
    periods = 6
    teachers = max(4, groups + 2)
    rooms = max(3, groups)
    session_rows = []
    for group in range(groups):
        for item in range(sessions_per_group):
            index = group * sessions_per_group + item
            session_rows.append({
                "session_id": f"S{index + 1:02d}",
                "course_id": f"HP{item + 1:02d}",
                "teacher_id": f"GV{index % teachers + 1:02d}",
                "group_id": f"NH{group + 1:02d}",
                "size": 35 + (group % 3) * 5,
                "duration": 2,
                "room_type": "normal",
            })
    if impossible:
        # Teacher GV01 needs two 2-period sessions but has only two free periods.
        session_rows[1]["teacher_id"] = "GV01"
    random.Random(seed).shuffle(session_rows)
    room_rows = [{"room_id": f"P{r + 1:02d}", "capacity": 60, "room_type": "normal"}
                 for r in range(rooms)]
    availability_rows = []
    preference_rows = []
    for teacher in range(1, teachers + 1):
        tid = f"GV{teacher:02d}"
        for day in days:
            for period in range(1, periods + 1):
                free = not impossible or tid != "GV01" or (day == "T2" and period in (1, 2))
                availability_rows.append({"teacher_id": tid, "day": day, "period": period,
                                          "available": str(free).lower()})
                preference_rows.append({"teacher_id": tid, "day": day, "period": period,
                                        "preference": 0 if period <= 4 else 2})
    write_csv(out / "sessions.csv", list(session_rows[0]), session_rows)
    write_csv(out / "rooms.csv", list(room_rows[0]), room_rows)
    write_csv(out / "availability.csv", list(availability_rows[0]), availability_rows)
    write_csv(out / "preferences.csv", list(preference_rows[0]), preference_rows)
    config = {"days": days, "periods_per_day": periods,
              "weights": {"late_periods": 2, "student_gaps": 1, "preference_penalty": 1},
              "time_limit_seconds": 10,
              "seed": seed,
              "data_note": "Dữ liệu mô phỏng sinh bởi generate_data.py; không phải lịch chính thức."}
    (out / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


def generate_tight(name: str, gadgets: int, seed: int = 3160, root: Path = ROOT) -> Path:
    """Create a planted feasible instance with scarce teacher slots and typed rooms.

    Each four-session block has one flexible session followed by three sessions
    pinned to distinct periods. The flexible session must take the remaining
    period. The blocks are independent so difficulty grows without hiding the
    reason a timetable is feasible.
    """
    if gadgets < 1:
        raise ValueError('gadgets phải dương')
    out = root / name
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    sessions = []
    rooms = []
    availability = []
    for block in range(1, gadgets + 1):
        room_type = f'lab_{block:02d}'
        rooms.append({'room_id': f'P{block:02d}', 'capacity': 40, 'room_type': room_type})
        fixed_periods = rng.sample((1, 2, 3, 4), 3)
        for label, allowed in (('A', (1, 2, 3, 4)), ('B', (fixed_periods[0],)),
                               ('C', (fixed_periods[1],)), ('D', (fixed_periods[2],))):
            session_id = f'G{block:02d}_{label}'
            teacher = f'GV_{session_id}'
            sessions.append({'session_id': session_id, 'course_id': session_id,
                             'teacher_id': teacher, 'group_id': f'NH_{session_id}',
                             'size': 30, 'duration': 1, 'room_type': room_type})
            for period in range(1, 5):
                availability.append({'teacher_id': teacher, 'day': 'T2', 'period': period,
                                     'available': str(period in allowed).lower()})
    write_csv(out / 'sessions.csv', list(sessions[0]), sessions)
    write_csv(out / 'rooms.csv', list(rooms[0]), rooms)
    write_csv(out / 'availability.csv', list(availability[0]), availability)
    config = {'days': ['T2'], 'periods_per_day': 4, 'time_limit_seconds': 10,
              'weights': {'late_periods': 0, 'student_gaps': 0, 'preference_penalty': 0},
              'seed': seed,
              'data_note': 'Dữ liệu stress test có nghiệm cài sẵn; mỗi phòng là một loại lab riêng, không phải lịch thực tế.'}
    (out / 'config.json').write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return out


if __name__ == "__main__":
    generate("small", 3, 3, seed=3161)
    generate("demo", 6, 4, seed=3162)
    generate("large", 8, 5, seed=3163)
    generate("unsat", 3, 3, impossible=True, seed=3164)
    generate_tight('tight_demo', 5, seed=3161)
