from __future__ import annotations

import csv
import io
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Session:
    session_id: str
    course_id: str
    teacher_id: str
    group_id: str
    size: int
    duration: int
    room_type: str


@dataclass(frozen=True)
class Room:
    room_id: str
    capacity: int
    room_type: str


@dataclass(frozen=True)
class Slot:
    day: str
    period: int
    room_id: str


@dataclass
class Problem:
    sessions: list[Session]
    rooms: list[Room]
    days: list[str]
    periods_per_day: int
    availability: dict[tuple[str, str, int], bool]
    preferences: dict[tuple[str, str, int], int]
    weights: dict[str, float]
    time_limit_seconds: float


class InputError(ValueError):
    pass


def _csv_rows(source, name, fields):
    reader = csv.DictReader(io.StringIO(source))
    if not reader.fieldnames or any(f not in reader.fieldnames for f in fields):
        raise InputError(f"{name}: thiếu cột: {', '.join(f for f in fields if f not in (reader.fieldnames or []))}")
    if len(reader.fieldnames) != len(set(reader.fieldnames)):
        raise InputError(f'{name}: tên cột bị trùng')
    for line, row in enumerate(reader, 2):
        if None in row or any(value is None for value in row.values()):
            raise InputError(f"{name}:{line}: thiếu giá trị hoặc thừa cột")
        yield line, {k: v.strip() for k, v in row.items()}


def _integer(value, name, line, field, minimum, maximum=None):
    try:
        result = int(value)
    except (TypeError, ValueError):
        raise InputError(f"{name}:{line} {field}: phải là số nguyên") from None
    if result < minimum or (maximum is not None and result > maximum):
        raise InputError(f"{name}:{line} {field}: ngoài khoảng hợp lệ")
    return result


