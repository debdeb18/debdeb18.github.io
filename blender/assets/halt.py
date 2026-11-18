"""The porch (halt), after the user's sketch: a stone platform standing in the sea beside the line, paved on top, with a
white fence along the back and the left end; along the back an info and timetable board, a lamp post and the waiting spot (an open
shelter with a tiled roof, a row of four seats and a bin, a lamp on each front post); steps down at the right
end to a small side jetty with a mooring post; and a railway-crossing signal at the front left.
Origin: centre of the platform's footprint at water level; the track side faces -Y; the top is at z = TOP."""
import math, random
from lib import *

VIEW = dict(angle=-28, lift=0.5, res=(1300, 820), samples=24)
LX, LY, TOP, BASE = 11.0, 4.6, 0.95, -1.2          # length, depth, top height, how far the block reaches down
COLOURS = dict(stone_a=0xC9B79A, stone_b=0xB7A483, stone_c=0xD6C7AB, joint=0x8E7F68, tile_a=0xD8CBB0, tile_b=0xCDBF9F, tile_c=0xE2D7BE,
               coping=0xEFE6D2, rail_w=0xF4F1EA, timber=0x8A5A3C, timber_dark=0x5C3B28, roof=0xB8573E, roof_dark=0x8E3F2C,
               bench_w=0xA57A4E, seat_wood=0xA0623A, seat_frame=0x2F3036, vend_body=0xE0602F, vend_dark=0x5A2A1E, vend_glow=0xFFE6B0, button_lit=0xFFF4D8, lamp_w=0xFFE2A0, board=0xF3EAD2, iron_d=0x2E2D33,
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

def info_board(r, x, y):
    """The board along the back fence: train times on the left, station notices and a map of the islands on the
    right, under a little tiled hood, on two timber legs. Faces the track (-Y)."""
    z = TOP; W, H, zb = 1.7, 1.05, z + 0.75
    for sx in (-1, 1): box('board_leg', (0.12, 0.12, zb - z + H + 0.25), (x + sx * (W / 2 - 0.05), y + 0.04, z), color='timber_dark', parent=r, bevel=0.02)
    box('board_back', (W, 0.07, H), (x, y, zb), color='timber', parent=r, bevel=0.02)
    box('board_frame_t', (W + 0.08, 0.1, 0.07), (x, y - 0.02, zb + H - 0.035), color='timber_dark', parent=r, bevel=0.015)
    box('board_frame_b', (W + 0.08, 0.1, 0.07), (x, y - 0.02, zb - 0.035), color='timber_dark', parent=r, bevel=0.015)
    shingles('board_hood', W + 0.3, 0.45, 1, (x, y - 0.18, zb + H + 0.12), 22, color='roof', dark='roof_dark', parent=r, tile=0.3)
    yf = y - 0.04
    # the timetable: a white sheet with a blue head and rows of times
    tx = x - W / 4 - 0.02
    box('time_paper', (0.74, 0.02, 0.86), (tx, yf, zb + 0.09), color='board', parent=r, bevel=0.004)
    box('time_head', (0.74, 0.025, 0.13), (tx, yf - 0.002, zb + 0.82), color=0x2F6F9A, parent=r, bevel=0.003)
    for i in range(7):
        for c in (-0.2, 0.12):
            box('time_line', (0.26 if c < 0 else 0.34, 0.025, 0.028), (tx + c, yf - 0.004, zb + 0.18 + i * 0.085), color='iron_d', parent=r, bevel=0)
    # the notices: a map of the islands, and two small posters
    nx = x + W / 4 + 0.02
    box('map_paper', (0.7, 0.02, 0.5), (nx, yf, zb + 0.47), color=0xE8F1F2, parent=r, bevel=0.004)
    for (dx, dz, rr) in ((-0.12, 0.2, 0.09), (0.12, 0.27, 0.06), (0.22, 0.15, 0.045)):
        cyl('map_island', rr, rr, 0.025, (nx + dx, yf - 0.003, zb + 0.47 + dz), (90, 0, 0), 0x7DB85A, r, bevel=0, verts=14)
    box('map_line', (0.62, 0.025, 0.02), (nx, yf - 0.004, zb + 0.56), color=0xB8403A, parent=r, bevel=0)
    box('poster_a', (0.32, 0.02, 0.36), (nx - 0.18, yf, zb + 0.06), color=0xF2C46A, parent=r, bevel=0.004)
    box('poster_b', (0.3, 0.02, 0.32), (nx + 0.19, yf, zb + 0.08), color=0xE8A0A0, parent=r, bevel=0.004)
    for (px, pz) in ((nx - 0.18, zb + 0.4), (nx + 0.19, zb + 0.38), (nx - 0.3, zb + 0.95), (nx + 0.3, zb + 0.95), (tx - 0.33, zb + 0.93), (tx + 0.33, zb + 0.93)):
        ball('pin', 0.016, (px, yf - 0.015, pz), (1, 0.6, 1), 0xB8403A, r)

def trash_can(r, x, y):
    """A station rubbish bin: a dark green drum with a domed lid, a round mouth in front and a label band."""
    z = TOP
    cyl('bin', 0.24, 0.22, 0.72, (x, y, z), color=0x3E6B55, parent=r, bevel=0.02, verts=24)
    cyl('bin_band', 0.245, 0.245, 0.1, (x, y, z + 0.42), color='board', parent=r, bevel=0.01, verts=24)
    cyl('bin_lid', 0.25, 0.25, 0.05, (x, y, z + 0.72), color=0x2F5444, parent=r, bevel=0.015, verts=24)
    ball('bin_dome', 0.24, (x, y, z + 0.77), (1, 1, 0.35), 0x2F5444, r)
    cyl('bin_mouth', 0.09, 0.09, 0.04, (x, y - 0.235, z + 0.6), (90, 0, 0), 'iron_d', r, bevel=0.01, verts=18)
    cyl('bin_foot', 0.2, 0.2, 0.04, (x, y, z), color=0x2F5444, parent=r, bevel=0.01, verts=24)

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
    # one row of four platform seats on a dark metal frame, the bin at its left end
    cx = (x0 + x1) / 2 + 0.45
    seat_row(r, cx, y1 - 0.5, 4)
    trash_can(r, cx - 4 * 0.62 / 2 - 0.42, y1 - 0.5)
    # a lantern hanging from each front post
    for x in (x0, x1):
        sx = -1 if x == x0 else 1
        tube('lantern_arm', [(x, y0, z + 1.95), (x + sx * 0.25, y0 - 0.05, z + 2.05), (x + sx * 0.35, y0 - 0.05, z + 1.95)], 0.02, 'iron_d', r)
        cyl('lantern_cap', 0.12, 0.05, 0.08, (x + sx * 0.35, y0 - 0.05, z + 1.88), color='iron_d', parent=r, bevel=0.01, verts=12)
        cyl('lantern', 0.09, 0.09, 0.22, (x + sx * 0.35, y0 - 0.05, z + 1.66), color='lamp_w', parent=r, bevel=0.03, emit=4.0, verts=12)

def seat_row(r, cx, cy, n):
    """A row of n moulded wooden seats on a shared metal beam, facing -Y: each seat a gently dished pan and a curved back."""
    z = TOP; P = 0.62; x0 = cx - (n - 1) * P / 2
    box('seat_beam', (n * P, 0.08, 0.07), (cx, cy, z + 0.34), color='seat_frame', parent=r, bevel=0.02)
    for sx in (-1, 1):                                                        # two T-legs with feet
        lx = cx + sx * (n * P / 2 - 0.25)
        box('seat_leg', (0.07, 0.07, 0.34), (lx, cy, z), color='seat_frame', parent=r, bevel=0.015)
        box('seat_foot', (0.1, 0.5, 0.04), (lx, cy, z), color='seat_frame', parent=r, bevel=0.015)
    for i in range(n):
        x = x0 + i * P
        box('seat_mount', (0.06, 0.3, 0.06), (x, cy, z + 0.39), color='seat_frame', parent=r, bevel=0.01)
        for k in range(5):                                                   # the seat pan, dipping a little in the middle
            t = k / 4; yy = cy - 0.2 + t * 0.4; dz = 0.035 * math.sin(math.pi * t)
            plank('seat_pan', (P - 0.08, 0.092, 0.042), (x, yy, z + 0.45 - dz), (-8 + 16 * t, 0, 0), 'seat_wood', r, bevel=0.014)
        for k in range(5):                                                   # the back, curving up and slightly back
            t = k / 4; yy = cy + 0.22 + t * 0.07; zz = z + 0.5 + t * 0.4
            plank('seat_back', (P - 0.1, 0.092, 0.042), (x, yy, zz + 0.046), (80 - 8 * t, 0, 0), 'seat_wood', r, bevel=0.014)
        box('seat_back_post', (0.04, 0.04, 0.32), (x, cy + 0.2, z + 0.4), (-12, 0, 0), 'seat_frame', r, bevel=0.008)

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
        for k in range(7):                                                    # centred on the mast, yellow at both ends
            box('crossbuck', (0.17, 0.04, 0.16), (-0.51 + k * 0.17, 0, -0.08), color='stripe_y' if k % 2 == 0 else 'stripe_k', parent=bd, bevel=0.01)
    # the lamp bar with two red lamps facing the track (and the other way)
    zl = z + H - 1.05
    box('lamp_bar', (1.1, 0.1, 0.1), (x, y, zl), color='stripe_k', parent=r, bevel=0.02)
    for sx in (-1, 1):
        for face in (-1, 1):
            yf = y + face * 0.05                                              # a round black backplate, the red lens on it
            cyl('lamp_plate', 0.19, 0.19, 0.04, (x + sx * 0.45, yf, zl - 0.12), (face * -90, 0, 0), 'stripe_k', r, bevel=0.01, verts=24)
            ball('red_lamp', 0.13, (x + sx * 0.45, yf + face * 0.04, zl - 0.12), (1, 0.32, 1), 'red_l', r, emit=2.0)
            for k in range(9):                                               # a curved hood over the top half of the lens
                ang = -80 + k * 20; R = 0.19
                box('lamp_visor', (0.075, 0.12, 0.022), (x + sx * 0.45 + R * math.sin(math.radians(ang)), yf + face * 0.08, zl - 0.12 + R * math.cos(math.radians(ang)) - 0.011), (0, ang, 0), 'stripe_k', r, bevel=0.006)
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
    # along the back, left to right: the info board, a lamp post, the waiting spot
    info_board(r, -2.6, LY / 2 - 0.42)
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
