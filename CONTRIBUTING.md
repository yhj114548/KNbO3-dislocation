# Contributing

We are adapting the Type A-E dislocation framework studied in SrTiO3 to KNbO3 with a LAMMPS core-shell model. Read the [README](README.md), [quickstart](docs/QUICKSTART.md) and [status](docs/STATUS.md) first.

## Choose a task

Browse [open Issues](https://github.com/yhj114548/KNbO3-dislocation/issues). `good first issue` marks approachable documentation/visualization work; `help wanted` marks tasks needing contributors, sometimes with scientific expertise. Comment before starting a large change so work can be coordinated.

## Submit a change

1. Fork the repository and create a branch for one task.
2. Make a focused change. Preserve original archives as provenance.
3. Run relevant small checks and record exactly what was run.
4. Open a pull request linking the Issue. Explain behavior, evidence and scientific limitations.

The original builders generate hundreds of thousands of particles; start with the small preview in a fresh run directory.

## Scientific review

- Cite the source for changed force-field parameters or mass/spring conventions.
- Separate input consistency, initial-force evaluation, relaxation convergence and validated dislocation physics.
- Include LAMMPS version/build, packages, Python dependencies, commands, cell axes, boundaries, phase, temperature, timestep and random seed as applicable.
- Show Burgers circuits or equivalent evidence before claiming a core topology.
- Preserve charge neutrality and core-shell pairing checks; assess local charge and stoichiometry separately.
- Discuss finite-size dependence, thermostat/barostat choices and shell adiabaticity for production results.
- Explain changed fingerprints; do not update hashes solely to suppress a mismatch.
- Justify stabilizing restraints, altered charges or added repulsion as changes to the model.

## Results, credit and reuse

Keep source and small inputs reviewable. Discuss storage of large trajectories with the maintainer. Historical archive output must remain identifiable. Omit private cluster details and credentials from logs.

Credit publications, parameter sources and contributors. Cite this repository with `CITATION.cff`. A license has not yet been selected; discuss reuse before redistributing packages. A contribution alone does not establish a validated result.