def load_text(files: dict[str, str]) -> Problem:
    required = ('sessions.csv', 'rooms.csv', 'availability.csv', 'config.json')
    for name in required:
        if name not in files:
            raise InputError(f"Thiếu tệp {name}")
    try:
        config = json.loads(files['config.json'])
        days = config['days']
        periods = config['periods_per_day']
        weights = config.get('weights', {})
        limit = float(config.get('time_limit_seconds', 10))
    except (KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
        raise InputError(f"config.json: cấu hình không hợp lệ: {exc}") from exc
    if not isinstance(days, list) or not days or any(not isinstance(d, str) or not d for d in days) or len(days) != len(set(days)):
        raise InputError('config.json days: cần danh sách ngày khác nhau')
    if type(periods) is not int or not 1 <= periods <= 24 or not math.isfinite(limit) or limit < 0:
        raise InputError('config.json: periods_per_day hoặc time_limit_seconds không hợp lệ')
    try:
        weights = {k: float(weights.get(k, 1)) for k in ('late_periods', 'student_gaps', 'preference_penalty')}
    except (AttributeError, ValueError, TypeError) as exc:
        raise InputError(f'config.json weights: {exc}') from exc
    if any(not math.isfinite(v) or v < 0 for v in weights.values()):
        raise InputError('config.json weights: phải hữu hạn và không âm')
    rooms = []
    seen = set()
    for line, row in _csv_rows(files['rooms.csv'], 'rooms.csv', ('room_id', 'capacity', 'room_type')):
        rid = row['room_id']
        if not rid or rid in seen or not row['room_type']:
            raise InputError(f'rooms.csv:{line} room_id/room_type: trống hoặc trùng')
        seen.add(rid)
        rooms.append(Room(rid, _integer(row['capacity'], 'rooms.csv', line, 'capacity', 0), row['room_type']))
    if not rooms:
        raise InputError('rooms.csv: cần ít nhất một phòng')
    sessions = []
    seen = set()
    for line, row in _csv_rows(files['sessions.csv'], 'sessions.csv', ('session_id', 'course_id', 'teacher_id', 'group_id', 'size', 'duration', 'room_type')):
        sid = row['session_id']
        if not sid or sid in seen or any(not row[f] for f in ('course_id', 'teacher_id', 'group_id')):
            raise InputError(f'sessions.csv:{line} mã: trống hoặc trùng')
        seen.add(sid)
        size = _integer(row['size'], 'sessions.csv', line, 'size', 0)
        duration = _integer(row['duration'], 'sessions.csv', line, 'duration', 1, 2)
        if not any(r.capacity >= size and (not row['room_type'] or r.room_type == row['room_type']) for r in rooms):
            raise InputError(f'sessions.csv:{line} size/room_type: không có phòng phù hợp')
        sessions.append(Session(sid, row['course_id'], row['teacher_id'], row['group_id'], size, duration, row['room_type']))
    if not sessions:
        raise InputError('sessions.csv: cần ít nhất một buổi học')
    availability = {}
    for line, row in _csv_rows(files['availability.csv'], 'availability.csv', ('teacher_id', 'day', 'period', 'available')):
        teacher, day = row['teacher_id'], row['day']
        period = _integer(row['period'], 'availability.csv', line, 'period', 1, periods)
        if day not in days or teacher not in {s.teacher_id for s in sessions}:
            raise InputError(f'availability.csv:{line} teacher_id/day: tham chiếu không hợp lệ')
        key = (teacher, day, period)
        if key in availability or row['available'].lower() not in ('true', 'false', '1', '0'):
            raise InputError(f'availability.csv:{line} available/khóa: giá trị sai hoặc trùng')
        availability[key] = row['available'].lower() in ('true', '1')
    teachers = {s.teacher_id for s in sessions}
    if not teachers <= {k[0] for k in availability}:
        missing = sorted(teachers - {k[0] for k in availability})
        raise InputError(f'sessions.csv teacher_id: không có trong availability.csv: {missing}')
    preferences = {}
    if 'preferences.csv' in files:
        for line, row in _csv_rows(files['preferences.csv'], 'preferences.csv', ('teacher_id', 'day', 'period', 'preference')):
            period = _integer(row['period'], 'preferences.csv', line, 'period', 1, periods)
            key = (row['teacher_id'], row['day'], period)
            if row['teacher_id'] not in teachers or row['day'] not in days or key in preferences:
                raise InputError(f'preferences.csv:{line} teacher_id/day: sai hoặc trùng')
            preferences[key] = _integer(row['preference'], 'preferences.csv', line, 'preference', 0, 1_000_000)
    return Problem(sessions, rooms, days, periods, availability, preferences, weights, limit)


def load_directory(path: str | Path) -> Problem:
    directory = Path(path)
    names = ('sessions.csv', 'rooms.csv', 'availability.csv', 'preferences.csv', 'config.json')
    try:
        return load_text({name: (directory / name).read_text(encoding='utf-8-sig') for name in names if (directory / name).exists()})
    except OSError as exc:
        raise InputError(str(exc)) from exc


def domain(problem: Problem, session: Session, deadline: float | None = None) -> list[Slot]:
    values = []
    for day in problem.days:
        for period in range(1, problem.periods_per_day - session.duration + 2):
            for room in problem.rooms:
                if deadline is not None and time.perf_counter() >= deadline:
                    raise TimeoutError('Hết thời gian khi tạo miền giá trị')
                if (room.capacity >= session.size
                        and (not session.room_type or room.room_type == session.room_type)
                        and all(problem.availability.get((session.teacher_id, day, p), False)
                                for p in range(period, period + session.duration))):
                    values.append(Slot(day, period, room.room_id))
    return values


def overlap(a: Session, av: Slot, b: Session, bv: Slot) -> bool:
    return av.day == bv.day and av.period < bv.period + b.duration and bv.period < av.period + a.duration


def conflict(a: Session, av: Slot, b: Session, bv: Slot) -> bool:
    return overlap(a, av, b, bv) and (av.room_id == bv.room_id or a.teacher_id == b.teacher_id or a.group_id == b.group_id)


def validate_schedule(problem: Problem, assignment: dict[str, Slot]) -> list[str]:
    errors = []
    sessions = {s.session_id: s for s in problem.sessions}
    rooms = {r.room_id: r for r in problem.rooms}
    for sid in sessions.keys() - assignment.keys():
        errors.append(f'missing:{sid}')
    for sid in assignment.keys() - sessions.keys():
        errors.append(f'unknown:{sid}')
    for sid, slot in assignment.items():
        if sid not in sessions:
            continue
        s = sessions[sid]
        room = rooms.get(slot.room_id)
        if room is None or room.capacity < s.size or (s.room_type and room.room_type != s.room_type):
            errors.append(f'room:{sid}')
        if slot.day not in problem.days or slot.period < 1 or slot.period + s.duration - 1 > problem.periods_per_day:
            errors.append(f'time:{sid}')
        elif any(not problem.availability.get((s.teacher_id, slot.day, p), False) for p in range(slot.period, slot.period + s.duration)):
            errors.append(f'availability:{sid}')
    ordered = [(s, assignment[s.session_id]) for s in problem.sessions if s.session_id in assignment]
    for i, (a, av) in enumerate(ordered):
        for b, bv in ordered[i + 1:]:
            if overlap(a, av, b, bv):
                for kind, same in (('room', av.room_id == bv.room_id), ('teacher', a.teacher_id == b.teacher_id), ('group', a.group_id == b.group_id)):
                    if same:
                        errors.append(f'{kind}_conflict:{a.session_id}:{b.session_id}')
    return sorted(errors)


def explain_slot(problem: Problem, assignment: dict[str, Slot], session_id: str, slot: Slot) -> list[str]:
    """Explain why moving one session to a proposed slot would be invalid."""
    sessions = {s.session_id: s for s in problem.sessions}
    rooms = {r.room_id: r for r in problem.rooms}
    if session_id not in sessions:
        return [f'Không có buổi {session_id}']
    session = sessions[session_id]
    reasons = []
    room = rooms.get(slot.room_id)
    if room is None:
        reasons.append(f'Phòng {slot.room_id} không tồn tại')
    else:
        if room.capacity < session.size:
            reasons.append(f'Phòng {slot.room_id} chỉ chứa {room.capacity}/{session.size} sinh viên')
        if session.room_type and room.room_type != session.room_type:
            reasons.append(f'Phòng {slot.room_id} không đúng loại {session.room_type}')
    if slot.day not in problem.days or slot.period < 1 or slot.period + session.duration - 1 > problem.periods_per_day:
        reasons.append('Buổi học vượt ra ngoài khung thời gian của tuần')
        return reasons
    for period in range(slot.period, slot.period + session.duration):
        if not problem.availability.get((session.teacher_id, slot.day, period), False):
            reasons.append(f'Giảng viên {session.teacher_id} không rảnh {slot.day} tiết {period}')
    for other_id, other_slot in assignment.items():
        if other_id == session_id or other_id not in sessions:
            continue
        other = sessions[other_id]
        if not overlap(session, slot, other, other_slot):
            continue
        if slot.room_id == other_slot.room_id:
            reasons.append(f'Trùng phòng {slot.room_id} với buổi {other_id}')
        if session.teacher_id == other.teacher_id:
            reasons.append(f'Trùng giảng viên {session.teacher_id} với buổi {other_id}')
        if session.group_id == other.group_id:
            reasons.append(f'Trùng nhóm {session.group_id} với buổi {other_id}')
    return reasons


def score(problem: Problem, assignment: dict[str, Slot]) -> dict[str, float]:
    errors = validate_schedule(problem, assignment)
    if errors:
        raise ValueError(f'Không chấm lịch sai: {errors}')
    late = gaps = pref = 0
    group_periods = {}
    for s in problem.sessions:
        slot = assignment[s.session_id]
        for p in range(slot.period, slot.period + s.duration):
            late += p > problem.periods_per_day - 2
            group_periods.setdefault((s.group_id, slot.day), set()).add(p)
            pref += problem.preferences.get((s.teacher_id, slot.day, p), 0)
    for occupied in group_periods.values():
        gaps += max(occupied) - min(occupied) + 1 - len(occupied)
    parts = {'late_periods': late, 'student_gaps': gaps, 'preference_penalty': pref}
    return {**parts, 'total': sum(problem.weights[k] * v for k, v in parts.items())}


def solve(problem: Problem, solver: str = 'enhanced', time_limit: float | None = None) -> dict:
    if solver not in ('baseline', 'enhanced'):
        raise ValueError('solver phải là baseline hoặc enhanced')
    limit = problem.time_limit_seconds if time_limit is None else time_limit
    if not math.isfinite(limit) or limit < 0:
        raise ValueError('time_limit phải hữu hạn và không âm')
    start = time.perf_counter()
    deadline = start + limit
    sessions = {s.session_id: s for s in problem.sessions}
    ids = list(sessions)
    domains = {}
    assignment = {}
    metrics = {'nodes': 0, 'backtracks': 0, 'pruned': 0, 'trace': []}
    neighbors = {}
    class TimedOut(Exception):
        pass

    def search():
        if time.perf_counter() >= deadline:
            raise TimedOut
        if len(assignment) == len(ids):
            return True
        unassigned = [sid for sid in ids if sid not in assignment]
        if solver == 'enhanced':
            sid = min(unassigned, key=lambda x: (len(domains[x]), -len(neighbors[x] & set(unassigned)), ids.index(x)))
        else:
            sid = unassigned[0]
        if len(metrics['trace']) < 20:
            metrics['trace'].append(f"Chọn {sid}: {len(domains[sid])} giá trị còn lại")
        for slot in list(domains[sid]):
            if time.perf_counter() >= deadline:
                raise TimedOut
            metrics['nodes'] += 1
            if any(conflict(sessions[sid], slot, sessions[other], other_slot) for other, other_slot in assignment.items()):
                continue
            assignment[sid] = slot
            removed = {}
            viable = True
            if solver == 'enhanced':
                for other in unassigned:
                    if other == sid or other not in neighbors[sid]:
                        continue
                    old = domains[other]
                    new = [candidate for candidate in old if not conflict(sessions[sid], slot, sessions[other], candidate)]
                    if len(new) != len(old):
                        removed[other] = old
                        domains[other] = new
                        metrics['pruned'] += len(old) - len(new)
                        if len(metrics['trace']) < 20:
                            example = next(candidate for candidate in old if conflict(sessions[sid], slot, sessions[other], candidate))
                            reasons = []
                            if slot.room_id == example.room_id:
                                reasons.append(f'phòng {slot.room_id}')
                            if sessions[sid].teacher_id == sessions[other].teacher_id:
                                reasons.append(f'giảng viên {sessions[sid].teacher_id}')
                            if sessions[sid].group_id == sessions[other].group_id:
                                reasons.append(f'nhóm {sessions[sid].group_id}')
                            metrics['trace'].append(
                                f"{sid}={slot.day}/{slot.period}/{slot.room_id}: loại {len(old)-len(new)} giá trị của {other}; "
                                f"ví dụ {example.day}/{example.period}/{example.room_id} trùng {', '.join(reasons)}")
                    if not new:
                        viable = False
                        if len(metrics['trace']) < 20:
                            metrics['trace'].append(f'Miền {other} rỗng sau khi gán {sid}')
                        break
            if viable and search():
                return True
            for other, old in removed.items():
                domains[other] = old
            del assignment[sid]
        metrics['backtracks'] += 1
        return False

    try:
        domains = {sid: domain(problem, sessions[sid], deadline) for sid in ids}
        possible_rooms = {}
        for sid in ids:
            if time.perf_counter() >= deadline:
                raise TimedOut
            possible_rooms[sid] = {slot.room_id for slot in domains[sid]}
        for a in ids:
            if time.perf_counter() >= deadline:
                raise TimedOut
            neighbors[a] = {b for b in ids if a != b and (
                sessions[a].teacher_id == sessions[b].teacher_id
                or sessions[a].group_id == sessions[b].group_id
                or bool(possible_rooms[a] & possible_rooms[b]))}
        found = search()
        status = 'FEASIBLE' if found else 'UNSAT'
    except (TimedOut, TimeoutError):
        status = 'TIMEOUT'
    elapsed = time.perf_counter() - start
    result = {'status': status, 'assignment': dict(assignment) if status == 'FEASIBLE' else None,
              'elapsed_seconds': elapsed, **metrics}
    if status == 'FEASIBLE':
        errors = validate_schedule(problem, result['assignment'])
        if errors:
            raise RuntimeError(f'Bộ giải tạo lịch sai: {errors}')
        result['score'] = score(problem, result['assignment'])
    return result


def export_csv(problem: Problem, assignment: dict[str, Slot]) -> str:
    errors = validate_schedule(problem, assignment)
    if errors:
        raise ValueError(f'Không thể xuất lịch sai: {errors}')
    out = io.StringIO()
    writer = csv.writer(out, lineterminator='\n')
    writer.writerow(('session_id', 'day', 'start_period', 'room_id'))
    for s in problem.sessions:
        slot = assignment[s.session_id]
        writer.writerow((s.session_id, slot.day, slot.period, slot.room_id))
    return out.getvalue()


def import_csv(text: str) -> dict[str, Slot]:
    result = {}
    for line, row in _csv_rows(text, 'schedule.csv', ('session_id', 'day', 'start_period', 'room_id')):
        sid = row['session_id']
        if sid in result:
            raise InputError(f'schedule.csv:{line} session_id: trùng')
        result[sid] = Slot(row['day'], _integer(row['start_period'], 'schedule.csv', line, 'start_period', 1), row['room_id'])
    return result


def improve_schedule(problem: Problem, assignment: dict[str, Slot],
                     time_limit: float = 2.0, max_passes: int = 10) -> dict:
    """Deterministic first-improvement local search over single-session moves."""
    if not math.isfinite(time_limit) or time_limit < 0 or max_passes < 0:
        raise ValueError('Giới hạn tối ưu không hợp lệ')
    if validate_schedule(problem, assignment):
        raise ValueError('Chỉ tối ưu lịch hợp lệ')
    current = dict(assignment)
    before = score(problem, current)
    best = before['total']
    deadline = time.perf_counter() + time_limit
    moves = 0
    for _ in range(max_passes):
        changed = False
        for session in problem.sessions:
            if time.perf_counter() >= deadline:
                break
            sid = session.session_id
            for slot in domain(problem, session):
                if time.perf_counter() >= deadline:
                    break
                if slot == current[sid]:
                    continue
                candidate = dict(current)
                candidate[sid] = slot
                if validate_schedule(problem, candidate):
                    continue
                cost = score(problem, candidate)['total']
                if cost < best:
                    current, best = candidate, cost
                    moves += 1
                    changed = True
                    break
            if changed:
                break
        if not changed:
            for index, a in enumerate(problem.sessions):
                if time.perf_counter() >= deadline:
                    break
                for b in problem.sessions[index + 1:]:
                    if time.perf_counter() >= deadline:
                        break
                    first, second = current[a.session_id], current[b.session_id]
                    candidate = dict(current)
                    candidate[a.session_id] = second
                    candidate[b.session_id] = first
                    if validate_schedule(problem, candidate):
                        continue
                    cost = score(problem, candidate)['total']
                    if cost < best:
                        current, best = candidate, cost
                        moves += 1
                        changed = True
                        break
                if changed:
                    break
        if not changed:
            break
    return {'assignment': current, 'before': before, 'after': score(problem, current), 'moves': moves}
