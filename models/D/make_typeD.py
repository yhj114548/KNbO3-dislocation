#!/usr/bin/env python3
# =====================================================================
#  make_typeD.py
#  ---------------------------------------------------------------
#  Build a Type D edge dislocation (dipole) in KNbO3 core-shell,
#  following Klomp, Porz & Albe, Acta Mater. 242 (2023) 118404.
#
#  Type D :  Burgers b = a<110> (edge)
#              line   t = <1-11>
#              glide plane {1-1-2}
#              cell axes :  x = <1-1-2>,  y = <110>,  z = <1-11>
#
#  Input  : CONFIG.IN   (pseudo-cubic 1-f.u. core-shell unit cell)
#  Output : CONFIG.D   (LAMMPS data file, atom_style full, with bonds)
# =====================================================================
from builder_common import build

FRAME = dict(
    x = [1, -1, -2],
    y = [1, 1, 0],          # edge Burgers component / ribbon thickness
    z = [1, -1, 1],          # = line vector t
    b = [1, 1, 0],          # a<110>
    char  = "edge",
    glide = "{1-1-2}",
)
# x/y are exchanged from the original builder so that the frame is right-
# handed and the edge component lies along y, as in Klomp Sec.2.2/Table 1.
# The physical Burgers vector and line direction are unchanged. This is a
# cubic-symmetry-equivalent orientation of the paper's Type D construction.
REPEATS = (66, 66, 3)        # (NX, NY, NZ); 389,070 ions after the ribbon cut

if __name__ == "__main__":
    build("D", FRAME, REPEATS, outfile="CONFIG.D")
