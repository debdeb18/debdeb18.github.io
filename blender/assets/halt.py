"""The porch (halt), after the user's sketch: a stone platform standing in the sea beside the line, paved on top, with a
white fence along the back and the left end; along the back a vending machine, a lamp post and the waiting spot (an open
shelter with a tiled roof, two benches, a lamp on each front post and the train schedule board); steps down at the right
end to a small side jetty with a mooring post; and a railway-crossing signal at the front left.
Origin: centre of the platform's footprint at water level; the track side faces -Y; the top is at z = TOP."""
import math, random
from lib import *

VIEW = dict(angle=-28, lift=0.5, res=(1300, 820), samples=24)
LX, LY, TOP, BASE = 11.0, 4.6, 0.95, -1.2          # length, depth, top height, how far the block reaches down
COLOURS = dict(stone_a=0xC9B79A, stone_b=0xB7A483, stone_c=0xD6C7AB, joint=0x8E7F68, tile_a=0xD8CBB0, tile_b=0xCDBF9F, tile_c=0xE2D7BE,
               coping=0xEFE6D2, rail_w=0xF4F1EA, timber=0x8A5A3C, timber_dark=0x5C3B28, roof=0xB8573E, roof_dark=0x8E3F2C,
               bench_w=0xA57A4E, vend=0xE8EEF0, vend_glow=0xBFE6FF, lamp_w=0xFFE2A0, board=0xF3EAD2, iron_d=0x2E2D33,
               stripe_y=0xF2C230, stripe_k=0x26262A, red_l=0xE0453A, plank=0xA07650, plank_d=0x7E5A3A)

def stone_face(r, rnd, along, fixed, axis):
    """Courses of cut stone on one side of the block: rows of blocks of varying length."""
    z = BASE; row = 0
    while z < TOP - 0.12:
        h = min(0.34, TOP - 0.12 - z); a = -along / 2 + (0.3 if row % 2 else 0.0)
        if row % 2:
            l = 0.3
            if axis == 'x': box('stone', (l - 0.03, 0.06, h - 0.03), (-along / 2 + l / 2, fixed, z), color='stone_b', parent=r, bevel=0.025)
            else: box('stone', (0.06, l - 0.03, h - 0.03), (fixed, -along / 2 + l / 2, z), color='stone_b', parent=r, bevel=0.025)
        while a < along / 2 - 0.01:
            l = min(rnd.uniform(0.55, 1.05), along / 2 - a)
            c = rnd.choice(('stone_a', 'stone_b', 'stone_c'))
            if axis == 'x': box('stone', (l - 0.03, 0.06, h - 0.03), (a + l / 2, fixed, z), color=c, parent=r, bevel=0.025, jitter=0.006)
            else: box('stone', (0.06, l - 0.03, h - 0.03), (fixed, a + l / 2, z), color=c, parent=r, bevel=0.025, jitter=0.006)
            a += l
        z += h; row += 1

def fence(r, p0, p1):
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

