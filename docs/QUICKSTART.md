# Quickstart: small Type A geometry

## Requirements

- Python 3.9 or later and NumPy for construction.
- Optional: OVITO to inspect `CONFIG.A` or `initial-cores.dump`.
- Optional: LAMMPS with CORESHELL, KSPACE and CLASS2 for the initial-force check.

## Construct the preview

From the repository root, after installing NumPy:

```bash
python examples/type_a_preview.py
```

The script uses the byte-preserved Type A builder with repeats `(6, 6, 2)` rather than the archive's large repeats. It copies `CONFIG.IN`, `Param_KNO` and `check_type_a.in` to a new directory and writes `CONFIG.A`. It refuses to overwrite an existing directory; use `--output runs/another-preview` for a new run.

Observed construction: 1,320 particles, 660 ions/bonds, K:Nb:O = 1:1:3 and total charge numerically zero. Box lengths are approximately 33.55 x 33.55 x 7.91 Angstrom. This cell is too small for an isolated-dislocation benchmark.

## Optional initial-force check

```bash
cd runs/type-a-preview
lmp -in check_type_a.in -log check.log
```

Use your installed executable name, such as `lmp_serial`. This performs `run 0` only: read the structure and evaluate initial forces. No minimization, thermostat or dynamics occur. The no-time-integration warning is expected. Open `initial-cores.dump` in OVITO.

The small check uses `kspace_style ewald 1.0e-5`; the archived potential specifies PPPM. Ewald avoids an FFTW/PPPM cleanup crash observed with the local 22 Jul 2025 build. Force-field coefficients are unchanged. Do not transfer this solver choice or tiny cell to production without convergence checks.

## Recorded check

LAMMPS 22 Jul 2025: the Ewald initial-force check exited 0 and exported core coordinates. Initial potential energy was about -20379.745 eV and maximum atom-force norm about 63.365725 eV/Angstrom. These describe the unrelaxed preview, not a converged dislocation.

Construction, read-data and initial-force steps are checked. Relaxation, dipole topology, phase behavior, core-shell adiabaticity, mobility and finite-size limits remain open tasks. Follow [STATUS](STATUS.md) before attempting archive-sized calculations.

See the [LAMMPS core-shell guide](https://docs.lammps.org/Howto_coreshell.html) for paired charges/springs, `/cs` styles, `temp/cs` and pressure handling. A successful `run 0` alone does not validate dynamics.
