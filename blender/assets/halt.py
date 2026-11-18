"""The halt: a small stone platform standing in the sea beside the line, after the user's reference. Cut-stone sides,
a paved top, a white balustrade along the back and the far end (the near end stays open to a boardwalk), a little
red waiting booth with a slab roof, and a signal post at the front corner.
Origin: centre of the platform's footprint at water level; the track side faces -Y; the top is at z = TOP."""
import math, random
from lib import *

VIEW = dict(angle=30, lift=0.45, res=(1300, 820))
LX, LY, TOP, BASE = 8.0, 4.0, 0.95, -1.2          # length, depth, top height, how far the block reaches down
COLOURS = dict(stone_a=0xC9B79A, stone_b=0xB7A483, stone_c=0xD6C7AB, joint=0x8E7F68, tile_a=0xD8CBB0, tile_b=0xCDBF9F, tile_c=0xE2D7BE,
               coping=0xEFE6D2, rail_w=0xF4F1EA, booth=0x9C3F2E, booth_dark=0x7A2F22, booth_trim=0xEFE3C8, slab=0x5E666E,
               glass_h=0x3A4652, post_g=0x4A4E55, lamp_r=0xE0453A, lamp_g=0x5FD08A, lamp_w=0xFFE2A0)

def stone_face(r, rnd, along, fixed, axis):
    """Courses of cut stone on one side of the block: rows of blocks of varying length."""
    z = BASE; row = 0
    while z < TOP - 0.12:
        h = min(0.34, TOP - 0.12 - z); a = -along / 2 + (0.3 if row % 2 else 0.0) - 0.3
        while a < along / 2:
            l = min(rnd.uniform(0.55, 1.05), along / 2 - a)
            if l > 0.08:
                c = rnd.choice(('stone_a', 'stone_b', 'stone_c'))
                if axis == 'x': box('stone', (l - 0.03, 0.06, h - 0.03), (a + l / 2, fixed, z), color=c, parent=r, bevel=0.025, jitter=0.006)
                else: box('stone', (0.06, l - 0.03, h - 0.03), (fixed, a + l / 2, z), color=c, parent=r, bevel=0.025, jitter=0.006)
            a += l
        z += h; row += 1

def balustrade(r, p0, p1):
    """A white railing from p0 to p1 (on the platform top): posts with caps, top and bottom rails, close balusters."""
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0); ang = math.degrees(math.atan2(y1 - y0, x1 - x0)); z = TOP
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    box('rail_bottom', (L, 0.09, 0.07), (cx, cy, z + 0.12), (0, 0, ang), 'rail_w', r, bevel=0.015)
    box('rail_top', (L + 0.12, 0.14, 0.08), (cx, cy, z + 0.92), (0, 0, ang), 'rail_w', r, bevel=0.025)
    n = max(2, round(L / 1.6))
    for i in range(n + 1):
        t = i / n; x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        box('post', (0.16, 0.16, 0.95), (x, y, z), (0, 0, ang), 'rail_w', r, bevel=0.03)
        box('post_cap', (0.22, 0.22, 0.06), (x, y, z + 0.95), (0, 0, ang), 'rail_w', r, bevel=0.02)
    m = int(L / 0.17)
    for i in range(1, m):
        t = i / m; x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        cyl('baluster', 0.028, 0.028, 0.72, (x, y, z + 0.18), color='rail_w', parent=r, bevel=0.005, verts=8)

def booth(r, x, y):
    """The little waiting booth: red walls with cream trim, a window toward the track, an open side, a bench inside."""
    W, D, H = 1.6, 1.3, 2.25; z = TOP
    box('booth_back', (W, 0.1, H), (x, y + D / 2 - 0.05, z), color='booth', parent=r, bevel=0.02)
    box('booth_side', (0.1, D, H), (x + W / 2 - 0.05, y, z), color='booth', parent=r, bevel=0.02)
    for xx in (-W / 2 + 0.05,): box('booth_side_open', (0.1, 0.35, H), (x + xx, y + D / 2 - 0.22, z), color='booth', parent=r, bevel=0.02)
    # front: wall below and above a window
    box('booth_front_low', (W, 0.1, 0.95), (x, y - D / 2 + 0.05, z), color='booth', parent=r, bevel=0.02)
    box('booth_front_high', (W, 0.1, 0.35), (x, y - D / 2 + 0.05, z + H - 0.35), color='booth', parent=r, bevel=0.02)
    box('window', (W - 0.3, 0.04, H - 1.3 - 0.05), (x, y - D / 2 + 0.05, z + 0.95), color='glass_h', parent=r, bevel=0.01, rough=0.15)
    for xx in (-W / 2 + 0.07, W / 2 - 0.07): box('jamb', (0.14, 0.12, H - 1.3), (x + xx, y - D / 2 + 0.05, z + 0.95), color='booth', parent=r, bevel=0.015)
    box('mullion', (0.06, 0.08, H - 1.3), (x, y - D / 2 + 0.03, z + 0.95), color='booth_trim', parent=r, bevel=0.01)
    for zz in (0.95, H - 0.36): box('trim', (W + 0.04, 0.13, 0.06), (x, y - D / 2 + 0.05, z + zz), color='booth_trim', parent=r, bevel=0.015)
    box('skirting', (W + 0.04, D + 0.04, 0.12), (x, y, z), color='booth_dark', parent=r, bevel=0.02)
    # slab roof, a little overhang, a gutter line
    box('roof', (W + 0.5, D + 0.5, 0.16), (x, y, z + H), color='slab', parent=r, bevel=0.04)
    box('roof_edge', (W + 0.56, D + 0.56, 0.05), (x, y, z + H - 0.03), color='booth_trim', parent=r, bevel=0.015)
    # inside: a plank bench along the back, a small timetable on the side wall, a lamp under the roof
    box('bench', (W - 0.3, 0.38, 0.06), (x, y + D / 2 - 0.3, z + 0.45), color=0xA57A4E, parent=r, bevel=0.015)
    for xx in (-W / 2 + 0.3, W / 2 - 0.3): box('bench_leg', (0.06, 0.32, 0.45), (x + xx, y + D / 2 - 0.3, z), color=0x6E4E33, parent=r, bevel=0.01)
    box('timetable', (0.03, 0.45, 0.6), (x + W / 2 - 0.11, y, z + 1.2), color='booth_trim', parent=r, bevel=0.01)
    cyl('booth_lamp', 0.1, 0.06, 0.1, (x, y, z + H - 0.12), color='lamp_w', parent=r, bevel=0.01, emit=2.0)