def vending(r, x, y):
    z = TOP
    box('vend_body', (0.95, 0.65, 1.85), (x, y, z), color='vend', parent=r, bevel=0.04)
    box('vend_window', (0.8, 0.03, 0.9), (x, y - 0.33, z + 0.82), color='vend_glow', parent=r, bevel=0.005, emit=1.6)
    for i in range(8):
        cyl('can', 0.035, 0.035, 0.12, (x - 0.3 + (i % 4) * 0.2, y - 0.36, z + 1.1 + (i // 4) * 0.28), color=(0xD9532F, 0x3F8FD1, 0xF2C230, 0x5FA46B)[i % 4], parent=r, bevel=0.005, verts=10)
    box('vend_slot', (0.75, 0.04, 0.2), (x, y - 0.33, z + 0.3), color='iron_d', parent=r, bevel=0.01)
    box('vend_top', (1.0, 0.7, 0.1), (x, y, z + 1.85), color=0xD9483B, parent=r, bevel=0.03)

def lamp_post(r, x, y):
    z = TOP
    cyl('lamp_post', 0.06, 0.05, 2.9, (x, y, z), color='iron_d', parent=r, bevel=0.008, verts=12)
    box('lamp_foot', (0.3, 0.3, 0.12), (x, y, z), color='coping', parent=r, bevel=0.03)
    tube('lamp_arm', [(x, y, z + 2.8), (x, y - 0.25, z + 3.0), (x, y - 0.5, z + 2.9)], 0.025, 'iron_d', r)
    cyl('lamp_shade', 0.22, 0.06, 0.16, (x, y - 0.5, z + 2.68), color='iron_d', parent=r, bevel=0.01, verts=16)
    ball('lamp_bulb', 0.09, (x, y - 0.5, z + 2.66), color='lamp_w', parent=r, emit=5.0)

def shelter(r, x0, x1, y0, y1):
    """The waiting spot: four timber posts, a tiled roof sloping to the front, two benches, a lamp on each front post,
    the train schedule board on the right front post."""
    z = TOP; H = 2.35
    for x in (x0, x1):
        for y in (y0, y1):
            box('post', (0.16, 0.16, H + (0.25 if y == y1 else 0)), (x, y, z), color='timber_dark', parent=r, bevel=0.025)
    for y in (y0, y1): box('beam', (x1 - x0 + 0.4, 0.14, 0.18), ((x0 + x1) / 2, y, z + H - 0.05 + (0.25 if y == y1 else 0)), color='timber_dark', parent=r, bevel=0.02)
    for x in (x0, x1): box('beam_side', (0.14, y1 - y0 + 0.2, 0.16), (x, (y0 + y1) / 2, z + H + 0.05), (math.degrees(math.atan2(0.25, y1 - y0)), 0, 0), 'timber_dark', r, bevel=0.02)
    pitch = math.degrees(math.atan2(0.25, y1 - y0)) + 6
    shingles('shelter_roof', x1 - x0 + 0.9, (y1 - y0) + 1.0, 4, ((x0 + x1) / 2, y0 - 0.45, z + H + 0.05), pitch, color='roof', dark='roof_dark', parent=r, tile=0.4)
    for dx in (-0.6, 0.6):                                                     # wooden brackets under the eave
        box('bracket', (0.08, 0.5, 0.08), (x0 + 0.25 + dx * 0, y0 - 0.15, z + H - 0.35), (45, 0, 0), 'timber_dark', r, bevel=0.01)
        box('bracket', (0.08, 0.5, 0.08), (x1 - 0.25 + dx * 0, y0 - 0.15, z + H - 0.35), (45, 0, 0), 'timber_dark', r, bevel=0.01)
    # two benches facing the track
    L = (x1 - x0 - 0.9) / 2
    for bx in (x0 + 0.3 + L / 2, x1 - 0.3 - L / 2):
        by = y1 - 0.45
        for k, dz in enumerate((0.45,)):
            for j in range(3): box('bench_slat', (L, 0.14, 0.04), (bx, by - 0.16 + j * 0.16, z + dz), color='bench_w', parent=r, bevel=0.01, jitter=0.004)
        for j in range(2): box('bench_back', (L, 0.03, 0.12), (bx, by + 0.3, z + 0.72 + j * 0.18), color='bench_w', parent=r, bevel=0.01)
        for sx in (-1, 1):
            box('bench_leg', (0.07, 0.5, 0.45), (bx + sx * (L / 2 - 0.15), by, z), color='timber_dark', parent=r, bevel=0.01)
            box('bench_upright', (0.06, 0.06, 0.55), (bx + sx * (L / 2 - 0.15), by + 0.3, z + 0.45), color='timber_dark', parent=r, bevel=0.01)
    # a lantern hanging from each front post
    for x in (x0, x1):
        sx = -1 if x == x0 else 1
        tube('lantern_arm', [(x, y0, z + 1.95), (x + sx * 0.25, y0 - 0.05, z + 2.05), (x + sx * 0.35, y0 - 0.05, z + 1.95)], 0.02, 'iron_d', r)
        cyl('lantern_cap', 0.12, 0.05, 0.08, (x + sx * 0.35, y0 - 0.05, z + 1.88), color='iron_d', parent=r, bevel=0.01, verts=12)
        cyl('lantern', 0.09, 0.09, 0.22, (x + sx * 0.35, y0 - 0.05, z + 1.66), color='lamp_w', parent=r, bevel=0.03, emit=4.0, verts=12)
    # the train schedule board on the right front post, facing the track
    bx = x1 + 0.12
    box('schedule', (0.06, 0.75, 0.95), (bx, y0 + 0.45, z + 0.8), color='timber', parent=r, bevel=0.02)
    box('schedule_paper', (0.07, 0.62, 0.8), (bx + 0.01, y0 + 0.45, z + 0.87), color='board', parent=r, bevel=0.005)
    box('schedule_head', (0.08, 0.62, 0.12), (bx + 0.015, y0 + 0.45, z + 1.55), color=0x2F6F9A, parent=r, bevel=0.005)
    for i in range(6): box('schedule_line', (0.08, 0.5, 0.025), (bx + 0.02, y0 + 0.45, z + 0.97 + i * 0.09), color='iron_d', parent=r, bevel=0)

def crossing_signal(r, x, y):
    """A railway-crossing signal: a yellow-and-black striped mast, a crossbuck, two red lamps on a bar, a small
    direction box and a bell on top."""
    z = TOP; H = 3.4
    box('signal_foot', (0.42, 0.42, 0.18), (x, y, z), color='coping', parent=r, bevel=0.04)
    n = 12
    for i in range(n):
        cyl('mast', 0.075, 0.075, H / n, (x, y, z + 0.18 + i * (H - 0.18) / n), color='stripe_y' if i % 2 == 0 else 'stripe_k', parent=r, bevel=0.002, verts=14)
    # the crossbuck: two striped boards in an X
    zc = z + H - 0.2
    for ang in (35, -35):
        bd = root('crossbuck_arm'); bd.location = (x, y - 0.1, zc); bd.rotation_euler = (0, math.radians(ang), 0); bd.parent = r
        for k in range(6):
            box('crossbuck', (0.2, 0.04, 0.16), (-0.5 + k * 0.2 + 0.1, 0, -0.08), color='stripe_y' if k % 2 == 0 else 'stripe_k', parent=bd, bevel=0.01)
    # the lamp bar with two red lamps facing the track (and the other way)
    zl = z + H - 1.05
    box('lamp_bar', (1.1, 0.1, 0.1), (x, y, zl), color='stripe_k', parent=r, bevel=0.02)
    for sx in (-1, 1):
        for face in (-1, 1):
            cyl('lamp_hood', 0.17, 0.17, 0.08, (x + sx * 0.45, y + face * 0.06, zl - 0.12), (face * -90, 0, 0), 'stripe_k', r, bevel=0.01, verts=18)
            ball('red_lamp', 0.12, (x + sx * 0.45, y + face * 0.12, zl - 0.12), (1, 0.45, 1), 'red_l', r, emit=2.0)
            cyl('lamp_visor', 0.18, 0.18, 0.12, (x + sx * 0.45, y + face * 0.12, zl - 0.02), (face * -90, 0, 0), 'stripe_k', r, bevel=0.005, verts=18)
    box('arrow_box', (0.42, 0.14, 0.22), (x, y - 0.06, zl - 0.48), color='stripe_k', parent=r, bevel=0.02)
    box('arrow', (0.28, 0.02, 0.06), (x, y - 0.14, zl - 0.4), color='lamp_w', parent=r, bevel=0.005, emit=1.5)
    ball('bell', 0.15, (x, y, z + H + 0.02), (1, 1, 0.7), 'stripe_k', r)
    cyl('bell_rim', 0.17, 0.17, 0.04, (x, y, z + H - 0.05), color='stripe_k', parent=r, bevel=0.01, verts=16)

def build():
    PAL.update(COLOURS)
    rnd = random.Random(9); r = root('halt')
    # the block: a core, cut-stone faces on all four sides, a coping round the top edge
    box('core', (LX - 0.12, LY - 0.12, TOP - BASE), (0, 0, BASE), color='joint', parent=r, bevel=0.02)
    stone_face(r, rnd, LX, -LY / 2, 'x'); stone_face(r, rnd, LX, LY / 2, 'x')
    stone_face(r, rnd, LY, -LX / 2, 'y'); stone_face(r, rnd, LY, LX / 2, 'y')
    for y in (-LY / 2, LY / 2): box('coping', (LX + 0.14, 0.32, 0.12), (0, y, TOP - 0.12), color='coping', parent=r, bevel=0.03)
    for x in (-LX / 2, LX / 2): box('coping', (0.32, LY + 0.14, 0.12), (x, 0, TOP - 0.12), color='coping', parent=r, bevel=0.03)
    S = 0.5                                                                    # the paved top
    for i in range(int(LX / S)):
        for j in range(int(LY / S) + 1):
            yy = -LY / 2 + S / 2 + j * S
            if yy > LY / 2 - 0.1: continue
            box('tile', (S - 0.03, min(S, LY / 2 - yy + S / 2 - 0.05) - 0.03, 0.04), (-LX / 2 + S / 2 + i * S, yy, TOP - 0.03), color=rnd.choice(('tile_a', 'tile_b', 'tile_c')), parent=r, bevel=0.008, jitter=0.003)
    box('edge_line', (LX - 0.4, 0.12, 0.012), (0, -LY / 2 + 0.45, TOP + 0.01), color=0xE7C14A, parent=r, bevel=0.003)
    # the fence: along the back and the left end
    fence(r, (-LX / 2 + 0.15, LY / 2 - 0.15), (LX / 2 - 0.15, LY / 2 - 0.15))
    fence(r, (-LX / 2 + 0.15, -LY / 2 + 0.75), (-LX / 2 + 0.15, LY / 2 - 0.15))
    # along the back, left to right: the vending machine, a lamp post, the waiting spot
    vending(r, -2.7, LY / 2 - 0.65)
    lamp_post(r, -1.4, LY / 2 - 0.45)
    shelter(r, -0.4, 4.6, 0.35, LY / 2 - 0.45)
    # the railway-crossing signal at the front left
    crossing_signal(r, -LX / 2 + 0.75, -LY / 2 + 0.75)
    # steps down at the right end, then a small side jetty with a mooring post
    for k in range(4): box('step', (0.42, 1.6, 0.22), (LX / 2 + 0.21 + k * 0.42, 0.25, TOP - 0.22 - k * 0.2), color='stone_b', parent=r, bevel=0.03)
    JX0, JX1, JZ = LX / 2 + 1.68, LX / 2 + 5.4, 0.12
    for i in range(int((JX1 - JX0) / 0.3)):
        box('jetty_plank', (0.28, 1.6, 0.06), (JX0 + 0.15 + i * 0.3, 0.25, JZ), color='plank' if i % 3 else 'plank_d', parent=r, bevel=0.01, jitter=0.006)
    for jx in (JX0 + 0.3, JX0 + 1.9, JX1 - 0.2):
        for sy in (-0.65, 1.15): cyl('jetty_pile', 0.08, 0.07, 1.6, (jx, sy, -1.4), color='timber_dark', parent=r, bevel=0.01, verts=10)
    for sy in (-0.55, 1.05): box('jetty_beam', (JX1 - JX0, 0.12, 0.14), ((JX0 + JX1) / 2, sy, JZ - 0.14), color='timber_dark', parent=r, bevel=0.02)
    cyl('bollard', 0.12, 0.1, 0.5, (JX1 - 0.3, 0.95, JZ + 0.06), color='timber_dark', parent=r, bevel=0.03, verts=12)
    ball('bollard_cap', 0.13, (JX1 - 0.3, 0.95, JZ + 0.58), (1, 1, 0.5), 'timber_dark', r)
    tube('rope', [(JX1 - 0.3, 0.95, JZ + 0.4), (JX1 - 0.2, 1.6, JZ + 0.05), (JX1 - 0.4, 2.3, JZ + 0.25)], 0.02, 0xD9C08E, r)
    return r
