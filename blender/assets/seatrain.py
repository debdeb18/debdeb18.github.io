"""Design B: a two-car sea-railway train after the user's references.

The body is not a box. Every car is lofted from one cross-section: the sides bulge slightly at the waist and lean in
above the windows (tumblehome), a rounded shoulder runs into a curved roof. At each outer end that same cross-section is
swept round into a rounded nose that rakes back at the windscreen. Colours follow the bands of the cross-section:
ribbed orange-red below, a cream-yellow window band, a red-brown roof.

Inside: plank floor, wood wainscot, long pink upholstered benches on wooden bases, end panels with grab poles and
rails, overhead luggage racks on brackets, hanging ring straps, a curved cream ceiling with round lamps and vent
grilles, and an arched doorway through to the next car. Front faces -Y, wheels sit at z = 0."""
import math
import bmesh, bpy
from mathutils import Matrix
import lib
from lib import *

VIEW = dict(angle=35, lift=0.22, res=(1300, 820))
L, GAP, NOSE = 14.0, 0.8, 0.85                     # car length (nose tip to coupling end), gap between cars, nose depth
ZB, ZW = 1.95, 2.72                                # window band: bottom and top
COLOURS = dict(lower=0xC9573E, lower_dark=0x9E3D2F, upper=0xF2C85E, upper_pale=0xF8E6AE, roof_t=0x8E3B31, roof_box=0x7B3129,
               trim=0x3A2A26, glass_t=0x31414F, lamp_t=0xFFE2A0, plank=0xA0683C, plank_dark=0x7E4C2A, wain=0x6E4428, wain_dark=0x5A3720,
               cushion=0xD9707A, cushion_dark=0xB9505C, wall_in=0xF2DDB8, ceil=0xF6E6C8, pole=0x8A6A48, brass_t=0xD9A441,
               ring=0xEDE2C8, iron=0x2E2D33, rack=0x5E4A3A)

# The cross-section (half of it, x >= 0), from the skirt up to the roof crown. Rows between points become bands:
# 0..3 lower body, 3..4 the window band, 4..5 the cream strip above the windows, 5.. the roof.
HALF = [(1.30, 0.55), (1.355, 0.85), (1.385, 1.25), (1.375, ZB), (1.315, ZW), (1.27, 2.86), (1.17, 3.02), (0.98, 3.14),
        (0.68, 3.24), (0.34, 3.29), (0.0, 3.31)]
BAND = lambda k: 'lower' if k < 3 else 'window' if k == 3 else 'upper' if k == 4 else 'roof_t'

def xat(z):
    """Half-width of the body at height z (on the sides, below the shoulder)."""
    for (x0, z0), (x1, z1) in zip(HALF, HALF[1:]):
        if z0 <= z <= z1: return x0 + (x1 - x0) * (z - z0) / (z1 - z0)
    return HALF[0][0]

def grid(name, rows, color, parent, solid=0.0, **mk):
    """A smooth surface through a grid of 3D points (rows x cols), optionally given thickness."""
    bm = bmesh.new(); vs = [[bm.verts.new(p) for p in row] for row in rows]
    for i in range(len(rows) - 1):
        for j in range(len(rows[0]) - 1):
            try: bm.faces.new((vs[i][j], vs[i][j + 1], vs[i + 1][j + 1], vs[i + 1][j]))
            except ValueError: pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bm.normal_update()
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = lib._finish(name, me, color, (0, 0, 0), (0, 0, 0), parent, 0, **mk)
    if solid:
        m = o.modifiers.new('solid', 'SOLIDIFY'); m.thickness = solid; m.offset = 0
        o.modifiers.move(len(o.modifiers) - 1, 0)
    return o

def band_rows(k0, k1, side):
    """The profile points from row k0 to k1 on one side (side = +1 or -1), bottom to top."""
    return [(side * x, z) for x, z in HALF[k0:k1 + 1]]

