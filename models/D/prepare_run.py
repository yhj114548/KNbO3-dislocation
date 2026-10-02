#!/usr/bin/env python3
"""Check inputs and copy only current inputs to a fresh run folder. No submission."""
from datetime import datetime
from pathlib import Path
import json
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parent
subprocess.run([sys.executable, str(root / 'verify_inputs.py')], check=True)
meta = json.loads((root / 'input_fingerprints.json').read_text())
typ = meta['type']
dest = root / 'runs' / datetime.now().strftime('run_%Y%m%d_%H%M%S')
dest.mkdir(parents=True, exist_ok=False)
names = ['CONFIG.IN', 'CONFIG.' + typ, 'Param_KNO', 'IN_' + typ,
         'RELAX_' + typ + '.in', meta['defect_file'], 'job.pbs',
         'verify_inputs.py', 'input_fingerprints.json']
for name in names:
    shutil.copy2(root / name, dest / name)
print('\nPrepared current inputs at:', dest)
print('No simulation has been submitted or run.')
print('After changing into that directory, use your existing scheduler, or:')
print('mpirun -np N lmp -in IN_' + typ + ' -log log.corrected.lammps')
