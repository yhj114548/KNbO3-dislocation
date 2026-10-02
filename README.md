# KNbO3 Dislocation Simulations with a Core-Shell Model

This project develops LAMMPS models of Type A-E dislocations in potassium niobate (KNbO3) using a core-shell interatomic model.

The dislocation classification and simulation strategy are inspired by Klomp, Porz, and Albe's atomistic study of Type A-E dislocations in SrTiO3. The goal here is to transfer that framework to KNbO3 and investigate how a polarizable core-shell description affects dislocation-core structure, dissociation, stability, and mobility.

## Research goals

- Build reproducible KNbO3 structures for Type A, B, C, D, and E dislocations.
- Implement the simulations in LAMMPS with a KNbO3 core-shell potential.
- Relax and compare the five dislocation-core configurations.
- Examine glide or climb dissociation where applicable.
- Evaluate the effects of polarization, core charge, temperature, and applied stress.
- Compare the KNbO3 results with the SrTiO3 behavior reported in the reference paper.

## Scientific background

The reference study models five prominent dislocation types in cubic SrTiO3. It reports that Types A-C share a {1-10} glide plane and can exhibit glide dissociation, whereas Types D and E have different glide planes and substantially higher barriers to motion. Because KNbO3 is ferroelectric and strongly polarizable, a core-shell model may reveal behavior that is not captured by the fixed-effective-charge model used for SrTiO3.

This repository treats the SrTiO3 results as a structural and methodological reference, not as an assumption that KNbO3 will behave identically.

## Repository contents

- `20260205-KNO_ts_0.001_tri (copy).zip`: reference KNbO3 core-shell LAMMPS model
- `A.zip`: Type A dislocation model
- `B.zip`: Type B dislocation model
- `C.zip`: Type C dislocation model
- `D.zip`: Type D dislocation model
- `E (copy).zip`: Type E dislocation model
- `2023-ActaMater-Klomp.pdf`: reference paper

The files are currently distributed as archives. A planned next step is to unpack them into documented directories so that inputs, structures, and analysis scripts can be reviewed and improved directly on GitHub.

## How to contribute

Contributions are welcome from researchers and developers working on LAMMPS, core-shell potentials, ferroelectric perovskites, atomistic dislocation modeling, and visualization.

Useful contributions include:

- checking the crystallographic construction of Types A-E;
- validating the KNbO3 core-shell parameters and LAMMPS settings;
- improving relaxation and loading protocols;
- checking charge neutrality and core-shell initialization;
- adding OVITO or Python analysis workflows;
- calculating dislocation energies, dissociation distances, and Peierls stresses;
- documenting reproducible runs and comparing the five configurations.

Please open an Issue to discuss a proposed change or a Pull Request with a focused improvement. When reporting results, include the LAMMPS version, potential parameters, boundary conditions, temperature, timestep, minimization or thermostat settings, and the exact input files used.

## Project status

This is an early-stage research repository. The Type A-E input sets are under development and still require systematic validation. Results should not yet be treated as benchmark data.

## Reference

A. J. Klomp, L. Porz, and K. Albe, "The nature and motion of deformation-induced dislocations in SrTiO3: Insights from atomistic simulations," *Acta Materialia* 242 (2023) 118404. https://doi.org/10.1016/j.actamat.2022.118404

## License and citation

A project license and `CITATION.cff` file will be added before the repository is presented as a reusable research package. Until then, please contact the repository owner before reusing unpublished KNbO3 model files or results.