def across(k0, k1):
    """The profile from row k0 on the -x side, over the top, down to row k0 on the +x side (k1 is the crown)."""
    return [p for p in reversed(band_rows(k0, k1, -1))] + band_rows(k0, k1, 1)[1:]

def loft(name, pts, ya, yb, color, parent, **mk):
    return grid(name, [[(x, ya, z), (x, yb, z)] for x, z in pts], color, parent, **mk)

def nose_point(X, z, th, yj, f):
    """A point on the nose: the cross-section swept round a half-ellipse in plan, raked back above the window sill."""
    d = NOSE * (0.88 + 0.12 * min(1, (z - 0.55) / 0.7)) if z <= ZB else max(0.05, NOSE - (z - ZB) * 0.62)
    return (X * math.cos(th), yj + f * d * math.sin(th), z)

def nose(r, yj, f):
    """The rounded, raked nose built on the join plane yj, facing f (-1: toward -Y)."""
    ths = [i * math.pi / 24 for i in range(25)]                       # 0 .. pi: from the +x side round the front to -x
    for k in range(len(HALF) - 1):
        rows = [[nose_point(HALF[kk][0], HALF[kk][1], th, yj, f) for th in ths] for kk in (k, k + 1)]
        col = BAND(k)
        if col == 'window': col = 'glass_t'
        grid('nose_%d' % k, rows, col, r, solid=0.05, rough=0.15 if col == 'glass_t' else 0.75)
    # windscreen frames along the sill and the top of the glass, three posts between the panes, two wipers
    for z in (ZB + 0.01, ZW - 0.01):
        tube('screen_rail', [nose_point(xat(z) + 0.012, z, th, yj, f) for th in ths[2:23]], 0.035, 'trim', r)
    for th in (math.radians(32), math.pi / 2, math.radians(148)):
        tube('screen_post', [nose_point(xat(z) + 0.015, z, th, yj, f) for z in (ZB, (ZB + ZW) / 2, ZW)], 0.045, 'trim', r)
    for th in (math.radians(68), math.radians(112)):
        p = nose_point(xat(ZB + 0.12) + 0.03, ZB + 0.12, th, yj, f)
        q = nose_point(xat(ZB + 0.55) + 0.03, ZB + 0.55, th + 0.12 * (1 if th < 1.57 else -1), yj, f)
        tube('wiper', [p, q], 0.012, 'iron', r)
    for z in (0.95, 1.2, 1.45, 1.7):                                  # ribs round the lower nose
        tube('nose_rib', [nose_point(xat(z) + 0.012, z, th, yj, f) for th in ths], 0.014, 'lower_dark', r)
    for th in (math.radians(52), math.radians(128)):                  # two headlights low on the nose, marker lamps
        x, y, z = nose_point(xat(1.25) + 0.05, 1.25, th, yj, f)
        cyl('head_body', 0.15, 0.13, 0.14, (x, y, z - 0.07), (f * -90, 0, 0), 'iron', r, bevel=0.03, verts=20)
        ball('head_light', 0.11, (x, y + f * 0.1, z), (1, 0.45, 1), 'lamp_t', r, emit=4.0 if f < 0 else 0.5)
        mx, my, mz = nose_point(xat(1.75) + 0.03, 1.75, th + (0.35 if th < 1.57 else -0.35), yj, f)
        ball('marker', 0.05, (mx, my, mz), (1, 0.6, 1), 0xFF6A4A, r, emit=1.2)
    px, py, pz = nose_point(0, 1.45, math.pi / 2, yj, f)                # a name plate with three painted marks
    box('plate', (0.62, 0.05, 0.36), (px, py + f * 0.02, pz - 0.18), color='trim', parent=r, bevel=0.03)
    box('plate_face', (0.52, 0.03, 0.26), (px, py + f * 0.045, pz - 0.13), color='upper_pale', parent=r, bevel=0.02)
    for k in range(3): box('plate_mark', (0.08, 0.02, 0.14), (px - 0.14 + k * 0.14, py + f * 0.06, pz - 0.08), color='trim', parent=r, bevel=0.005)
    rx, ry, rz = nose_point(0, 3.18, math.pi / 2, yj, f)                # the roof headlight
    cyl('roof_lamp', 0.17, 0.15, 0.24, (rx, ry - f * 0.12, rz + 0.05), (f * -90, 0, 0), 'iron', r, bevel=0.03, verts=22)
    ball('roof_light', 0.13, (rx, ry + f * 0.02, rz + 0.05), (1, 0.4, 1), 'lamp_t', r, emit=6.0 if f < 0 else 0.6)
    bx, by, bz = nose_point(0, 0.6, math.pi / 2, yj, f)                 # bumper, buffers, coupler
    box('bumper', (2.0, 0.24, 0.24), (0, by + f * 0.04, 0.36), color='iron', parent=r, bevel=0.08)
    for sx in (-1, 1): cyl('buffer', 0.12, 0.12, 0.2, (sx * 0.72, by + f * 0.15, 0.48), (f * -90, 0, 0), 'iron', r, bevel=0.03, verts=16)
    box('coupler', (0.28, 0.4, 0.18), (0, by + f * 0.12, 0.32), color='iron', parent=r, bevel=0.05)

