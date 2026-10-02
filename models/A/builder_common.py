#!/usr/bin/env python3
# =====================================================================
#  builder_common.py
#  ---------------------------------------------------------------
#  Shared logic for building KNbO3 core-shell dislocation dipoles,
#  types A-E, following Klomp, Porz & Albe, Acta Mater. 242 (2023) 118404.
#  Imported by make_typeA.py / make_typeB.py / make_typeC.py /
#  make_typeD.py / make_typeE.py  -- each just sets TYPE, FRAME, REPEATS
#  and calls build().
#
#  All types use a<110> family Burgers vectors. This delivery includes only
#  A and C. In Table 1 their plane normal is x; their edge component is y.
#  A: b=[110], t=[001] (edge); C: b=[110], t=[111] (mixed).
#  This is a KNbO3 adaptation, not a reproduction of the SrTiO3 force field.
#  Global stoichiometry is enforced below; local core charge and Burgers
#  circuits still require structural verification after relaxation.
# =====================================================================
import numpy as np

UNITCELL = "CONFIG.IN"


def read_unitcell(path):
    lines = open(path).read().splitlines()
    box = np.zeros((3, 2)); masses = {}; atoms = []
    sec = None
    for ln in lines:
        s = ln.strip()
        if s.endswith("xlo xhi"): box[0] = list(map(float, s.split()[:2]))
        elif s.endswith("ylo yhi"): box[1] = list(map(float, s.split()[:2]))
        elif s.endswith("zlo zhi"): box[2] = list(map(float, s.split()[:2]))
        elif s == "Masses": sec = "M"; continue
        elif s.startswith("Atoms"): sec = "A"; continue
        elif s == "Bonds": sec = "B"; continue
        elif s == "Velocities": sec = None; continue
        if not s: continue
        p = s.replace("\t", " ").split()
        if sec == "M" and p[0].isdigit() and len(p) >= 2:
            masses[int(p[0])] = float(p[1])
        elif sec == "A" and p[0].isdigit():
            atoms.append((int(p[0]), int(p[1]), int(p[2]),
                          float(p[3]), float(p[4]), float(p[5]), float(p[6])))
    a = box[0, 1] - box[0, 0]
    return a, masses, atoms


