"""Trees after the painted-tree references: slender, curving trunks that fork into a few limbs, each limb ending in its
own puffy clump of leaves (lumps: dark underneath, lit on top). Three broadleaf styles plus a conifer made of stacked
rounded puffs (no cones). The website covers every clump in painted leaf cards; these lumps are the shape and the shade.
    style 0: umbrella, wide and flat-topped   style 1: tall, clumps at two levels   style 2: round, forked low"""
import math, random
from lib import *
VIEW = dict(angle=30, lift=0.2)

def clump(t, x, y, z, s, rnd, flat=0.72):
    """One puff of leaves: a ring of lumps around a centre, darker below, lighter on top, a few highlights."""
    lump('leaves', s * 0.62, (x, y, z), (1, 1, flat), 'tree_mid', t, rough=1)
    n = 5
    for i in range(n):
        a = i / n * 6.283 + rnd.uniform(-0.3, 0.3); d = s * rnd.uniform(0.45, 0.62)
        lump('leaves', s * rnd.uniform(0.38, 0.5), (x + math.cos(a) * d, y + math.sin(a) * d, z - s * 0.12), (1, 1, flat), 'tree', t, rough=1)
    for i in range(3):
        a = rnd.uniform(0, 6.283); d = s * rnd.uniform(0, 0.35)
        lump('leaves', s * rnd.uniform(0.32, 0.42), (x + math.cos(a) * d, y + math.sin(a) * d, z + s * 0.32), (1, 1, flat), 'tree_light', t, rough=1)
    lump('highlight', s * 0.22, (x + rnd.uniform(-0.2, 0.2) * s, y - 0.2 * s, z + s * 0.5), (1, 1, 0.7), 'tree_hi', t, rough=1)

def limb(t, base, tip, r0, r1, rnd):
    """A gently curving branch from base to tip."""
    mx, my, mz = [(a + b) / 2 for a, b in zip(base, tip)]
    bend = (rnd.uniform(-0.25, 0.25), rnd.uniform(-0.25, 0.25), 0.15)
    tube('branch', [base, (mx + bend[0], my + bend[1], mz + bend[2]), tip], [r0, (r0 + r1) / 2, r1], 'trunk', t)

def build(h=6.0, r=4.0, seed=3, kind='broad'):
    rnd = random.Random(seed); t = root('tree')
    if kind == 'pine':                                                   # a conifer: a column of rounded puffs
        H = h * 1.15
        tube('trunk', [(0, 0, -0.2), (0.05, 0.03, H * 0.5), (0, 0, H)], [r * 0.08, r * 0.06, r * 0.03], 'trunk', t)
        tiers = 6
        for k in range(tiers):
            f = k / (tiers - 1); rr = r * 0.5 * (1 - f * 0.72); z = h * 0.32 + f * h * 0.78
            n = max(1, round(6 * (1 - f * 0.8)))
            for i in range(n):
                a = i / n * 6.283 + k * 0.6; d = rr * 0.55 if n > 1 else 0
                lump('leaves', rr * rnd.uniform(0.55, 0.7), (math.cos(a) * d, math.sin(a) * d, z), (1, 1, 0.75), 'tree' if i % 2 else 'tree_mid', t, rough=1)
            lump('leaves', rr * 0.55, (0, 0, z + rr * 0.25), (1, 1, 0.8), 'tree_light' if k > 2 else 'tree_mid', t, rough=1)
        return t
    style = seed % 3
    lean = rnd.uniform(0.3, 0.8) * (1 if seed % 2 else -1); la = rnd.uniform(0, 6.283)
    lx, ly = math.cos(la) * lean, math.sin(la) * lean
    H = h * (1.3 if style == 1 else 1.0)
    trunk_top = (lx, ly, H * 0.72)
    tube('trunk', [(0, 0, -0.2), (lx * 0.25, ly * 0.25, H * 0.3), (lx * 0.7, ly * 0.7, H * 0.55), trunk_top], [r * 0.09, r * 0.065, r * 0.05, r * 0.04], 'trunk', t)
    tube('flare', [(0, 0, -0.2), (0, 0, 0.35)], [r * 0.14, r * 0.09], 'trunk', t)
    clumps = []
    if style == 0:                                                       # umbrella: four limbs spread wide, a flat crown
        for i in range(4):
            a = i / 4 * 6.283 + rnd.uniform(-0.35, 0.35); d = r * rnd.uniform(0.5, 0.75)
            tip = (lx + math.cos(a) * d, ly + math.sin(a) * d, H * 0.9 + rnd.uniform(-0.2, 0.3))
            limb(t, trunk_top, tip, r * 0.035, r * 0.015, rnd); clumps.append((tip, r * rnd.uniform(0.42, 0.52), 0.62))
        clumps.append(((lx, ly, H * 1.0), r * 0.5, 0.6))
    elif style == 1:                                                     # tall: a mid clump on a side branch, a crown on top
        top = (lx * 1.15, ly * 1.15, H)
        limb(t, trunk_top, top, r * 0.04, r * 0.02, rnd); clumps.append((top, r * 0.48, 0.75))
        for i in range(2):
            a = la + math.pi * (0.6 + i * 0.8) + rnd.uniform(-0.3, 0.3)
            base = (lx * 0.55, ly * 0.55, H * 0.5 + i * H * 0.12)
            tip = (base[0] + math.cos(a) * r * 0.55, base[1] + math.sin(a) * r * 0.55, base[2] + r * 0.25)
            limb(t, base, tip, r * 0.03, r * 0.012, rnd); clumps.append((tip, r * rnd.uniform(0.32, 0.4), 0.72))
        a = la + 0.4; clumps.append(((lx + math.cos(a) * r * 0.35, ly + math.sin(a) * r * 0.35, H * 0.88), r * 0.38, 0.72))
    else:                                                                # round: forks low into three limbs, a rounded crown
        fork = (lx * 0.6, ly * 0.6, H * 0.5)
        for i in range(3):
            a = i / 3 * 6.283 + rnd.uniform(-0.3, 0.3); d = r * rnd.uniform(0.3, 0.45)
            tip = (fork[0] + math.cos(a) * d, fork[1] + math.sin(a) * d, H * 0.95 + rnd.uniform(-0.1, 0.25))
            limb(t, fork, tip, r * 0.04, r * 0.018, rnd); clumps.append((tip, r * rnd.uniform(0.4, 0.48), 0.78))
        clumps.append(((lx * 0.7, ly * 0.7, H * 1.12), r * 0.42, 0.8))
    for (x, y, z), s, flat in clumps: clump(t, x, y, z, s, rnd, flat)
    return t
