#!/usr/bin/env python3
# =====================================================================
#  make_typeE.py
#  ---------------------------------------------------------------
#  Build a Type E mixed dislocation (dipole) in KNbO3 core-shell,
#  following Klomp, Porz & Albe, Acta Mater. 242 (2023) 118404.
#
#  Type E :  Burgers b = a<110> (mixed)
#              line   t = <100>
#              glide plane {001}
#              cell axes :  x = <010>,  y = <001>,  z = <100>
#
#  Input  : CONFIG.IN   (pseudo-cubic 1-f.u. core-shell unit cell)
#  Output : CONFIG.E   (LAMMPS data file, atom_style full, with bonds)
# =====================================================================
from builder_common import build

FRAME = dict(
    x = [0, 1, 0],
    y = [0, 0, 1],
    z = [1, 0, 0],          # = line vector t
    b = [1, 1, 0],          # a<110>
    char  = "mixed",
    glide = "{001}",
)
REPEATS = (106, 106, 7)        # (NX, NY, NZ)  -> ~393,260 ions

if __name__ == "__main__":
    build("E", FRAME, REPEATS, outfile="CONFIG.E")