def build(type_label, frame, repeats, outfile):
    """
    type_label : 'A'..'E'
    frame      : dict(x=[..], y=[..], z=[..], b=[..], char=str, glide=str)
    repeats    : (NX, NY, NZ)
    outfile    : output LAMMPS data file name
    """
    a, MASSES, UC_ATOMS = read_unitcell(UNITCELL)
    for core, shell in ((1,4),(2,5),(3,6)):
        if not np.isclose(MASSES[shell]/MASSES[core], 0.1, rtol=0, atol=1e-8):
            raise ValueError("Check CONFIG.IN: shell/core mass ratio must be 0.1")
    NX, NY, NZ = repeats

    base = np.array([[at[4], at[5], at[6]] for at in UC_ATOMS]) / a
    btype = np.array([at[2] for at in UC_ATOMS])
    bq = np.array([at[3] for at in UC_ATOMS])
    bmol = np.array([at[1] for at in UC_ATOMS])
    nbase = len(base)

    partner = {}
    for i in range(nbase):
        for j in range(nbase):
            if i != j and bmol[i] == bmol[j]:
                partner[i] = j
    assert len(partner) == nbase, "core-shell pairing failed"

    XDIR = np.array(frame['x'], float)
    YDIR = np.array(frame['y'], float)
    ZDIR = np.array(frame['z'], float)
    assert abs(np.dot(XDIR, YDIR)) < 1e-9
    assert abs(np.dot(YDIR, ZDIR)) < 1e-9
    assert abs(np.dot(XDIR, ZDIR)) < 1e-9

    ex = XDIR / np.linalg.norm(XDIR)
    ey = YDIR / np.linalg.norm(YDIR)
    ez = ZDIR / np.linalg.norm(ZDIR)
    R = np.vstack([ex, ey, ez])

    Lx = a * np.linalg.norm(XDIR) * NX
    Ly = a * np.linalg.norm(YDIR) * NY
    Lz = a * np.linalg.norm(ZDIR) * NZ
    box = np.array([Lx, Ly, Lz])

    corners = np.array([[X, Y, Z] for X in (0, Lx) for Y in (0, Ly) for Z in (0, Lz)])
    cub = (R.T @ corners.T).T / a
    lo = np.floor(cub.min(0)).astype(int) - 1
    hi = np.ceil(cub.max(0)).astype(int) + 1

    ii = np.arange(lo[0], hi[0] + 1)
    jj = np.arange(lo[1], hi[1] + 1)
    kk = np.arange(lo[2], hi[2] + 1)
    I, J, K = np.meshgrid(ii, jj, kk, indexing="ij")
    shifts = np.stack([I.ravel(), J.ravel(), K.ravel()], 1).astype(float)
    ncell = len(shifts)

    pos = (shifts[:, None, :] + base[None, :, :]) * a
    pos = pos.reshape(-1, 3) @ R.T
    typ = np.tile(btype, ncell)
    qs = np.tile(bq, ncell)
    cellidx = np.repeat(np.arange(ncell), nbase)
    siteidx = np.tile(np.arange(nbase), ncell)
    sid = cellidx * nbase + siteidx
    pid = cellidx * nbase + np.tile([partner[s] for s in range(nbase)], ncell)

    tol = 1e-4
    inside = np.all((pos > -tol) & (pos < box - tol), 1)
    inflag = np.zeros(sid.max() + 1, bool); inflag[sid[inside]] = True
    keep = inflag[sid] & inflag[pid]
    pos, typ, qs, sid, pid = pos[keep], typ[keep], qs[keep], sid[keep], pid[keep]

    # ---------- insert the dislocation dipole ----------
    b_cell = R @ (np.array(frame['b'], float) * a)
    bx, by, bz = b_cell
    y_line = Ly / 2.0
    x1, x2 = Lx / 4.0, 3 * Lx / 4.0

    id2loc = {s: i for i, s in enumerate(sid)}

    # edge component: remove a one-Burgers-thick ribbon between the two cores
    edge_mag = np.hypot(bx, by)
    if edge_mag > 1e-6:
        sel = ((pos[:, 0] > x1) & (pos[:, 0] < x2) &
               (pos[:, 1] > y_line) & (pos[:, 1] < y_line + edge_mag))
        delmask = sel.copy()
        for idx in np.where(sel)[0]:
            p = pid[idx]
            if p in id2loc:
                delmask[id2loc[p]] = True
        kp = ~delmask
        pos, typ, qs, sid, pid = pos[kp], typ[kp], qs[kp], sid[kp], pid[kp]

    # screw component: analytical displacement field for a dipole
    if abs(bz) > 1e-6:
        dx1 = pos[:, 0] - x1; dy1 = pos[:, 1] - y_line
        dx2 = pos[:, 0] - x2; dy2 = pos[:, 1] - y_line
        theta = np.arctan2(dy1, dx1) - np.arctan2(dy2, dx2)
        pos[:, 2] += (bz / (2 * np.pi)) * theta
        pos[:, 2] = np.mod(pos[:, 2], Lz)

    # ---------- restore stoichiometry K:Nb:O = 1:1:3 (=> charge neutral) ----------
    id2loc = {s: i for i, s in enumerate(sid)}
    core_of = {1: 'K', 2: 'Nb', 3: 'O'}
    nK = (typ == 1).sum(); nNb = (typ == 2).sum(); nO = (typ == 3).sum()
    nfu = min(nK, nNb, nO // 3)
    excess = {'K': nK - nfu, 'Nb': nNb - nfu, 'O': nO - 3 * nfu}
    deln = set()
    for ct, sp in core_of.items():
        need = excess[sp]
        if need <= 0: continue
        ci = np.where(typ == ct)[0]
        order = ci[np.argsort(np.abs(pos[ci, 0] - x1))]
        r = 0
        for c in order:
            if r >= need: break
            if c in deln: continue
            p = pid[c]
            if p in id2loc:
                deln.add(c); deln.add(id2loc[p]); r += 1
    mask = np.ones(len(pos), bool)
    for i in deln: mask[i] = False
    pos, typ, qs, sid, pid = pos[mask], typ[mask], qs[mask], sid[mask], pid[mask]

    # ---------- rebuild bonds & molecule ids ----------
    id2loc = {s: i for i, s in enumerate(sid)}
    bondtype_of = {1: 1, 2: 2, 3: 3}
    bonds = []; mol = np.zeros(len(pos), int); seen = set(); mid = 0
    for i, s in enumerate(sid):
        p = pid[i]
        if p not in id2loc: continue
        key = tuple(sorted((s, p)))
        if key in seen: continue
        seen.add(key); mid += 1
        j = id2loc[p]
        c, sh = (i, j) if typ[i] in bondtype_of else (j, i)
        bonds.append((bondtype_of[typ[c]], c, sh))
        mol[i] = mid; mol[j] = mid

    Qtot = qs.sum()
    nK = (typ == 1).sum(); nO = (typ == 3).sum()
    print(f"Type {type_label} [{frame['char']}, glide {frame['glide']}]: "
          f"{len(pos)} atoms ({len(pos)//2} ions), {len(bonds)} bonds")
    print(f"        box = {Lx:.2f} x {Ly:.2f} x {Lz:.2f} A")
    print(f"        Q = {Qtot:+.4f} e,  O/K = {nO/nK:.3f}")

    with open(outfile, "w") as f:
        f.write(f"LAMMPS KNbO3 Type {type_label} dislocation "
                f"(b=a<110>, {frame['char']}, glide {frame['glide']})\n\n")
        f.write(f"{len(pos)} atoms\n{len(bonds)} bonds\n")
        f.write("6 atom types\n3 bond types\n\n")
        f.write(f"-0.0001 {Lx:.6f} xlo xhi\n")
        f.write(f"-0.0001 {Ly:.6f} ylo yhi\n")
        f.write(f"-0.0001 {Lz:.6f} zlo zhi\n\n")
        f.write("Masses\n\n")
        labels = {1: "K_core", 2: "Nb_core", 3: "O_core",
                  4: "K_shell", 5: "Nb_shell", 6: "O_shell"}
        for t in range(1, 7):
            f.write(f"{t}  {MASSES[t]}\t# {labels[t]}\n")
        f.write("\nAtoms # full\n\n")
        for i in range(len(pos)):
            f.write(f"{i+1} {mol[i]} {typ[i]} {qs[i]:.4f} "
                    f"{pos[i,0]:.5f}\t{pos[i,1]:.5f}\t{pos[i,2]:.5f}\t0 0 0\n")
        f.write("\nBonds\n\n")
        for bi, (bt, c, sh) in enumerate(bonds):
            f.write(f"{bi+1} {bt} {c+1} {sh+1}\n")
    print(f"        wrote {outfile}")
    return len(pos)
