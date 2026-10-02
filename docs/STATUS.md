# Status and evidence

Audit of archives at base commit `15eb003`. Evidence refers to delivered files and a small local check, not an independently converged production study.

| Package | Observed evidence | Next task |
| --- | --- | --- |
| A | Status ends `FAIL stage_4; MD NOT STARTED`; `CONFIG.A` absent from A.zip | Verify geometry and diagnose force convergence |
| B | 13 small entries contain only `0xFF`; no corrected relaxation/MD result recorded | Recover source/metadata from a known-good copy |
| C | Status ends `FAIL stage_2; MD NOT STARTED` | Verify local chemistry and static relaxation |
| D | Status reports `FAIL shells_fixed_cores`; D.zip omits `CONFIG.D` despite its README | Regenerate/verify structure and defect IDs |
| E | Older stabilization protocol and historical output | Review altered charges/restraints/repulsion and establish a physical baseline |
| 20260205 | Unit-cell input/potential and historical outputs | Verify potential provenance, phase and units |

## Archive audit

`archive-audit.json` records archive SHA-256 hashes, copied entries and byte hashes, missing generated structures and unreadable small text entries. 58 small UTF-8 source/input/status files were extracted without changing bytes. Unreadable entries, macOS metadata, scheduler files and large generated data were excluded from review folders. Original archives remain available.

CRC success verifies stored bytes, not scientific validity or meaningful text. B's invalid entries have valid CRCs but unusable contents. No source recovery is claimed.

## Small Type A check

- Supplied builder with `(6, 6, 2)`: 1,320 particles and 660 core-shell pairs.
- Total charge numerically zero; O/K ratio 3.
- LAMMPS 22 Jul 2025 with Ewald `1e-5`: `run 0` exits 0 and exports core coordinates.
- Initial-force norm about 63.37 eV/Angstrom: unrelaxed construction.
- Local PPPM evaluation produced an FFTW cleanup segmentation fault; not recorded as a successful run.

This demonstrates construction and input readability, not Burgers-circuit verification, stable phase, relaxed cores, dissociation or validated force fields. No full production simulation was run for the contribution setup.

## Large data

`models/*` are review copies, not complete replacement packages. A/C need generated CONFIG data; B needs recovery; D needs regenerated data and verified defect selections; E's configuration remains in its archive. Use fresh run directories and respect manifests. Do not hide a mismatch by simply changing hashes.
