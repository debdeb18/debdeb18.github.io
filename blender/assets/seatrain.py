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
from mathutils import Matrix, Vector
import lib
from lib import *

VIEW = dict(angle=35, lift=0.22, res=(1300, 820))
L, GAP, NOSE = 14.0, 0.8, 0.7                     # car length (nose tip to coupling end), gap between cars, nose depth
ZB, ZW = 1.95, 2.6                                 # window band: bottom and top
COLOURS = dict(lower=0xC9573E, lower_dark=0x9E3D2F, upper=0xF2C85E, upper_pale=0xF8E6AE, roof_t=0x8E3B31, roof_box=0x7B3129,
               trim=0x3A2A26, glass_t=0x31414F, lamp_t=0xFFE2A0, plank=0xA0683C, plank_dark=0x7E4C2A, wain=0x6E4428, wain_dark=0x5A3720,
               cushion=0xD9707A, cushion_dark=0xB9505C, wall_in=0xF2DDB8, ceil=0xF6E6C8, pole=0x8A6A48, brass_t=0xD9A441,
               ring=0xEDE2C8, iron=0x2E2D33, rack=0x5E4A3A, amber=0xFFA43A, slat_line=0x7E2F24, screen=0x2A3440)
# the wood-and-brass scheme of the close-up reference: brown slatted lower body, tan upper, dark brown roof
FILM = dict(lower=0xC9573E, lower_dark=0x9E3D2F, upper=0xF2C85E, upper_pale=0xF8E6AE, roof_t=0x8E3B31, roof_box=0x7B3129, skirt=0x7E2F24)
WOOD = dict(lower=0x7A3B26, lower_dark=0x5C2A1B, slat_line=0x4E2416, upper=0xC9A066, upper_pale=0xE9D2A2, roof_t=0x4A2E28, roof_box=0x3E2622)
import os
# default: the cream-and-brown of the toy references
COLOURS.update(lower=0x9C5B33, lower_dark=0x7A4326, upper=0xF2D98C, upper_pale=0xFBF0CF, roof_t=0x7B3F2A, roof_box=0x6A3624, skirt=0x6B3A22,
               silver=0xC9CCD1, lamp_red=0xE04A3A)
if os.environ.get('LIVERY') == 'wood': COLOURS.update(WOOD)
if os.environ.get('LIVERY') == 'film': COLOURS.update(FILM)

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

def grid(name, rows, color, parent, solid=0.0, flat=False, **mk):
    """A smooth surface through a grid of 3D points (rows x cols), optionally given thickness."""
    bm = bmesh.new(); vs = [[bm.verts.new(p) for p in row] for row in rows]
    for i in range(len(rows) - 1):
        for j in range(len(rows[0]) - 1):
            try: bm.faces.new((vs[i][j], vs[i][j + 1], vs[i + 1][j + 1], vs[i + 1][j]))
            except ValueError: pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bm.normal_update()
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = lib._finish(name, me, color, (0, 0, 0), (0, 0, 0), parent, 0, **mk)
    if flat:                                                       # crisp facets (no smoothing) for the slats
        for pl in o.data.polygons: pl.use_smooth = False
        for m in list(o.modifiers):
            if m.type == 'WEIGHTED_NORMAL': o.modifiers.remove(m)
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

WEDGE = 1.3                                        # how far the point of the nose sticks out (about the half-width: a 45 degree wedge)

def nose_point(X, z, th, yj, f):
    """A point on the nose. From above it is a gentle oval. From the side it is a trapezium: upright below the waist, the
    windscreen leaning well back, and the roof overhanging forward again as a brow."""
    plan = math.sin(th)                                                      # an ellipse: 1 at the front, 0 at the sides
    D = 0.62
    if z <= ZB: d = D * (0.9 + 0.1 * min(1, (z - 0.55) / 0.5))
    elif z <= ZW: d = D - (z - ZB) / (ZW - ZB) * 0.42                          # the windscreen leans back
    elif z <= 2.95: d = D - 0.42 + (z - ZW) / (2.95 - ZW) * 0.5                # the brow comes forward again
    else: d = (D + 0.08) * max(0.0, (3.31 - z) / (3.31 - 2.95)) ** 0.7        # and the roof rounds over it
    d += max(0.0, X - xat(z))                                                 # anything set proud of the body stands proud at the front too
    return (X * math.cos(th), yj + f * d * plan, z)

