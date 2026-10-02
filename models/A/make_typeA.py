#!/usr/bin/env python3
# =====================================================================
#  make_typeA.py
#  ---------------------------------------------------------------
#  Build a Type A edge dislocation (dipole) in KNbO3 core-shell,
#  following Klomp, Porz & Albe, Acta Mater. 242 (2023) 118404.
#
#  Type A :  Burgers b = a<110> (edge)
#              line   t = <001>
#              glide plane {1-10}
#              cell axes :  x = <1-10>,  y = <110>,  z = <001>
#
#  Input  : CONFIG.IN   (pseudo-cubic 1-f.u. core-shell unit cell)
#  Output : CONFIG.A   (LAMMPS data file, atom_style full, with bonds)
# =====================================================================
from builder_common import build

FRAME = dict(
    x = [1, -1, 0],
    y = [1, 1, 0],
    z = [0, 0, 1],          # = line vector t
    b = [1, 1, 0],          # a<110>
    char  = "edge",
    glide = "{1-10}",
)
REPEATS = (81, 81, 6)        # (NX, NY, NZ)  -> ~391,230 ions

if __name__ == "__main__":
    build("A", FRAME, REPEATS, outfile="CONFIG.A")