def car(r, y0, flip):
    f = 1 if flip else -1                                              # the nose points this way
    yj = (y0 + L - NOSE) if flip else (y0 + NOSE)                      # where the nose joins the body
    ye = y0 if flip else y0 + L                                        # the coupling end
    ya, yb = min(yj, ye), max(yj, ye)
    yc = (ya + yb) / 2
    inward = 1 if ye < yj else -1                                      # from the coupling end toward the middle of the car
    # ---------- shell: lower sides, window band (only between windows), cream strip, roof ----------
    for side in (-1, 1): loft('lower', band_rows(0, 3, side), ya, yb, 'lower', r, solid=0.05)
    loft('upper', across(4, 10), ya, yb, 'upper', r, solid=0.05)
    loft('roof', [(x * 1.006, z + 0.006) for x, z in across(5, 10)], ya, yb, 'roof_t', r, solid=0.04)
    doors = (ya + 1.05, yb - 1.05)
    n = 13; w0, w1 = ya + 1.95, yb - 1.95; step = (w1 - w0) / n; PW = 0.34; ww = step - PW     # small windows, wide pillars
    solids = [(ya, w0 + PW / 2)] + [(w0 + i * step - PW / 2, w0 + i * step + PW / 2) for i in range(1, n)] + [(w1 - PW / 2, yb)]
    for side in (-1, 1):
        for a, b in solids: loft('pillar', band_rows(3, 4, side), a, b, 'upper', r, solid=0.05)
        x0, x1 = side * HALF[3][0], side * HALF[4][0]
        for i in range(n):                                             # wood frames, a glazing bar and lower-sash glass
            cy = w0 + (i + 0.5) * step
            for z, x in ((ZB + 0.02, x0), (ZW - 0.02, x1)): box('win_rail', (0.07, ww + 0.02, 0.04), (x * 0.985, cy, z - 0.02), color='trim', parent=r, bevel=0.01)
            box('win_bar', (0.05, ww, 0.03), ((x0 + x1) / 2 * 0.985, cy, ZB + (ZW - ZB) * 0.5), (0, side * 4.5, 0), 'trim', r, bevel=0.008)
            box('glass', (0.015, ww, (ZW - ZB) * 0.47), ((x0 + x1) / 2 * 0.975, cy, ZB + 0.03), (0, side * 4.5, 0), 'glass_t', r, bevel=0, rough=0.1)
        for dy in doors:                                               # doors: cream panel, window, kick plate, step, grab handles
            xd = side * (HALF[2][0] + 0.015)
            box('door', (0.04, 0.95, ZW - 0.6), (xd, dy, 0.6), color='upper', parent=r, bevel=0.02)
            box('door_window', (0.05, 0.5, 0.62), (xd + side * 0.01, dy, ZB + 0.02), color='glass_t', parent=r, bevel=0.02, rough=0.15)
            box('door_kick', (0.05, 0.95, 0.16), (xd + side * 0.01, dy, 0.6), color='lower_dark', parent=r, bevel=0.01)
            box('step', (0.24, 0.9, 0.05), (side * 1.42, dy, 0.42), color='iron', parent=r, bevel=0.015)
            for o in (-0.56, 0.56): tube('grab', [(side * 1.43, dy + o, 1.1), (side * 1.45, dy + o, 1.4), (side * 1.43, dy + o, 1.75)], 0.016, 'brass_t', r, rough=0.3)
        for z in (0.95, 1.2, 1.45, 1.7):                               # horizontal ribs along the lower body, broken at the doors
            xr = side * (xat(z) + 0.012)
            for a, b in ((ya + 0.05, doors[0] - 0.5), (doors[0] + 0.5, doors[1] - 0.5), (doors[1] + 0.5, yb - 0.05)):
                tube('rib', [(xr, a, z), (xr, b, z)], 0.014, 'lower_dark', r)
        tube('drip_rail', [(side * 1.285, ya, 2.9), (side * 1.285, yb, 2.9)], 0.02, 'roof_box', r)
        box('number_plate', (0.03, 0.42, 0.16), (side * (xat(1.35) + 0.015), yc, 1.27), color='upper_pale', parent=r, bevel=0.01)
    nose(r, yj, f)
    # ---------- roof: ventilators with lids, a horn ----------
    for dy, ln in ((-4.2, 1.6), (0.0, 2.8), (4.2, 1.6)):
        box('ventilator', (0.95, ln, 0.22), (0, yc + dy, 3.27), color='roof_box', parent=r, bevel=0.09)
        box('vent_lid', (1.08, ln + 0.1, 0.05), (0, yc + dy, 3.47), color='roof_t', parent=r, bevel=0.02)
    cyl('horn', 0.05, 0.1, 0.32, (0.55, yj - f * 0.6, 3.3), (f * -90, 0, 0), 'brass_t', r, bevel=0.01, rough=0.3)
    # ---------- the coupling end: a wall in the shape of the cross-section, with an arched doorway cut through ----------
    def resample(pts, n):
        seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]; tot = sum(seg); out = []
        for k in range(n):
            t, i = tot * k / (n - 1), 0
            while i < len(seg) - 1 and t > seg[i]: t -= seg[i]; i += 1
            a, b = pts[i], pts[i + 1]; u = min(1, t / seg[i]) if seg[i] else 0
            out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
        return out
    door = [(-0.4, 0.85), (-0.4, 2.3)] + [(-math.cos(t) * 0.4, 2.3 + math.sin(t) * 0.4) for t in [k * math.pi / 12 for k in range(1, 12)]] + [(0.4, 2.3), (0.4, 0.85)]
    outer, inner = resample(across(0, 10), 49), resample(door, 49)
    grid('end_wall', [[(x, ye, z) for x, z in outer], [(x, ye, z) for x, z in inner]], 'wall_in', r, solid=0.06)
    tube('arch_frame', [(math.cos(a) * 0.42, ye + inward * 0.04, 2.3 + math.sin(a) * 0.42) for a in [k * math.pi / 10 for k in range(11)]], 0.045, 'wain', r)
    for sx in (-1, 1): box('arch_jamb', (0.08, 0.1, 1.45), (sx * 0.42, ye + inward * 0.04, 0.85), color='wain', parent=r, bevel=0.01)
    # ---------- inside ----------
    zf = 0.85
    for i in range(int((yb - ya - 0.4) / 0.16)):                       # plank floor
        box('plank', (2.5, 0.155, 0.04), (0, ya + 0.3 + i * 0.16, zf - 0.04), color='plank' if (i * 7) % 3 else 'plank_dark', parent=r, bevel=0.004)
    for side in (-1, 1):
        xi = side * 1.31
        box('wainscot', (0.03, yb - ya - 0.3, ZB - zf), (xi, yc, zf), color='wain', parent=r, bevel=0)
        for z in (zf + 0.02, ZB - 0.06): box('wain_rail', (0.05, yb - ya - 0.3, 0.05), (xi - side * 0.01, yc, z), color='wain_dark', parent=r, bevel=0.01)
        box('sill_in', (0.12, yb - ya - 0.3, 0.05), (xi - side * 0.04, yc, ZB - 0.02), color='wain_dark', parent=r, bevel=0.01)
        a, b = doors[0] + 0.6, doors[1] - 0.6                          # a long bench between the doors
        ln, cy = b - a, (a + b) / 2
        box('bench_base', (0.5, ln, 0.38), (side * 1.0, cy, zf), color='wain', parent=r, bevel=0.03)
        box('bench_kick', (0.02, ln - 0.1, 0.24), (side * 0.745, cy, zf + 0.07), color='wain_dark', parent=r, bevel=0.005)
        box('bench_seat', (0.56, ln, 0.13), (side * 1.0, cy, zf + 0.38), color='cushion', parent=r, bevel=0.06)
        box('bench_back', (0.13, ln, 0.6), (side * 1.24, cy, zf + 0.5), (0, side * -6, 0), 'cushion_dark', r, bevel=0.06)
        for e in (a, b):                                               # wooden end panel, a grab pole, a rail to the wall
            box('bench_end', (0.6, 0.05, 0.9), (side * 0.98, e, zf), color='wain', parent=r, bevel=0.02)
            tube('pole', [(side * 0.68, e, zf), (side * 0.68, e, 2.98)], 0.022, 'pole', r)
            tube('end_rail', [(side * 0.68, e, 1.65), (side * 1.3, e, 1.65)], 0.018, 'pole', r)
        for i in range(int((yb - ya - 1) / 1.15) + 1):                 # overhead luggage rack: brackets and three rods
            by = ya + 0.6 + i * 1.15
            tube('rack_bracket', [(side * 1.25, by, 2.74), (side * 1.02, by, 2.82), (side * 0.95, by, 2.84)], 0.016, 'rack', r)
            tube('rack_stay', [(side * 1.22, by, 2.95), (side * 1.02, by, 2.83)], 0.012, 'rack', r)
        for x in (0.95, 1.05, 1.15):
            tube('rack_rod', [(side * x, ya + 0.5, 2.84 - (x - 0.95) * 0.3), (side * x, yb - 0.5, 2.84 - (x - 0.95) * 0.3)], 0.012, 'rack', r)
        tube('strap_rail', [(side * 0.62, ya + 0.6, 3.02), (side * 0.62, yb - 0.6, 3.02)], 0.02, 'pole', r)
        for i in range(14):                                            # ring straps
            sy = ya + 1.0 + i * (yb - ya - 2.0) / 13
            tube('strap', [(side * 0.62, sy, 3.0), (side * 0.62, sy, 2.66)], 0.01, 'ring', r)
            tube('strap_ring', [(side * 0.62, sy + math.sin(t) * 0.075, 2.59 + math.cos(t) * 0.075) for t in [k * math.pi / 6 for k in range(13)]], 0.012, 'ring', r)
        for a2, b2 in solids[1:-1]: box('pillar_in', (0.03, b2 - a2 + 0.04, ZW - ZB), (side * 1.3, (a2 + b2) / 2, ZB), color='wain', parent=r, bevel=0.005)
        for i in range(n): box('win_in', (0.03, step - 0.12, 0.05), (side * 1.3, w0 + (i + 0.5) * step, ZW - 0.02), color='wain', parent=r, bevel=0.005)
    loft('ceiling', [(x * 0.93, z - 0.1) for x, z in across(5, 10)], ya + 0.1, yb - 0.1, 'ceil', r)      # starts above the windows
    for i in range(4):                                                 # round lamps with brass rims, vent grilles
        cy = ya + 2.0 + i * (yb - ya - 4) / 3
        cyl('lamp_rim', 0.2, 0.2, 0.03, (0, cy, 3.12), color='brass_t', parent=r, bevel=0.01, verts=24, rough=0.3)
        ball('lamp_dome', 0.17, (0, cy, 3.1), (1, 1, 0.45), 'lamp_t', r, emit=3.0)
        box('grille', (0.6, 0.35, 0.02), (0, cy + (yb - ya - 4) / 6, 3.16), color='wain_dark', parent=r, bevel=0.005)
    wy = ye + inward * 0.05                                            # the inner face of the end wall
    for sx in (-1, 1):
        box('end_wain', (0.85, 0.03, ZB - zf), (sx * 0.86, wy, zf), color='wain', parent=r, bevel=0)
        box('picture', (0.36, 0.03, 0.46), (sx * 0.86, wy + inward * 0.02, 2.15), color='wain_dark', parent=r, bevel=0.01)
        box('picture_in', (0.28, 0.03, 0.36), (sx * 0.86, wy + inward * 0.035, 2.2), color=0x4F6F7A if sx < 0 else 0xC9A06A, parent=r, bevel=0.005)
    box('door_sign', (0.4, 0.04, 0.1), (0, wy + inward * 0.03, 2.85), color='lamp_t', parent=r, bevel=0.01, emit=1.5)
    # ---------- running gear ----------
    box('skirt_frame', (2.3, yb - ya - 1.2, 0.3), (0, yc, 0.3), color='iron', parent=r, bevel=0.04)
    for by in (ya + 2.6, yb - 2.6):
        box('bogie', (1.9, 2.2, 0.28), (0, by, 0.16), color='iron', parent=r, bevel=0.06)
        for sx in (-1, 1):
            box('bogie_side', (0.1, 2.4, 0.22), (sx * 0.98, by, 0.22), color='iron', parent=r, bevel=0.04)
            box('spring', (0.13, 0.42, 0.16), (sx * 1.0, by, 0.42), color='iron', parent=r, bevel=0.04)
            for dy in (-0.68, 0.68):
                cyl('wheel', 0.34, 0.34, 0.1, (sx * 0.68 - 0.05, by + dy, 0.34), (0, 90, 0), 'iron', r, bevel=0.02, verts=22)
                cyl('hub', 0.11, 0.1, 0.04, (sx * 0.84, by + dy, 0.34), (0, 90, 0), 'brass_t', r, bevel=0.01, rough=0.4)
    for y, w in ((yc - 1.2, 1.5), (yc + 1.0, 1.0)): box('equipment', (1.6, w, 0.36), (0, y, 0.12), color=0x3A3A40, parent=r, bevel=0.06)

def build():
    PAL.update(COLOURS)
    r = root('seatrain')
    glass_tm = lambda: None
    car(r, 0.0, False)
    car(r, L + GAP, True)
    for sx in (-1, 1): box('bellows', (0.06, GAP + 0.2, 2.25), (sx * 0.72, L + GAP / 2, 0.75), color='iron', parent=r, bevel=0.02)
    box('bellows_top', (1.5, GAP + 0.2, 0.08), (0, L + GAP / 2, 3.0), color='iron', parent=r, bevel=0.02)
    box('passage_floor', (1.38, GAP + 0.2, 0.04), (0, L + GAP / 2, 0.81), color='plank', parent=r, bevel=0.005)
    for m in bpy.data.materials:                                       # all glass: clear, so the cabin shows through
        if m.name.startswith('c_31414f') and m.node_tree:
            b = m.node_tree.nodes['Principled BSDF']; b.inputs['Transmission Weight'].default_value = 0.9; b.inputs['Roughness'].default_value = 0.05
    return r
