#!/usr/bin/env python3
"""Rebuild a valid LAMMPS defect-group include from CONFIG.D.

Criterion unchanged: fewer nonbonded neighbors than the per-type modal
coordination within 2.85 Angstrom (2.85e-10 m). Core-shell partners are
excluded and every selected ion is expanded to its complete molecule.
This is a preparation restraint selector, not a Burgers-vector analysis
or evidence that either dislocation core is locally charge neutral.
"""
from pathlib import Path
from collections import Counter
import hashlib
import time
import numpy as np
from scipy.spatial import cKDTree

start = time.time()
path = Path('CONFIG.D')
box = np.zeros((3, 2))
sec = None
records = []
bonds = []
with path.open() as f:
    for ln in f:
        s = ln.strip()
        if not s or s.startswith('#'):
            continue
        found_box = False
        for axis, label in enumerate(('xlo xhi', 'ylo yhi', 'zlo zhi')):
            if s.endswith(label):
                box[axis] = list(map(float, s.split()[:2]))
                found_box = True
                break
        if found_box:
            continue
        if s.endswith('xy xz yz'):
            raise ValueError('This selector requires the orthogonal as-built CONFIG.D')
        if s == 'Masses': sec = 'M'; continue
        if s.startswith('Atoms'): sec = 'A'; continue
        if s == 'Bonds': sec = 'B'; continue
        if s == 'Velocities': sec = 'V'; continue
        fields = s.split()
        if not fields[0].isdigit():
            continue
        if sec == 'A':
            records.append([float(v) for v in fields[:7]])
        elif sec == 'B':
            bonds.append((int(fields[2]), int(fields[3])))

atoms = np.asarray(records)
del records
ids, mols, types = (atoms[:, j].astype(np.int64) for j in (0, 1, 2))
pos = atoms[:, 4:7]
if len(np.unique(ids)) != len(ids):
    raise ValueError('Duplicate atom IDs')
_, counts = np.unique(mols, return_counts=True)
if np.any(counts != 2):
    raise ValueError('Expected two particles per core-shell molecule')
id_to_index = np.full(int(ids.max()) + 1, -1, dtype=np.int64)
id_to_index[ids] = np.arange(len(ids))
bond_ids = np.asarray(bonds, dtype=np.int64)
if np.any(bond_ids < 1) or np.any(bond_ids > ids.max()):
    raise ValueError('Invalid bond endpoint ID')
bond_index = id_to_index[bond_ids]
if np.any(bond_index < 0):
    raise ValueError('Missing bond endpoint')
if np.any(np.bincount(bond_index.ravel(), minlength=len(ids)) != 1):
    raise ValueError('Expected exactly one core-shell bond per particle')
if np.any(mols[bond_index[:, 0]] != mols[bond_index[:, 1]]):
    raise ValueError('Bond endpoints have different molecule IDs')
if not np.all(np.sort(types[bond_index], axis=1)[:, 1] - np.sort(types[bond_index], axis=1)[:, 0] == 3):
    raise ValueError('Bond is not a same-species core-shell pair')

lengths = box[:, 1] - box[:, 0]
if np.any(lengths <= 0):
    raise ValueError('Invalid box dimensions')
wrapped = np.mod(pos - box[:, 0], lengths)
cutoff = 2.85  # 2.85e-10 m in the LAMMPS metal-unit data file
# Count lists in the tree directly; do not allocate millions of pair tuples.
tree = cKDTree(wrapped, boxsize=lengths)
degree = tree.query_ball_point(wrapped, cutoff, return_length=True, workers=-1) - 1
separation = wrapped[bond_index[:, 0]] - wrapped[bond_index[:, 1]]
separation -= np.rint(separation / lengths) * lengths
near_bonds = bond_index[np.linalg.norm(separation, axis=1) <= cutoff]
np.add.at(degree, near_bonds.ravel(), -1)
print(f'Parsed {len(ids)} particles / {len(bonds)} physical ions in {time.time() - start:.1f} s')
print(f'Nonbonded coordination cutoff: {cutoff * 1e-10:.8e} m')
selected = np.zeros(len(ids), dtype=bool)
for atom_type in sorted(np.unique(types)):
    mask = types == atom_type
    distribution = Counter(degree[mask].tolist())
    mode, nmode = distribution.most_common(1)[0]
    under = mask & (degree < mode)
    selected |= under
    print(f'Type {atom_type}: mode={mode}; under-coordinated={int(under.sum())}; distribution={sorted(distribution.items())}')
selected_mols = np.unique(mols[selected])
full_mask = np.isin(mols, selected_mols)
full_ids = ids[full_mask]
fingerprint = hashlib.sha256(path.read_bytes()).hexdigest()
out = Path('defect_group_D.txt')
with out.open('w') as f:
    f.write('# Regenerated from CONFIG.D by check_coord.py; rerun after rebuilding CONFIG.D.\n')
    f.write(f'# CONFIG.D SHA256: {fingerprint}\n')
    f.write('# Criterion: nonbonded coordination below per-type mode at 2.85e-10 m.\n')
    f.write(f'# Complete core-shell molecules: {len(selected_mols)} ions, {len(full_ids)} particles.\n')
    if len(full_ids):
        f.write('group defects id &\n')
        for first in range(0, len(full_ids), 12):
            block = full_ids[first:first + 12]
            continuation = ' &' if first + 12 < len(full_ids) else ''
            f.write('    ' + ' '.join(map(str, block)) + continuation + '\n')
    else:
        f.write('group defects empty\n')
print(f'Wrote {out}: {len(selected_mols)} ions / {len(full_ids)} particles')
if len(full_ids):
    print('Selected particle coordinate ranges (m):')
    for axis, label in enumerate(('x', 'y', 'z')):
        print(f'  {label}: {pos[full_mask, axis].min() * 1e-10:.8e} to {pos[full_mask, axis].max() * 1e-10:.8e}')
print(f'CONFIG.D SHA256: {fingerprint}')
