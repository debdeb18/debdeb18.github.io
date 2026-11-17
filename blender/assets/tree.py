"""Trees: a leafy broadleaf (lumpy canopy clumps, dark underneath and sunlit on top) and a tiered pine."""
import math, random
from lib import *
VIEW = dict(angle=30, lift=0.2)

def build(h=6.0, r=4.0, seed=3, kind='broad'):
    rnd = random.Random(seed); t = root('tree')
    if kind == 'pine':
        cyl('trunk', r * 0.09, r * 0.05, h * 1.15, (0, 0, 0), (rnd.uniform(-2, 2), rnd.uniform(-2, 2), 0), 'trunk', t, bevel=0.02, verts=10)
        n = 6
        for i in range(n):
            k = i / (n - 1); rr = r * 0.62 * (1 - k * 0.78)
            cyl('tier', rr, rr * 0.18, h * 0.3, (rnd.uniform(-0.08, 0.08), rnd.uniform(-0.08, 0.08), h * (0.28 + k * 0.72)), (rnd.uniform(-5, 5), rnd.uniform(-5, 5), rnd.uniform(0, 90)),
                'tree' if i % 2 == 0 else 'tree_mid', t, bevel=0.06, verts=9, rough=1)
        return t
    lx, ly = rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5)
    tube('trunk', [(0, 0, -0.2), (lx * 0.4, ly * 0.4, h * 0.4), (lx, ly, h * 0.75), (lx * 0.8, ly * 0.8, h * 1.05)], [r * 0.15, r * 0.1, r * 0.075, r * 0.04], 'trunk', t)
    clumps = []
    for i in range(7):                                    # a skirt of low, dark clumps
        a = i / 7 * 6.283 + rnd.uniform(-0.3, 0.3); d = r * rnd.uniform(0.5, 0.72)
        clumps.append((lx + math.cos(a) * d, ly + math.sin(a) * d, h + rnd.uniform(-0.12, 0.1) * r, r * rnd.uniform(0.4, 0.52), 'tree'))
    for i in range(5):                                    # the body
        a = i / 5 * 6.283 + rnd.uniform(-0.4, 0.4); d = r * rnd.uniform(0.25, 0.45)
        clumps.append((lx + math.cos(a) * d, ly + math.sin(a) * d, h + rnd.uniform(0.25, 0.45) * r, r * rnd.uniform(0.42, 0.55), 'tree_mid'))
    for i in range(3):                                    # the sunlit crown
        a = rnd.uniform(0, 6.283); d = r * rnd.uniform(0, 0.25)
        clumps.append((lx + math.cos(a) * d, ly + math.sin(a) * d, h + rnd.uniform(0.6, 0.8) * r, r * rnd.uniform(0.34, 0.45), 'tree_light'))
    for x, y, z, cr, col in clumps:
        lump('leaves', cr, (x, y, z), (1, 1, 0.82), col, t, rough=1)
        if col != 'tree' and rnd.random() < 0.8:          # small highlights catching the light
            lump('highlight', cr * 0.42, (x + rnd.uniform(-0.3, 0.3) * cr, y - 0.3 * cr, z + cr * 0.55), (1, 1, 0.7), 'tree_hi' if col == 'tree_light' else 'tree_light', t, rough=1)
    for i in range(2):
        a = rnd.uniform(0, 6.283)
        tube('branch', [(lx * 0.5, ly * 0.5, h * 0.55), (lx + math.cos(a) * r * 0.3, ly + math.sin(a) * r * 0.3, h * 0.8), (lx + math.cos(a) * r * 0.55, ly + math.sin(a) * r * 0.55, h * 0.98)], [r * 0.06, r * 0.04, r * 0.02], 'trunk', t)
    return t
