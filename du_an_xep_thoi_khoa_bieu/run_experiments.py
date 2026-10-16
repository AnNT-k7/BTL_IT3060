"""Reproduce the baseline vs MRV + forward-checking experiment."""

from __future__ import annotations

import csv
import datetime
import platform
from pathlib import Path
from tempfile import TemporaryDirectory

from generate_data import generate, generate_tight
from timetable_ai.core import load_directory, score, solve, validate_schedule


ROOT = Path(__file__).parent
OUTPUT = ROOT / 'results' / 'benchmark.csv'
FIELDS = ('case', 'seed', 'repeat', 'sessions', 'solver', 'status', 'elapsed_seconds',
          'nodes', 'backtracks', 'pruned', 'hard_violations', 'score',
          'python_version', 'platform', 'measured_at')


def main() -> None:
    rows = []
    measured_at = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')

    def measure(case, seed, repeat, problem, algorithm):
        result = solve(problem, algorithm, 10)
        assignment = result['assignment']
        violations = len(validate_schedule(problem, assignment)) if assignment else ''
        return {
            'case': case, 'seed': seed, 'repeat': repeat,
            'sessions': len(problem.sessions), 'solver': algorithm,
            'status': result['status'], 'elapsed_seconds': f"{result['elapsed_seconds']:.6f}",
            'nodes': result['nodes'], 'backtracks': result['backtracks'],
            'pruned': result['pruned'], 'hard_violations': violations,
            'score': score(problem, assignment)['total'] if assignment else '',
            'python_version': platform.python_version(), 'platform': platform.platform(),
            'measured_at': measured_at,
        }

    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        for name, groups, per_group in (('small', 3, 3), ('medium', 6, 4), ('large', 8, 5)):
            for seed in (3161, 3162, 3163):
                path = generate(f'{name}_{seed}', groups, per_group, seed=seed, root=root)
                problem = load_directory(path)
                for algorithm in ('baseline', 'enhanced'):
                    for repeat in range(1, 6):
                        rows.append(measure(name, seed, repeat, problem, algorithm))
        for name, gadgets in (('tight20', 5), ('tight40', 10)):
            for seed in (3161, 3162, 3163):
                path = generate_tight(f'{name}_{seed}', gadgets, seed=seed, root=root)
                problem = load_directory(path)
                for algorithm in ('baseline', 'enhanced'):
                    for repeat in range(1, 6):
                        rows.append(measure(name, seed, repeat, problem, algorithm))
    for name in ('backtracking', 'unsat'):
        problem = load_directory(ROOT / 'data' / name)
        for algorithm in ('baseline', 'enhanced'):
            for repeat in range(1, 6):
                rows.append(measure(name, '', repeat, problem, algorithm))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f'Wrote {len(rows)} measurements to {OUTPUT}')
    print(f'Python {platform.python_version()} / {platform.platform()}')
    for name in ('small', 'medium', 'large', 'tight20', 'tight40', 'backtracking', 'unsat'):
        for algorithm in ('baseline', 'enhanced'):
            selected = [row for row in rows if row['case'] == name and row['solver'] == algorithm]
            mean_ms = sum(float(row['elapsed_seconds']) for row in selected) / len(selected) * 1000
            print(name, algorithm, 'runs=', len(selected), 'status=', selected[0]['status'],
                  'mean_ms=', round(mean_ms, 3), 'mean_nodes=',
                  round(sum(int(row['nodes']) for row in selected) / len(selected), 1))


if __name__ == '__main__':
    main()