def signal(r, x, y):
    """The signal post at the front corner: a tall grey mast with a ladder, a two-lamp head and a small hood."""
    z = TOP; H = 4.4
    cyl('mast', 0.08, 0.06, H, (x, y, z), color='post_g', parent=r, bevel=0.01, verts=12)
    box('mast_foot', (0.4, 0.4, 0.2), (x, y, z), color='coping', parent=r, bevel=0.04)
    for k in range(10): box('rung', (0.32, 0.03, 0.03), (x, y + 0.12, z + 0.5 + k * 0.32), color='post_g', parent=r, bevel=0.005)
    for sx in (-0.15, 0.15): box('ladder_side', (0.03, 0.03, 3.3), (x + sx, y + 0.12, z + 0.4), color='post_g', parent=r, bevel=0.005)
    box('head', (0.34, 0.22, 0.8), (x, y - 0.06, z + H - 0.95), color='post_g', parent=r, bevel=0.05)
    for k, c in enumerate(('lamp_r', 'lamp_g')):
        zz = z + H - 0.72 + (1 - k) * 0.36
        cyl('lamp_hood', 0.13, 0.13, 0.16, (x, y - 0.2, zz), (90, 0, 0), 'post_g', r, bevel=0.01, verts=16)
        ball('signal_lamp', 0.09, (x, y - 0.27, zz), (1, 0.5, 1), c, r, emit=2.5)
    box('head_cap', (0.42, 0.3, 0.06), (x, y - 0.06, z + H - 0.15), color='post_g', parent=r, bevel=0.02)
    cyl('finial', 0.04, 0.01, 0.25, (x, y - 0.06, z + H - 0.1), color='post_g', parent=r, bevel=0.005, verts=8)

def build():
    PAL.update(COLOURS)
    rnd = random.Random(9); r = root('halt')
    # the block: a core, then cut-stone faces on all four sides, a coping round the top edge
    box('core', (LX - 0.12, LY - 0.12, TOP - BASE), (0, 0, BASE), color='joint', parent=r, bevel=0.02)
    stone_face(r, rnd, LX, -LY / 2, 'x'); stone_face(r, rnd, LX, LY / 2, 'x')
    stone_face(r, rnd, LY, -LX / 2, 'y'); stone_face(r, rnd, LY, LX / 2, 'y')
    for y in (-LY / 2, LY / 2): box('coping', (LX + 0.14, 0.32, 0.12), (0, y, TOP - 0.12), color='coping', parent=r, bevel=0.03)
    for x in (-LX / 2, LX / 2): box('coping', (0.32, LY + 0.14, 0.12), (x, 0, TOP - 0.12), color='coping', parent=r, bevel=0.03)
    # the paved top: square slabs with thin joints and slightly varied tones
    S = 0.5
    for i in range(int(LX / S)):
        for j in range(int(LY / S)):
            box('tile', (S - 0.03, S - 0.03, 0.04), (-LX / 2 + S / 2 + i * S, -LY / 2 + S / 2 + j * S, TOP - 0.03), color=rnd.choice(('tile_a', 'tile_b', 'tile_c')), parent=r, bevel=0.008, jitter=0.003)
    box('edge_line', (LX - 0.4, 0.12, 0.012), (0, -LY / 2 + 0.45, TOP + 0.01), color=0xE7C14A, parent=r, bevel=0.003)   # the safety line
    # balustrade along the back and the far (-x) end; the +x end stays open for the boardwalk
    balustrade(r, (-LX / 2 + 0.15, LY / 2 - 0.15), (LX / 2 - 0.15, LY / 2 - 0.15))
    balustrade(r, (-LX / 2 + 0.15, -LY / 2 + 0.6), (-LX / 2 + 0.15, LY / 2 - 0.15))
    booth(r, LX / 2 - 1.25, LY / 2 - 0.95)
    signal(r, -LX / 2 + 0.55, -LY / 2 + 0.55)
    # a couple of mooring rings and a step down to the water at the open end
    for k in range(3): box('step', (0.5, 1.2, 0.2), (LX / 2 + 0.25 + k * 0.5, 0.6, TOP - 0.25 - k * 0.3), color='stone_b', parent=r, bevel=0.03)
    return r
