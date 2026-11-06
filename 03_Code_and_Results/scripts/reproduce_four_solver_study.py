"""Reproduce all recorded numerical studies into a new directory.

This runs real fits; plotting and manuscript generation are separate commands.
Use Python from the environment containing requirements-admm.txt.
"""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, help='New result root, relative to the code directory')
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    if output.exists():
        parser.error(f'Refusing to overwrite an existing study: {output}')
    output.mkdir(parents=True)
    commands = [
        ['run_experiments.py', '--output', str(output / 'main')],
        ['run_extended_experiments.py', '--output', str(output / 'extended')],
        ['run_admm_sensitivity.py', '--output', str(output / 'sensitivity'),
         '--extended-inputs', str(output / 'extended' / 'inputs')],
    ]
    for script, *arguments in commands:
        subprocess.run([sys.executable, str(ROOT / 'scripts' / script), *arguments],
                       cwd=ROOT, check=True)
    print(f'Completed numerical study: {output}', flush=True)
    print('Plot with scripts/plot_four_solver_results.py --results <that directory>.')


if __name__ == '__main__':
    main()
