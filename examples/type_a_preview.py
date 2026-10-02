#!/usr/bin/env python3
"""Build a small Type A geometry for inspection; does not relax or run MD."""
import argparse
import importlib.util
import os
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'runs' / 'type-a-preview')
    args = parser.parse_args()
    output = args.output.resolve()
    # A new directory prevents overwriting results from a previous inspection.
    output.mkdir(parents=True, exist_ok=False)
    source = ROOT / 'models' / 'A'
    for name in ('CONFIG.IN', 'Param_KNO'):
        shutil.copy2(source / name, output / name)
    shutil.copy2(ROOT / 'examples' / 'check_type_a.in', output / 'check_type_a.in')
    spec = importlib.util.spec_from_file_location('type_a_builder', source / 'builder_common.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    previous = Path.cwd()
    try:
        os.chdir(output)
        builder.build('A', dict(x=[1,-1,0], y=[1,1,0], z=[0,0,1], b=[1,1,0],
                               char='edge', glide='{1-10}'), (6,6,2), 'CONFIG.A')
    finally:
        os.chdir(previous)
    print('Geometry-only preview at:', output)
    print('Not a converged dislocation model or a finite-size benchmark.')
    print('Optional initial-force check: cd to this directory, then lmp -in check_type_a.in')


if __name__ == '__main__':
    main()
