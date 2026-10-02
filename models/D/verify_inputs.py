#!/usr/bin/env python3
"""Read-only preflight for these corrected core-shell inputs; Python standard library.

Run inside the corrected B or D folder: python3 verify_inputs.py
Checks input integrity, not force convergence, adiabaticity or defect physics.
The geometry fingerprint deliberately rejects a different/regenerated structure
unless it is byte-identical, because the defect selection contains fixed atom IDs.
"""
from array import array
from collections import Counter
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
META = json.loads((ROOT / "input_fingerprints.json").read_text())
TYPE = META["type"]
DATA = "CONFIG." + TYPE
DEFECTS = META["defect_file"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_data(path, require_geometry=False):
    masses, counts, bounds = {}, Counter(), {}
    types, molecules, seen_bonds = None, None, None
    n, nb, atoms_read, bonds_read, charge_units = 0, 0, 0, 0, 0
    coords = None
    max_pair_distance_m = 0.0
    rounded_boundary_atoms = 0
    section = None
    expected_q = {1: 12394, 2: -29878, 3: 11236,
                  4: -4189, 5: 78265, 6: -30100}
    digest = hashlib.sha256()
    in_body = False
    with path.open('rb') as handle:
        for raw in handle:
            line = raw.decode().split('#', 1)[0].strip()
            if line == 'Atoms':
                in_body = True
            if in_body:
                digest.update(raw)
            if not line:
                continue
            if line in ('Masses', 'Atoms', 'Bonds'):
                section = line
                continue
            fields = line.split()
            if section is None:
                if len(fields) == 2 and fields[1] == 'atoms':
                    n = int(fields[0])
                    types = array('B', [0]) * (n + 1)
                    molecules = array('I', [0]) * (n + 1)
                    seen_bonds = bytearray(n + 1)
                    coords = array('d', [0.0]) * (3 * (n + 1))
                elif len(fields) == 2 and fields[1] == 'bonds':
                    nb = int(fields[0])
                elif len(fields) == 4 and fields[2] in ('xlo', 'ylo', 'zlo'):
                    bounds[fields[2][0]] = tuple(map(float, fields[:2]))
                continue
            if section == 'Masses':
                masses[int(fields[0])] = float(fields[1])
            elif section == 'Atoms':
                idx, mol, typ = map(int, fields[:3])
                require(0 < idx <= n and types[idx] == 0, 'Duplicate/out-of-range atom ID')
                require(typ in expected_q, 'Unexpected atom type')
                q = Decimal(fields[3]) * 10000
                require(q == expected_q[typ], f'Unexpected charge for atom {idx}')
                xyz = list(map(float, fields[4:7]))
                require(all(math.isfinite(v) for v in xyz), f'Nonfinite coordinate: {idx}')
                # Builder prints coordinates to 5 decimals, bounds to 6.
                # Permit half a coordinate rounding unit (5e-16 m);
                # read_data remaps these coincident pairs across periodic faces.
                require(all(bounds[axis][0] - 5.1e-6 <= value <= bounds[axis][1] + 5.1e-6
                            for axis, value in zip('xyz', xyz)), f'Out-of-box atom: {idx}')
                if any(not bounds[axis][0] <= value <= bounds[axis][1]
                       for axis, value in zip('xyz', xyz)):
                    rounded_boundary_atoms += 1
                types[idx], molecules[idx] = typ, mol
                coords[3 * idx:3 * idx + 3] = array('d', xyz)
                counts[typ] += 1
                charge_units += int(q)
                atoms_read += 1
            elif section == 'Bonds':
                bi, bt, i, j = map(int, fields)
                require(bi == bonds_read + 1, 'Nonsequential bond ID')
                require(0 < i <= n and 0 < j <= n, 'Out-of-range bonded atom')
                require(bt in (1, 2, 3) and {types[i], types[j]} == {bt, bt + 3},
                        f'Wrong core-shell bond mapping at bond {bi}')
                require(molecules[i] == molecules[j] != 0, f'Molecule mismatch: {bi}')
                require(not seen_bonds[i] and not seen_bonds[j], 'Atom bonded more than once')
                seen_bonds[i] = seen_bonds[j] = 1
                dsq = 0.0
                for k, axis in enumerate('xyz'):
                    length = bounds[axis][1] - bounds[axis][0]
                    delta = coords[3*i+k] - coords[3*j+k]
                    delta -= round(delta / length) * length
                    dsq += delta * delta
                max_pair_distance_m = max(max_pair_distance_m, math.sqrt(dsq) * 1e-10)
                bonds_read += 1
    require(atoms_read == n and bonds_read == nb, 'Header/record count mismatch')
    require(all(seen_bonds[1:]), 'An atom has no core-shell bond')
    require(len(set(molecules[1:])) == nb, 'Molecule IDs do not identify unique pairs')
    require(charge_units == 0, 'Nonzero total charge')
    require(counts[1] == counts[2] and counts[3] == 3 * counts[1], 'Wrong stoichiometry')
    for core, shell in ((1, 4), (2, 5), (3, 6)):
        require(counts[core] == counts[shell], 'Core/shell count mismatch')
        require(math.isclose(masses[shell] / masses[core], 0.1, rel_tol=0, abs_tol=1e-8),
                f'Shell/core mass ratio error: {core}/{shell}')
    expected_masses = {1: 35.544, 2: 84.460, 3: 14.545, 4: 3.5544, 5: 8.446, 6: 1.4545}
    require(masses == expected_masses, 'Masses differ from the corrected convention')
    fingerprint = digest.hexdigest()
    if require_geometry:
        manifest = json.loads((ROOT / 'input_fingerprints.json').read_text())
        require(hashlib.sha256(path.read_bytes()).hexdigest() == manifest['data_sha256'],
                'Simulation data changed, including its box/header: reassess inputs before running')
        require(fingerprint == manifest['atoms_bonds_sha256'],
                'Geometry/IDs changed: reassess and regenerate the defect selection first')
        require(hashlib.sha256((ROOT / DEFECTS).read_bytes()).hexdigest()
                == manifest['defect_sha256'], 'Defect selection changed')
    return {'atoms': n, 'ions': nb, 'counts_by_type': dict(counts),
            'total_charge_C': charge_units * 1e-4 * 1.602176634e-19,
            'box_lengths_m': {axis: (hi-lo)*1e-10 for axis, (lo, hi) in bounds.items()},
            'mass_kg_by_type': {k: v * 1.66053906660e-27 for k, v in masses.items()},
            'max_initial_core_shell_distance_m': max_pair_distance_m,
            'atoms_at_rounded_periodic_boundary': rounded_boundary_atoms,
            'atoms_bonds_sha256': fingerprint}, types, molecules


def main():
    unit, _, _ = read_data(ROOT / 'CONFIG.IN')
    require(hashlib.sha256((ROOT / 'Param_KNO').read_bytes()).hexdigest() == META['potential_sha256'],
            'Param_KNO changed from the verified source coefficients')
    config, types, molecules = read_data(ROOT / DATA, require_geometry=True)
    lines = [(x.split('#', 1)[0]).strip() for x in (ROOT / DEFECTS).read_text().splitlines()]
    tokens = ' '.join(lines).replace('&', ' ').split()
    require(tokens[:3] == ['group', 'defects', 'id'], 'Unexpected defect group command')
    ids = list(map(int, tokens[3:]))
    require(len(ids) == len(set(ids)) == META['selected_atoms'], 'Duplicate/wrong number of selected atoms')
    require(all(0 < idx < len(types) for idx in ids), 'Invalid selected atom ID')
    selected_pairs = Counter(molecules[idx] for idx in ids)
    require(all(n == 2 for n in selected_pairs.values()), 'Defect selection splits a core-shell pair')
    selected_cores = sum(types[idx] <= 3 for idx in ids)
    require(selected_cores == META['selected_cores'], 'Unexpected defect core count')
    print(json.dumps({'status': 'PASS_INPUT_CONSISTENCY_ONLY', 'CONFIG.IN': unit,
                      DATA: config, 'selected_defect_cores': selected_cores,
                      'verification_scope': 'input consistency; engine tests are reported separately',
                      'note': 'Does not certify minimization, adiabaticity, local charge or dislocation structure'},
                     indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