def nose(r, yj, f):
    """The front, after the close-up reference: a rounded V, two big rounded windscreen panes in thick bezels, an
    overhanging brow with one headlight, vertical slats below, a name plate, amber lamps, a pale skirt with buffers."""
    N = 72
    ths = [i * math.pi / N for i in range(N + 1)]                     # 0 .. pi: from the +x side round the front to -x
    for k in range(len(HALF) - 1):
        col = BAND(k)
        if k == 0: col = 'skirt'                                       # the dark skirt
        if col == 'window': col = 'upper'                              # the bezel colour; the glass goes on top
        if k in (1, 2):                                                # vertical slats: every other column stands proud
            rows = [[nose_point(HALF[kk][0] + (0.035 if (i // 2) % 2 else 0), HALF[kk][1], th, yj, f) for i, th in enumerate(ths)] for kk in (k, k + 1)]
        else:
            rows = [[nose_point(HALF[kk][0], HALF[kk][1], th, yj, f) for th in ths] for kk in (k, k + 1)]
        grid('nose_%d' % k, rows, col, r, solid=0.05, flat=k in (1, 2))
    # two big windscreen panes with rounded corners, on either side of a centre post
    za, zb = ZB + 0.06, ZW - 0.02
    for t0, t1 in ((math.radians(22), math.radians(84)), (math.radians(96), math.radians(158))):
        gth = [t0 + (t1 - t0) * i / 16 for i in range(17)]
        gz = [za + (zb - za) * i / 6 for i in range(7)]
        grid('windscreen', [[nose_point(xat(z) + 0.04, z, th, yj, f) for th in gth] for z in gz], 'screen', r, rough=0.08)
        tm, zm, a, b = (t0 + t1) / 2, (za + zb) / 2, (t1 - t0) / 2, (zb - za) / 2
        bez = []
        for k in range(49):                                              # a rounded rectangle (superellipse) traced on the surface
            u = k / 48 * 2 * math.pi; cu, su = math.cos(u), math.sin(u)
            pw = 0.25 if su < 0 else 0.6                                     # square-ish bottom corners, round top corners
            th = tm + a * math.copysign(abs(cu) ** pw, cu); z = zm + b * math.copysign(abs(su) ** pw, su)
            bez.append(nose_point(xat(z) + 0.03, z, th, yj, f))
        tube('bezel', bez, 0.055, 'upper_pale', r)
    tube('centre_post', [nose_point(xat(z) + 0.03, z, math.pi / 2, yj, f) for z in (ZB + 0.02, (ZB + ZW) / 2, ZW - 0.02)], 0.06, 'upper_pale', r)
    for th in (math.radians(50), math.radians(130)):                   # wipers
        p = nose_point(xat(za + 0.05) + 0.05, za + 0.05, th, yj, f); q = nose_point(xat(za + 0.45) + 0.05, za + 0.45, th + 0.18 * (1 if th < 1.57 else -1), yj, f)
        tube('wiper', [p, q], 0.012, 'iron', r)
    # the brow: the roof edge overhangs the windscreen, with a round headlight on top in the middle
    tube('brow', [nose_point(xat(ZW + 0.1) + 0.07, ZW + 0.1, th, yj, f) for th in ths[4:-4]], 0.06, 'roof_t', r)
    hx, hy, hz = nose_point(xat(ZW + 0.2), ZW + 0.2, math.pi / 2, yj, f)
    cyl('head_body', 0.19, 0.17, 0.26, (hx, hy - f * 0.18, hz + 0.1), (f * -90, 0, 0), 'iron', r, bevel=0.03, verts=24)
    cyl('head_rim', 0.17, 0.17, 0.04, (hx, hy + f * 0.07, hz + 0.1), (f * -90, 0, 0), 'brass_t', r, bevel=0.01, verts=24, rough=0.3)
    ball('headlight', 0.14, (hx, hy + f * 0.11, hz + 0.1), (1, 0.4, 1), 'lamp_t', r, emit=6.0 if f < 0 else 0.6)
    # the lower front: a vertical name plate on the centre, a small amber lamp on each side
    px, py, pz = nose_point(xat(1.55) + 0.06, 1.55, math.pi / 2, yj, f)
    box('plate', (0.3, 0.05, 0.6), (px, py, pz - 0.3), color='lamp_red', parent=r, bevel=0.03)
    box('plate_face', (0.24, 0.03, 0.52), (px, py + f * 0.025, pz - 0.26), color='upper_pale', parent=r, bevel=0.02)
    for k in range(2): box('plate_mark', (0.12, 0.02, 0.16), (px, py + f * 0.04, pz - 0.16 - k * 0.22), color='lamp_red', parent=r, bevel=0.005)
    tube('belt', [nose_point(xat(ZB - 0.03) + 0.045, ZB - 0.03, th, yj, f) for th in ths], 0.03, 'silver', r, rough=0.3)   # the silver waist strip
    for th in (math.radians(58), math.radians(122)):
        sx = 1 if th < math.pi / 2 else -1
        n = Vector((sx * WEDGE, f * xat(1.6), 0)).normalized()
        x, y, z = nose_point(xat(1.6) + 0.03, 1.6, th, yj, f)
        lb = cyl('lamp_body', 0.1, 0.09, 0.08, (x, y, z), (0, 0, 0), 'silver', r, bevel=0.02, verts=16, rough=0.3); lb.rotation_euler = n.to_track_quat('Z', 'Y').to_euler()
        ball('red_lamp', 0.065, (x + n.x * 0.08, y + n.y * 0.08, z), (1, 1, 1), 'lamp_red', r, emit=2.0)
    # the skirt: big round buffers and a coupler
    bx, by, bz = nose_point(xat(0.6), 0.6, math.pi / 2, yj, f)
    for sx in (-1, 1):
        n = Vector((sx * WEDGE, f * xat(0.6), 0)).normalized()
        x, y, z = nose_point(xat(0.62), 0.62, math.radians(62 if sx > 0 else 118), yj, f)
        st = cyl('buffer_stem', 0.07, 0.07, 0.2, (x, y, 0.5), (0, 0, 0), 'iron', r, bevel=0.01, verts=12); st.rotation_euler = n.to_track_quat('Z', 'Y').to_euler()
        ball('buffer', 0.17, (x + n.x * 0.22, y + n.y * 0.22, 0.5), (1, 1, 1), 'iron', r, rough=0.4)
    box('coupler', (0.32, 0.45, 0.2), (0, by + f * 0.15, 0.32), color='iron', parent=r, bevel=0.05)

def car(r, y0, flip):
    f = 1 if flip else -1                                              # the nose points this way
    yj = (y0 + L - NOSE) if flip else (y0 + NOSE)                      # where the nose joins the body
    ye = y0 if flip else y0 + L                                        # the coupling end
    ya, yb = min(yj, ye), max(yj, ye)
    yc = (ya + yb) / 2
    inward = 1 if ye < yj else -1                                      # from the coupling end toward the middle of the car
    # ---------- shell: lower sides, window band (only between windows), cream strip, roof ----------
    for side in (-1, 1):
        loft('skirt', band_rows(0, 1, side), ya, yb, 'skirt', r, solid=0.05)
        loft('lower', band_rows(1, 3, side), ya, yb, 'lower', r, solid=0.05)
    loft('upper', across(4, 10), ya, yb, 'upper', r, solid=0.05)
    loft('roof', [(x * 1.006, z + 0.006) for x, z in across(5, 10)], ya, yb, 'roof_t', r, solid=0.04)
    doors = (ya + 1.05, yb - 1.05)
    n = 10; w0, w1 = ya + 1.95, yb - 1.95; step = (w1 - w0) / n; PW = 0.26; ww = step - PW     # near-square windows
    solids = [(ya, w0 + PW / 2)] + [(w0 + i * step - PW / 2, w0 + i * step + PW / 2) for i in range(1, n)] + [(w1 - PW / 2, yb)]
    for side in (-1, 1):
        for a, b in solids: loft('pillar', band_rows(3, 4, side), a, b, 'upper', r, solid=0.05)
        x0, x1 = side * HALF[3][0], side * HALF[4][0]
        for i in range(n):                                             # wood frames, a glazing bar and lower-sash glass
            cy = w0 + (i + 0.5) * step
            for z, x in ((ZB + 0.02, x0), (ZW - 0.02, x1)): box('win_rail', (0.07, ww + 0.02, 0.04), (x * 0.985, cy, z - 0.02), color='trim', parent=r, bevel=0.01)
            box('glass', (0.015, ww, ZW - ZB - 0.04), ((x0 + x1) / 2 * 0.975, cy, ZB + 0.02), (0, side * 4.5, 0), 'glass_t', r, bevel=0, rough=0.1)
        for dy in doors:                                               # doors: cream panel, window, kick plate, step, grab handles
            xd = side * (HALF[2][0] + 0.015)
            box('door', (0.04, 0.95, ZW - 0.6), (xd, dy, 0.6), color='upper', parent=r, bevel=0.02)
            box('door_window', (0.05, 0.5, 0.62), (xd + side * 0.01, dy, ZB + 0.02), color='glass_t', parent=r, bevel=0.02, rough=0.15)
            box('door_kick', (0.05, 0.95, 0.16), (xd + side * 0.01, dy, 0.6), color='lower_dark', parent=r, bevel=0.01)
            box('step', (0.24, 0.9, 0.05), (side * 1.42, dy, 0.42), color='iron', parent=r, bevel=0.015)
            for o in (-0.56, 0.56): tube('grab', [(side * 1.43, dy + o, 1.1), (side * 1.45, dy + o, 1.4), (side * 1.43, dy + o, 1.75)], 0.016, 'brass_t', r, rough=0.3)
        # vertical slats along the lower body: a corrugated panel, every other strip standing proud
        for a, b in ((ya + 0.05, doors[0] - 0.5), (doors[0] + 0.5, doors[1] - 0.5), (doors[1] + 0.5, yb - 0.05)):
            ys = [a + k * 0.06 for k in range(int((b - a) / 0.06) + 1)]
            cols = [[(side * (x + 0.012 + (0.03 if (k // 2) % 2 else 0)), y, z) for k, y in enumerate(ys)] for x, z in HALF[1:4]]
            grid('slats', cols, 'lower', r, flat=True)
        tube('drip_rail', [(side * 1.285, ya, 2.9), (side * 1.285, yb, 2.9)], 0.02, 'roof_box', r)
        tube('belt', [(side * (xat(ZB - 0.03) + 0.045), ya, ZB - 0.03), (side * (xat(ZB - 0.03) + 0.045), yb, ZB - 0.03)], 0.03, 'silver', r, rough=0.3)
        box('number_plate', (0.03, 0.42, 0.16), (side * (xat(1.35) + 0.015), yc, 1.27), color='upper_pale', parent=r, bevel=0.01)
    nose(r, yj, f)
    # ---------- roof: ventilators with lids, a horn ----------
    # roof: one long low raised panel in the middle, a round mushroom ventilator toward each end
    box('roof_panel', (1.0, 5.0, 0.12), (0, yc, 3.27), color='roof_box', parent=r, bevel=0.05)
    for dy in (-4.6, 4.6):
        cyl('vent_stem', 0.16, 0.16, 0.12, (0, yc + dy, 3.26), color='roof_box', parent=r, bevel=0.02, verts=20)
        ball('vent_cap', 0.24, (0, yc + dy, 3.38), (1, 1, 0.4), 'roof_t', r)
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
