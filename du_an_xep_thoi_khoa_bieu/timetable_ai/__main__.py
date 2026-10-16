import argparse
import csv
import sys
from pathlib import Path

from .core import InputError, export_csv, load_directory, score, solve, validate_schedule


def main():
    parser = argparse.ArgumentParser(description='Xếp thời khóa biểu tuần bằng CSP')
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('solve', 'benchmark'):
        p = sub.add_parser(command)
        p.add_argument('--data', default='data/demo')
        p.add_argument('--time-limit', type=float)
        if command == 'solve':
            p.add_argument('--solver', choices=('baseline', 'enhanced'), default='enhanced')
            p.add_argument('--output', help='Đường dẫn CSV kết quả')
        else:
            p.add_argument('--output', help='Đường dẫn CSV số liệu')
    args = parser.parse_args()
    try:
        problem = load_directory(args.data)
        solvers = (args.solver,) if args.command == 'solve' else ('baseline', 'enhanced')
        rows = []
        exit_status = 0
        for solver in solvers:
            result = solve(problem, solver, args.time_limit)
            if args.command == 'solve':
                exit_status = {'FEASIBLE': 0, 'UNSAT': 3, 'TIMEOUT': 4}[result['status']]
            errors = validate_schedule(problem, result['assignment']) if result['assignment'] else []
            row = {'solver': solver, 'status': result['status'], 'elapsed_seconds': round(result['elapsed_seconds'], 6),
                   'nodes': result['nodes'], 'backtracks': result['backtracks'], 'pruned': result['pruned'],
                   'hard_violations': len(errors) if result['assignment'] else '',
                   'score': score(problem, result['assignment'])['total'] if result['assignment'] else ''}
            rows.append(row)
            print(row)
            if args.command == 'solve' and result['assignment']:
                content = export_csv(problem, result['assignment'])
                if args.output:
                    Path(args.output).write_text(content, encoding='utf-8')
                else:
                    print(content, end='')
        if args.command == 'benchmark' and args.output:
            with Path(args.output).open('w', encoding='utf-8', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
    except (InputError, ValueError) as exc:
        print(f'Lỗi dữ liệu: {exc}', file=sys.stderr)
        return 2
    return exit_status


if __name__ == '__main__':
    raise SystemExit(main())
