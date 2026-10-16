import unittest
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

from generate_data import generate_tight

from timetable_ai.core import (
    InputError, Slot, explain_slot, export_csv, import_csv, improve_schedule, load_directory,
    load_text, score, solve, validate_schedule,
)


DATA = Path(__file__).resolve().parents[1] / 'data'


class TimetableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.problem = load_directory(DATA / 'demo')

    def test_both_solvers_produce_independently_valid_schedules(self):
        for name in ('baseline', 'enhanced'):
            with self.subTest(solver=name):
                result = solve(self.problem, name, 10)
                self.assertEqual(result['status'], 'FEASIBLE')
                self.assertEqual(validate_schedule(self.problem, result['assignment']), [])
        enhanced = solve(self.problem, 'enhanced', 10)
        self.assertGreater(enhanced['pruned'], 0)

    def test_proven_unsat_and_timeout_are_distinct(self):
        impossible = load_directory(DATA / 'unsat')
        self.assertEqual(solve(impossible, 'enhanced', 10)['status'], 'UNSAT')
        self.assertEqual(solve(self.problem, 'enhanced', 0)['status'], 'TIMEOUT')

    def test_mrv_avoids_a_baseline_backtrack(self):
        problem = load_directory(DATA / 'backtracking')
        baseline = solve(problem, 'baseline', 10)
        enhanced = solve(problem, 'enhanced', 10)
        self.assertEqual(baseline['status'], 'FEASIBLE')
        self.assertEqual(enhanced['status'], 'FEASIBLE')
        self.assertGreater(baseline['backtracks'], enhanced['backtracks'])
        self.assertEqual(validate_schedule(problem, enhanced['assignment']), [])

    def test_tight_twenty_session_instance_is_solvable_with_pruning(self):
        with TemporaryDirectory() as directory:
            path = generate_tight('tight', 5, seed=3161, root=Path(directory))
            problem = load_directory(path)
            baseline = solve(problem, 'baseline', 10)
            enhanced = solve(problem, 'enhanced', 10)
            self.assertEqual(baseline['status'], 'FEASIBLE')
            self.assertEqual(enhanced['status'], 'FEASIBLE')
            self.assertGreater(baseline['backtracks'], enhanced['backtracks'])
            self.assertEqual(validate_schedule(problem, enhanced['assignment']), [])

    def test_enhanced_restores_domains_after_backtracking(self):
        from timetable_ai.core import Problem, Room, Session
        sessions = [Session(name, name, name, name, 10, 1, 'normal') for name in 'ABCD']
        allowed = {'A': (1, 2), 'B': (1, 3), 'C': (1, 3), 'D': (3, 4)}
        availability = {(name, 'T2', period): period in periods
                        for name, periods in allowed.items() for period in range(1, 5)}
        problem = Problem(sessions, [Room('P', 20, 'normal')], ['T2'], 4,
                          availability, {}, self.problem.weights, 10)
        result = solve(problem, 'enhanced', 10)
        self.assertEqual(result['status'], 'FEASIBLE')
        self.assertGreater(result['backtracks'], 0)
        self.assertEqual(validate_schedule(problem, result['assignment']), [])

    def test_export_round_trip(self):
        result = solve(self.problem, 'enhanced', 10)
        text = export_csv(self.problem, result['assignment'])
        reloaded = import_csv(text)
        self.assertEqual(reloaded, result['assignment'])
        self.assertEqual(validate_schedule(self.problem, reloaded), [])

    def test_explain_proposed_slot_names_the_conflict(self):
        assignment = solve(self.problem, 'enhanced', 10)['assignment']
        a, b = self.problem.sessions[:2]
        self.assertEqual(explain_slot(self.problem, assignment, a.session_id, assignment[a.session_id]), [])
        reasons = explain_slot(self.problem, assignment, a.session_id, assignment[b.session_id])
        self.assertTrue(any('Trùng phòng' in reason and b.session_id in reason for reason in reasons))

    def test_checker_catches_room_teacher_group_capacity_and_missing(self):
        problem = self.problem
        assignment = solve(problem, 'enhanced', 10)['assignment']
        a = problem.sessions[0]
        b = next(s for s in problem.sessions if s.session_id != a.session_id and s.group_id == a.group_id)
        same = dict(assignment)
        same[b.session_id] = assignment[a.session_id]
        errors = validate_schedule(problem, same)
        self.assertTrue(any(x.startswith('room_conflict:') for x in errors))
        self.assertTrue(any(x.startswith('group_conflict:') for x in errors))
        teacher_peer = next(s for s in problem.sessions if s.session_id != a.session_id and s.teacher_id == a.teacher_id)
        other_room = next(r.room_id for r in problem.rooms if r.room_id != assignment[a.session_id].room_id)
        teacher_collision = dict(assignment)
        teacher_collision[teacher_peer.session_id] = Slot(assignment[a.session_id].day,
                                                           assignment[a.session_id].period, other_room)
        self.assertTrue(any(x.startswith('teacher_conflict:') for x in validate_schedule(problem, teacher_collision)))
        missing = dict(assignment)
        del missing[a.session_id]
        self.assertIn(f'missing:{a.session_id}', validate_schedule(problem, missing))
        used_room = assignment[a.session_id].room_id
        altered = replace(problem, rooms=[replace(r, capacity=1) if r.room_id == used_room else r
                                          for r in problem.rooms])
        self.assertIn(f'room:{a.session_id}', validate_schedule(altered, assignment))

    def test_input_errors_have_file_and_line(self):
        folder = DATA / 'demo'
        names = ('sessions.csv', 'rooms.csv', 'availability.csv', 'preferences.csv', 'config.json')
        files = {name: (folder / name).read_text(encoding='utf-8') for name in names}
        files['availability.csv'] = files['availability.csv'].replace('GV01,T2,1,true', 'UNKNOWN,T2,1,true')
        with self.assertRaisesRegex(InputError, r'availability.csv:2'):
            load_text(files)
        files['availability.csv'] = (folder / 'availability.csv').read_text(encoding='utf-8')
        files['rooms.csv'] = files['rooms.csv'].replace(',60,normal', ',1,normal')
        with self.assertRaisesRegex(InputError, r'sessions.csv:2 size/room_type'):
            load_text(files)

    def test_malformed_headers_rows_and_days_are_input_errors(self):
        folder = DATA / 'demo'
        names = ('sessions.csv', 'rooms.csv', 'availability.csv', 'config.json')
        files = {name: (folder / name).read_text(encoding='utf-8') for name in names}
        files['rooms.csv'] = files['rooms.csv'].replace('room_id,capacity,room_type', 'room_id,capacity,room_type,extra')
        with self.assertRaisesRegex(InputError, 'rooms.csv:2'):
            load_text(files)
        files['rooms.csv'] = (folder / 'rooms.csv').read_text(encoding='utf-8').replace(
            'room_id,capacity,room_type', 'room_id,capacity,room_type,room_id')
        with self.assertRaisesRegex(InputError, 'tên cột bị trùng'):
            load_text(files)
        files['rooms.csv'] = (folder / 'rooms.csv').read_text(encoding='utf-8')
        files['config.json'] = '{"days": [[]], "periods_per_day": 6}'
        with self.assertRaisesRegex(InputError, 'days'):
            load_text(files)

    def test_export_rejects_unavailable_second_period(self):
        assignment = solve(self.problem, 'enhanced', 10)['assignment']
        session = self.problem.sessions[0]
        slot = assignment[session.session_id]
        altered_availability = dict(self.problem.availability)
        altered_availability[(session.teacher_id, slot.day, slot.period + 1)] = False
        altered = replace(self.problem, availability=altered_availability)
        self.assertIn(f'availability:{session.session_id}', validate_schedule(altered, assignment))
        with self.assertRaisesRegex(ValueError, 'Không thể xuất lịch sai'):
            export_csv(altered, assignment)

    def test_cli_non_solution_exit_codes(self):
        root = DATA.parent
        unsat = subprocess.run([sys.executable, '-m', 'timetable_ai', 'solve', '--data', 'data/unsat'],
                               cwd=root, capture_output=True, text=True)
        timeout = subprocess.run([sys.executable, '-m', 'timetable_ai', 'solve', '--data', 'data/demo',
                                  '--time-limit', '0'], cwd=root, capture_output=True, text=True)
        self.assertEqual(unsat.returncode, 3)
        self.assertEqual(timeout.returncode, 4)

    def test_nonfinite_time_limit_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'hữu hạn'):
            solve(self.problem, 'enhanced', float('nan'))

    def test_improvement_preserves_constraints_and_never_increases_cost(self):
        original = solve(self.problem, 'enhanced', 10)['assignment']
        improved = improve_schedule(self.problem, original, time_limit=2)
        self.assertEqual(validate_schedule(self.problem, improved['assignment']), [])
        self.assertLessEqual(improved['after']['total'], improved['before']['total'])
        self.assertEqual(improved['before'], score(self.problem, original))

    def test_swap_can_improve_when_single_moves_cannot(self):
        from timetable_ai.core import Problem, Room, Session
        sessions = [Session(name, name, name, name, 10, 1, 'normal') for name in 'AB']
        availability = {(name, 'T2', period): True for name in 'AB' for period in (1, 2)}
        preferences = {('A', 'T2', 1): 1, ('B', 'T2', 2): 1}
        problem = Problem(sessions, [Room('P', 20, 'normal')], ['T2'], 2,
                          availability, preferences,
                          {'late_periods': 0, 'student_gaps': 0, 'preference_penalty': 1}, 10)
        initial = {'A': Slot('T2', 1, 'P'), 'B': Slot('T2', 2, 'P')}
        result = improve_schedule(problem, initial, time_limit=1)
        self.assertEqual(result['before']['total'], 2)
        self.assertEqual(result['after']['total'], 0)
        self.assertEqual(validate_schedule(problem, result['assignment']), [])


if __name__ == '__main__':
    unittest.main()
