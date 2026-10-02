#!/usr/bin/env python3
# =====================================================================
#  make_typeC.py
#  ---------------------------------------------------------------
#  Build a Type C mixed dislocation (dipole) in KNbO3 core-shell,
#  following Klomp, Porz & Albe, Acta Mater. 242 (2023) 118404.
#
#  Type C :  Burgers b = a<110> (mixed)
#              line   t = <111>
#              glide plane {1-10}
#              cell axes :  x = <1-10>,  y = <11-2>,  z = <111>
#
#  Input  : CONFIG.IN   (pseudo-cubic 1-f.u. core-shell unit cell)
#  Output : CONFIG.C   (LAMMPS data file, atom_style full, with bonds)
# =====================================================================
from builder_common import build

FRAME = dict(
    x = [1, -1, 0],
    y = [1, 1, -2],
    z = [1, 1, 1],          # = line vector t
    b = [1, 1, 0],          # a<110>
    char  = "mixed",
    glide = "{1-10}",
)
REPEATS = (66, 66, 3)        # (NX, NY, NZ)  -> ~392,040 ions

if __name__ == "__main__":
    build("C", FRAME, REPEATS, outfile="CONFIG.C")
