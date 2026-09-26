"""Render a replicas-versus-load chart from real HPA observations."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path


def parse_rows(source: Path) -> list[tuple[datetime, float, int]]:
    with source.open(newline='', encoding='utf-8') as handle:
        reader = csv.DictReader(handle)
        expected = {'timestamp', 'offered_load', 'replicas'}
        if set(reader.fieldnames or []) != expected:
            raise ValueError('CSV header must be: timestamp,offered_load,replicas')
        rows = []
        for line, row in enumerate(reader, start=2):
            try:
                rows.append((datetime.fromisoformat(row['timestamp']), float(row['offered_load']), int(row['replicas'])))
            except (TypeError, ValueError) as exc:
                raise ValueError(f'invalid data at CSV line {line}') from exc
    if not rows:
        raise ValueError('CSV contains no measurements; collect a real HPA run first')
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_file', type=Path)
    parser.add_argument('--output', type=Path, default=Path('docs/evidence/hpa-replicas-vs-load.png'))
    args = parser.parse_args()

    rows = parse_rows(args.csv_file)
    import matplotlib.pyplot as plt

    times, loads, replicas = zip(*rows)
    figure, left_axis = plt.subplots(figsize=(10, 5))
    left_axis.plot(times, loads, color='#0f766e', marker='o', label='Offered load')
    left_axis.set_ylabel('Offered load (requests/second)', color='#0f766e')
    right_axis = left_axis.twinx()
    right_axis.step(times, replicas, where='post', color='#b45309', marker='s', label='Backend replicas')
    right_axis.set_ylabel('Backend replicas', color='#b45309')
    left_axis.set_xlabel('Timestamp')
    left_axis.set_title('CivicPulse HPA: replicas versus offered load')
    figure.autofmt_xdate()
    figure.tight_layout()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, dpi=160)
    print(f'wrote {args.output}')


if __name__ == '__main__':
    main()
