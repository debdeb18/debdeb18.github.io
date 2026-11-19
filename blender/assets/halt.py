"""The porch (halt), after the user's sketch: built on the old stone pier of a ruin standing in the sea beside the
line, beside the broken stump of a round tower; on its worn floor slabs, a
white fence along the back and the left end; along the back an info and timetable board, a lamp post and the waiting spot (an open
shelter with a tiled roof, a row of four seats and a bin, a lamp on each front post); steps down at the right
end to a small side jetty with a mooring post; and a railway-crossing signal at the front left.
Origin: centre of the platform's footprint at water level; the track side faces -Y; the top is at z = TOP."""
import math, random
import bpy, bmesh
from lib import *

VIEW = dict(angle=-28, lift=0.5, res=(1300, 820), samples=24)
LX, LY, TOP, BASE = 11.0, 4.6, 0.95, -1.2          # length, depth, top height, how far the block reaches down
COLOURS = dict(stone_a=0xE6E0CF, stone_b=0xD8D2C0, stone_c=0xEFEBDF, stone_d=0xD2D3C1, ivy_a=0x3F7A3A, ivy_b=0x5C9A45, grass_top=0x7DB85A, bush_a=0x4F8A3E, bush_b=0x6BA34A, moss_a=0x6F9A4C, moss_b=0x8DB463, tile_d=0xC2C1A8, tile_e=0xE9E0C9, joint=0x8D8878, tile_a=0xD8CBB0, tile_b=0xCDBF9F, tile_c=0xE2D7BE,
               coping=0xEFE6D2, rail_w=0xF4F1EA, timber=0x8A5A3C, timber_dark=0x5C3B28, roof=0xB8573E, roof_dark=0x8E3F2C,
               bench_w=0xA57A4E, seat_wood=0xA0623A, seat_frame=0x2F3036, vend_body=0xE0602F, vend_dark=0x5A2A1E, vend_glow=0xFFE6B0, button_lit=0xFFF4D8, lamp_w=0xFFE2A0, board=0xF3EAD2, iron_d=0x2E2D33,
               stripe_y=0xF2C230, stripe_k=0x26262A, red_l=0xE0453A, plank=0xA07650, plank_d=0x7E5A3A)

def stone(r, rnd, l, h, at, axis, fixed, color, moss=0.0):
    """One wall stone, laid a little unevenly: it sticks out by its own amount and sits a touch askew; now and then it
    is cracked in two. `at` is its centre along the face and its base height."""
    a, z = at; out = 1 if fixed > 0 else -1
    pos = fixed + out * rnd.uniform(0.0, 0.02)                                  # some stones stand proud of the others
    tilt, yaw = rnd.uniform(-1.2, 1.2), rnd.uniform(-1.0, 1.0)
    if axis == 'x': size, loc, rot = (l - 0.03, 0.06, h - 0.03), (a, pos, z), (0, tilt, yaw)
    else: size, loc, rot = (0.06, l - 0.03, h - 0.03), (pos, a, z), (tilt, 0, yaw)
    kw = dict(color=color, parent=r, bevel=0.025, jitter=0.008, along=axis, face=out, rough=1.8, moss=moss)
    if rnd.random() < 0.16 and l > 0.45:                                         # cracked in two, nearly upright
        k, t = rnd.uniform(-0.25, 0.25), rnd.uniform(-0.5, 0.5)
        n = (math.cos(t), 0, math.sin(t)) if axis == 'x' else (0, math.cos(t), math.sin(t))
        g = 0.008 / (l - 0.03)
        for sgn in (1, -1):
            nn = tuple(sgn * c for c in n)
            co = (k - sgn * g, 0, 0) if axis == 'x' else (0, k - sgn * g, 0)
            painted_box('stone', size, loc, rot, clip=(co, nn), **kw)
    else:
        painted_box('stone', size, loc, rot, **kw)

def stone_face(r, rnd, along, fixed, axis):
    """Courses of cut stone on one side of the block: rows of uneven height, stones of varying length, laid by hand."""
    z = BASE; row = 0
    while z < TOP - 0.12:
        h = min(rnd.uniform(0.24, 0.38), TOP - 0.12 - z)
        if TOP - 0.12 - (z + h) < 0.16: h = TOP - 0.12 - z                       # no sliver of a course at the top
        a = -along / 2 + (rnd.uniform(0.2, 0.4) if row % 2 else 0.0)
        moss = 0.55 if row == 0 else (0.25 if row == 1 else 0.0)                   # green at the foot, by the water
        if a > -along / 2 + 0.01:
            stone(r, rnd, a + along / 2, h, ((-along / 2 + a) / 2, z), axis, fixed, 'stone_b', moss)
        while a < along / 2 - 0.01:
            l = min(rnd.uniform(0.45, 1.0), along / 2 - a)
            if along / 2 - (a + l) < 0.2: l = along / 2 - a
            stone(r, rnd, l, h, (a + l / 2, z), axis, fixed, rnd.choice(('stone_a', 'stone_b', 'stone_c', 'stone_d')), moss)
            a += l
        z += h; row += 1

def moss_tuft(r, rnd, x, y, z, s=1.0):
    """A small cushion of moss tucked into a joint."""
    lump('moss', 0.05 * s, (x, y, z), (rnd.uniform(1.2, 2.2), rnd.uniform(1.0, 1.5), 0.6), rnd.choice(('moss_a', 'moss_b')), r, strength=0.35, grain=0.5)

def ruin_block(r, rnd, size, loc, rot, along, face, color=None, moss=0.0, crack=0.2):
    """One big old block of the ruin: weathered round its edges, chipped, sometimes cracked in two."""
    kw = dict(color=color or rnd.choice(('stone_a', 'stone_b', 'stone_c', 'stone_d')), parent=r, bevel=0.03, jitter=0.01,
              along=along, face=face, rough=2.6, moss=moss)
    if rnd.random() < crack:
        k, t = rnd.uniform(-0.25, 0.25), rnd.uniform(-0.6, 0.6)
        n = (math.cos(t), 0, math.sin(t)) if along == 'x' else (0, math.cos(t), math.sin(t))
        ax = 0 if along == 'x' else 1; g = 0.012 / size[ax]
        return [painted_box('ruin', size, loc, rot, clip=(tuple((k - sgn * g) if i == ax else 0 for i in range(3)), tuple(sgn * c for c in n)), **kw) for sgn in (1, -1)]
    return [painted_box('ruin', size, loc, rot, **kw)]

def ruin_face(r, rnd, along, fixed, axis):
    """One side of the old pier: courses of big weathered blocks, laid unevenly, a few fallen out."""
    z = BASE; row = 0; out = 1 if fixed > 0 else -1
    while z < TOP - 0.15:
        h = min(rnd.uniform(0.42, 0.58), TOP - 0.1 - z)
        if TOP - 0.1 - (z + h) < 0.25: h = TOP - 0.1 - z
        a = -along / 2 - (rnd.uniform(0.2, 0.6) if row % 2 else 0.0)
        moss = 0.6 if row == 0 else (0.3 if row == 1 else 0.0)
        while a < along / 2 - 0.05:
            l = rnd.uniform(0.7, 1.4)
            a0, a1 = max(a, -along / 2), min(a + l, along / 2); a += l
            if a1 - a0 < 0.15: continue
            if row > 0 and z + h < TOP - 0.2 and rnd.random() < 0.06: continue  # a block fallen out
            ll = a1 - a0 - 0.035; c = (a0 + a1) / 2; pos = fixed + out * rnd.uniform(-0.01, 0.04)
            tilt, yaw = rnd.uniform(-2, 2), rnd.uniform(-1.5, 1.5)
            if axis == 'x': ruin_block(r, rnd, (ll, 0.3, h - 0.035), (c, pos - out * 0.12, z), (0, tilt, yaw), 'x', out, moss=moss)
            else: ruin_block(r, rnd, (0.3, ll, h - 0.035), (pos - out * 0.12, c, z), (tilt, 0, yaw), 'y', out, moss=moss)
        z += h; row += 1

def floor_slabs(r, rnd, joints):
    """The top: big worn floor slabs of the old ruin in staggered rows, a few cracked or sunk a little."""
    y = -LY / 2 + 0.02; row = 0
    while y < LY / 2 - 0.1:
        d = min(rnd.uniform(0.75, 1.0), LY / 2 - 0.02 - y)
        if LY / 2 - 0.02 - (y + d) < 0.3: d = LY / 2 - 0.02 - y
        x = -LX / 2 + 0.02 - (rnd.uniform(0.2, 0.5) if row % 2 else 0)
        while x < LX / 2 - 0.05:
            w = rnd.uniform(0.8, 1.3); x0, x1 = max(x, -LX / 2 + 0.02), min(x + w, LX / 2 - 0.02); x += w
            if x1 - x0 < 0.2: continue
            if math.hypot((x0 + x1) / 2 - TX, y + d / 2 - TY) < TR - 0.2: continue   # inside the tower
            sz = (x1 - x0 - 0.03, d - 0.03, 0.08); loc = ((x0 + x1) / 2, y + d / 2, TOP - 0.08 + rnd.uniform(-0.012, 0.006))
            rot = (rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))
            kw = dict(color=rnd.choice(('tile_a', 'tile_b', 'tile_c', 'tile_d', 'tile_e')), parent=r, bevel=0.015, jitter=0.004, along='top', band=0.1, rough=2.2)
            if rnd.random() < 0.22:
                t = rnd.uniform(0, math.pi); n = (math.cos(t), math.sin(t), 0); k = (rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2), 0)
                for sgn in (1, -1):
                    co = (k[0] - sgn * n[0] * 0.01, k[1] - sgn * n[1] * 0.01, 0)
                    painted_box('slab', sz, loc, rot, clip=(co, tuple(sgn * c for c in n)), **kw)
            else:
                painted_box('slab', sz, loc, rot, **kw)
            if rnd.random() < 0.12: joints.append((x1, y + rnd.uniform(0.1, d - 0.1)))
        y += d; row += 1

TX, TY, TR, TW = -LX / 2 - 1.5, 0.5, 2.45, 0.6                                  # the ruined tower (centre, outer radius, wall): it overlaps the end of the pier
WINDOWS = ((115, TOP + 1.3, TOP + 2.5), (65, TOP + 2.9, TOP + 4.0), (165, TOP + 2.7, TOP + 3.8))   # (angle, sill, head)

def ivy(r, rnd, x, y, z, nx, ny, length):
    """Ivy hanging down a wall from (x, y, z): a few strands of leafy clusters pressed flat to the wall, fuller at the
    top and thinning out as they fall."""
    tx, ty = -ny, nx
    for sidx in range(rnd.randint(2, 3)):
        o = rnd.uniform(-0.25, 0.25); ln = length * rnd.uniform(0.55, 1.0); n = int(ln / 0.075)
        for i in range(n):
            f = 1 - i / n * 0.55; w = math.sin(i * 0.45 + sidx) * 0.06
            lump('ivy', rnd.uniform(0.09, 0.14) * f, (x + tx * (o + w) + nx * 0.03, y + ty * (o + w) + ny * 0.03, z - i * 0.075),
                 (1.4 if nx == 0 else 0.45, 1.4 if ny == 0 else 0.45, 1.0) if abs(nx) + abs(ny) > 0 and (abs(nx) < 0.3 or abs(ny) < 0.3) else (1.0, 1.0, 1.0),
                 rnd.choice(('ivy_a', 'ivy_b')), r, strength=0.45, grain=0.35, detail=1)

def grass_cap(r, rnd, x, y, z, w, d, yaw):
    """Grass grown over the broken top of a wall."""
    lump('grass_cap', 0.3, (x, y, z), (w / 0.55, d / 0.55, 0.3), 'grass_top', r, strength=0.3, grain=0.6, detail=2).rotation_euler = (0, 0, math.radians(yaw))

def ruin_tower(r, rnd):
    """The ruin of an old round tower at the left end, pale stone after the references: it stands high at the back, with
    a few battlements left, and is broken down low at the front; round-arched windows; grass over the broken tops and
    ivy hanging down; rubble inside and fallen blocks at its foot."""
    n = 18; z = BASE; row = 0; rm = TR - TW / 2; arc = 2 * math.pi * TR / n - 0.035
    cols = [rnd.uniform(-0.5, 0.3) for _ in range(n)]
    tops = [BASE] * n; built = []
    def top(th, k):                                                            # high at the back, ragged, low at the front
        c = max(0.0, math.cos(th - math.radians(115)))
        return TOP + 1.8 + 3.6 * c ** 0.5 + cols[k] * (0.4 + c)
    def in_window(th, z0, z1):
        for (wa, ws, wh) in WINDOWS:
            if abs(((th - math.radians(wa)) + math.pi) % (2 * math.pi) - math.pi) < 0.17 and z1 > ws and z0 < wh: return True
        return False
    while z < TOP + 5.6:
        h = rnd.uniform(0.4, 0.5); off = (0.5 if row % 2 else 0.0)
        for k in range(n):
            th = (k + off) / n * 2 * math.pi
            if z + h * 0.5 > top(th, k): continue
            if row > 1 and rnd.random() < 0.03 and not in_window(th, z - 0.6, z + h + 0.6): continue
            built.append((th, z, h, ruin_block(r, rnd, (arc, TW, h - 0.03), (TX + rm * math.cos(th), TY + rm * math.sin(th), z),
                       (rnd.uniform(-1.5, 1.5), rnd.uniform(-1.5, 1.5), math.degrees(th) - 90 + rnd.uniform(-1.5, 1.5)), 'x', 0,
                       moss=0.6 if row == 0 else (0.3 if row == 1 else 0.0), crack=0.0 if in_window(th, z - 0.6, z + h + 0.6) else 0.1)))
            tops[k] = max(tops[k], z + h)
        z += h; row += 1
    for (wa, ws, wh) in WINDOWS:                                               # cut each window: a round-arched opening
        th = math.radians(wa); ex, ey = math.cos(th), math.sin(th); tx_, ty_ = -ey, ex
        ww = 0.7; rr = ww / 2; hb = wh - ws - rr
        cutter = arch_cutter(TX + ex * rm, TY + ey * rm, ex, ey, ws, wh, ww, TW + 0.6)
        for (bt, bz, bh, objs) in built:
            if abs(((bt - th) + math.pi) % (2 * math.pi) - math.pi) < 0.45 and bz < wh + 0.05 and bz + bh > ws - 0.05:
                cut_with(objs, cutter)
        pts = [(TX + ex * (TR + 0.015) + tx_ * rr * 1.08 * math.cos(math.pi * i / 10), TY + ey * (TR + 0.015) + ty_ * rr * 1.08 * math.cos(math.pi * i / 10), ws + hb + rr * 1.08 * math.sin(math.pi * i / 10)) for i in range(11)]
        tube('arch', [(pts[0][0], pts[0][1], ws)] + pts + [(pts[-1][0], pts[-1][1], ws)], 0.045, 'stone_c', r)   # a moulding round the arch
        painted_box('sill', (ww + 0.2, TW + 0.12, 0.09), (TX + rm * ex, TY + rm * ey, ws - 0.09), (0, 0, math.degrees(th) - 90), color='stone_c', parent=r, bevel=0.02, along='x', rough=1.5)
    for k in range(n):                                                         # battlements, grass over the broken tops
        th = (k + 0.25) / n * 2 * math.pi; px, py = TX + rm * math.cos(th), TY + rm * math.sin(th)
        if tops[k] > TOP + 4.0 and k % 2 == 0:
            ruin_block(r, rnd, (arc * 0.8, TW * 0.9, 0.42), (px, py, tops[k]), (0, 0, math.degrees(th) - 90), 'x', 0, crack=0.0)
        elif tops[k] > BASE and rnd.random() < 0.75:
            grass_cap(r, rnd, px, py, tops[k] - 0.03, arc * 1.1, TW * 1.15, math.degrees(th) - 90)
    for (deg, ln) in ((135, 2.6), (95, 1.8), (150, 2.2), (60, 1.4)):            # ivy down the outside of the high wall
        th = math.radians(deg); k = int(round(deg / 360 * n - 0.25)) % n
        if tops[k] - TOP > 1.0:
            ivy(r, rnd, TX + TR * math.cos(th), TY + TR * math.sin(th), tops[k] - 0.05, math.cos(th), math.sin(th), min(ln, tops[k] - BASE - 0.5))
    for _ in range(9):                                                         # rubble and grass inside the stump
        a, d = rnd.uniform(0, 6.28), rnd.uniform(0, TR - TW - 0.3)
        rock('rubble', rnd.uniform(0.2, 0.4), (TX + d * math.cos(a), TY + d * math.sin(a), TOP - 0.2), (1.3, 1.0, 0.7), (0, 0, rnd.uniform(0, 360)), rnd.choice(('stone_a', 'stone_b', 'stone_c')), r, moss=0.3)
    grass_cap(r, rnd, TX, TY, TOP - 0.25, (TR - TW) * 1.9, (TR - TW) * 1.9, 0)
    for (a, d) in ((200, 0.5), (240, 0.8), (150, 0.3), (300, 0.6)):           # blocks fallen into the water
        ax = TX + (TR + d) * math.cos(math.radians(a)); ay = TY + (TR + d) * math.sin(math.radians(a))
        ruin_block(r, rnd, (rnd.uniform(0.6, 0.9), 0.45, 0.4), (ax, ay, BASE + 0.2), (rnd.uniform(-12, 12), rnd.uniform(-12, 12), rnd.uniform(0, 360)), 'x', 0, moss=0.5, crack=0.3)

def arch_cutter(cx, cy, nx, ny, sill, head, width, depth):
    """A hidden round-arched shape (named _cut) to cut a window through a wall facing (nx, ny) at (cx, cy)."""
    tx, ty = -ny, nx; rr = width / 2; hb = head - sill - rr
    prof = [(-rr, 0), (rr, 0), (rr, hb)] + [(rr * math.cos(math.pi * i / 12), hb + rr * math.sin(math.pi * i / 12)) for i in range(1, 12)] + [(-rr, hb)]
    bm = bmesh.new(); vs = []; col = bm.verts.layers.color.new('Col')
    for d in (-depth / 2, depth / 2):
        vs.append([bm.verts.new((cx + nx * d + tx * a, cy + ny * d + ty * a, sill + zz)) for (a, zz) in prof])
    m = len(prof); bm.faces.new(vs[0][::-1]); bm.faces.new(vs[1])
    for i in range(m): bm.faces.new((vs[0][i], vs[0][(i + 1) % m], vs[1][(i + 1) % m], vs[1][i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.verts.layers.color.remove(col)
    me = bpy.data.meshes.new('_cut'); bm.to_mesh(me); bm.free()
    at = me.color_attributes.new('Col', 'BYTE_COLOR', 'POINT')               # the same kind of colour as the blocks', so
    for d in at.data: d.color = (0.86, 0.85, 0.8, 1.0)                         # the cut carries it onto the window reveals
    me.materials.append(mat_vc('stone_c'))
    o = bpy.data.objects.new('_cut', me); bpy.context.scene.collection.objects.link(o); o.hide_render = True
    return o

def cut_with(objs, cutter):
    for o in objs:
        bo = o.modifiers.new('cut', 'BOOLEAN'); bo.operation = 'DIFFERENCE'; bo.object = cutter; bo.solver = 'EXACT'

def ruin_wall(r, rnd, x0, x1, yc, T, H, openings):
    """A tall ruined wall standing on the pier from x0 to x1 (centred at yc, T thick, H tall above the floor): courses of
    big pale blocks, its left end broken down in steps, a projecting ledge along the top, round-arched openings
    (x, sill, head) cut through it, grass on the broken tops and ivy down the front."""
    z = TOP - 0.04; row = 0; blocks = []; tops = {}
    def lim(x): return TOP + H                                             # full height all the way into the tower
    while z < TOP + H - 0.1:
        h = min(rnd.uniform(0.38, 0.48), TOP + H - z)
        a = x0 - (rnd.uniform(0.2, 0.45) if row % 2 else 0.0)
        while a < x1 - 0.05:
            l = rnd.uniform(0.6, 1.15); a0, a1 = max(a, x0), min(a + l, x1); a += l
            if a1 - a0 < 0.18: continue
            c = (a0 + a1) / 2
            if z + h * 0.5 > lim(c): continue
            objs = ruin_block(r, rnd, (a1 - a0 - 0.03, T, h - 0.03), (c, yc + rnd.uniform(-0.015, 0.015), z), (rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.8, 0.8)), 'x', 0,
                              crack=0.0 if any(abs(c - ox) < 1.0 for (ox, _, _) in openings) else 0.15)
            blocks.append((c, z, h, objs)); tops[round(c, 2)] = (c, z + h, a1 - a0)
        z += h; row += 1
    for (ox, sill, head) in openings:                                          # cut the arched openings, add sills
        cutter = arch_cutter(ox, yc, 0, -1, sill, head, 0.8, T + 0.6)
        cut_with([o for (c, bz, bh, objs) in blocks if abs(c - ox) < 1.3 and bz < head and bz + bh > sill for o in objs], cutter)
        painted_box('sill', (1.0, T + 0.12, 0.09), (ox, yc, sill - 0.09), color='stone_c', parent=r, bevel=0.02, along='x', rough=1.5)
        pts = [(ox + 0.43 * math.cos(math.pi * i / 10), yc - T / 2 - 0.015, head - 0.4 + 0.43 * math.sin(math.pi * i / 10)) for i in range(11)]
        tube('arch', [(pts[0][0], pts[0][1], sill)] + pts + [(pts[-1][0], pts[-1][1], sill)], 0.045, 'stone_c', r)
    xs = x0                                                                    # the ledge along the top
    while xs < x1 - 0.05:
        l = min(rnd.uniform(0.8, 1.3), x1 - xs)
        if l > 0.2: painted_box('ledge', (l - 0.03, T + 0.3, 0.2), (xs + l / 2, yc, TOP + H), (0, 0, rnd.uniform(-1, 1)), color='stone_c', parent=r, bevel=0.03, along='top', rough=1.8)
        xs += l
    for _ in range(6): grass_cap(r, rnd, rnd.uniform(x0 + 0.5, x1 - 0.5), yc, TOP + H + 0.17, rnd.uniform(0.6, 1.2), T + 0.2, 0)
    for xx in (x0 + 2.4, x0 + 4.3, x1 - 1.0):                                   # ivy down the front
        ivy(r, rnd, xx, yc - T / 2, TOP + H + 0.1, 0, -1, rnd.uniform(1.5, 2.6))
    return blocks

def bush(r, rnd, x, y, z, s=1.0):
    """A round leafy bush."""
    for _ in range(4):
        lump('bush', rnd.uniform(0.35, 0.5) * s, (x + rnd.uniform(-0.4, 0.4) * s, y + rnd.uniform(-0.4, 0.4) * s, z + rnd.uniform(0.2, 0.45) * s),
             (1.1, 1.1, 0.85), rnd.choice(('bush_a', 'bush_b')), r, strength=0.3, grain=0.5, detail=2)

def lantern(r, x, y, z):
    """A lantern on an iron bracket, fixed to the front of the wall."""
    tube('lantern_arm', [(x, y, z + 0.35), (x, y - 0.25, z + 0.42), (x, y - 0.35, z + 0.32)], 0.02, 'iron_d', r)
    cyl('lantern_cap', 0.12, 0.05, 0.08, (x, y - 0.35, z + 0.25), color='iron_d', parent=r, bevel=0.01, verts=12)
    cyl('lantern', 0.09, 0.09, 0.22, (x, y - 0.35, z + 0.03), color='lamp_w', parent=r, bevel=0.03, emit=4.0, verts=12)

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
        box('baluster', (0.06, 0.06, 0.72), (x, y, z + 0.18), (0, 0, ang), 'rail_w', r, bevel=0.009)   # square, with rounded edges

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
    rock('lamp_foot', 0.2, (x, y, z + 0.02), (1.0, 1.0, 0.5), (0, 0, 20), 'stone_b', r, flat=0.5)
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
    rock('signal_foot', 0.28, (x, y, z + 0.03), (1.0, 0.95, 0.5), (0, 0, 35), 'stone_b', r, flat=0.55)
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
    # the old pier of the ruin: big weathered blocks round a core, the top paved with its old floor slabs
    box('core', (LX - 0.5, LY - 0.5, TOP - BASE - 0.06), (0, 0, BASE), color='joint', parent=r, bevel=0.02)
    ruin_face(r, rnd, LX, -LY / 2, 'x'); ruin_face(r, rnd, LX, LY / 2, 'x')
    ruin_face(r, rnd, LY, -LX / 2, 'y'); ruin_face(r, rnd, LY, LX / 2, 'y')
    joints = []
    floor_slabs(r, rnd, joints)
    for (x, y) in joints: moss_tuft(r, rnd, x, y, TOP + 0.004, rnd.uniform(0.7, 1.1))
    ruin_tower(r, rnd)
    for (x, y, nx_, ny_, ln) in ((-3.2, -LY / 2 - 0.12, 0, -1, 1.2), (1.6, -LY / 2 - 0.12, 0, -1, 0.8), (3.9, LY / 2 + 0.12, 0, 1, 1.4), (LX / 2 + 0.12, -1.6, 1, 0, 1.0)):
        ivy(r, rnd, x, y, TOP - 0.05, nx_, ny_, ln)                          # a little ivy over the pier's edge
    # v2.2: a tall ruined wall from the tower along the platform, the waiting spot in front of it
    WT, WH = 0.7, 3.2
    WY = -LY / 2 + (LY - WT) * 2 / 5 + WT / 2                                  # the space in front of it and behind it is 2 : 3
    wx0 = TX + math.sqrt((TR - TW / 2) ** 2 - (WY - TY) ** 2)                   # it starts in the middle of the tower's wall
    ruin_wall(r, rnd, wx0, LX / 2 - 2.6, WY, WT, WH, ((-2.4, TOP + 1.25, TOP + 2.55), (1.4, TOP + 1.25, TOP + 2.55)))
    for lx in (-3.9, -0.5, 2.6): lantern(r, lx, WY - WT / 2, TOP + 1.95)
    seat_row(r, -0.5, WY - WT / 2 - 0.45, 4)
    trash_can(r, -0.5 - 4 * 0.62 / 2 - 0.45, WY - WT / 2 - 0.45)
    crossing_signal(r, 1.9, -LY / 2 + 0.7)
    # the right end: steps up to a landing behind the end of the wall, the info board there among bushes
    LH = 0.45; lx0, lx1, ly0, ly1 = LX / 2 - 2.55, LX / 2 - 0.05, 0.2, LY / 2 - 0.05
    for k in range(3):                                                          # steps up from the platform
        painted_box('step', (0.38, 1.0, LH / 3 * (k + 1)), (lx0 - 0.95 + k * 0.36 + 0.18, ly0 + 0.55, TOP - 0.02), color=rnd.choice(('stone_a', 'stone_b')), parent=r, bevel=0.03, along='top', band=0.1, rough=2.0)
    xs = lx0
    while xs < lx1 - 0.05:                                                      # the landing: a block of big slabs
        l = min(rnd.uniform(0.8, 1.2), lx1 - xs)
        painted_box('landing', (l - 0.03, ly1 - ly0 - 0.03, LH + 0.08), (xs + l / 2, (ly0 + ly1) / 2, TOP - 0.08), (0, 0, rnd.uniform(-0.8, 0.8)), color=rnd.choice(('tile_a', 'tile_b', 'tile_e')), parent=r, bevel=0.03, along='top', band=0.1, rough=2.0)
        xs += l
    info_board(r, (lx0 + lx1) / 2 + 0.2, ly1 - 0.55)                            # facing the steps... the board's own legs stand on the landing
    for (bx, by) in ((lx0 + 0.35, ly1 - 0.4), (lx1 - 0.35, ly1 - 0.35), (lx1 - 0.3, ly0 + 0.4)):
        bush(r, rnd, bx, by, TOP + LH - 0.05, 0.7)
    for (bx, by, bs) in ((TX - 1.2, TY - TR - 0.3, 1.2), (TX + 0.6, TY - TR - 0.5, 1.0), (TX - TR - 0.2, TY + 0.4, 1.1)):
        bush(r, rnd, bx, by, BASE + 0.4, bs)                                    # bushes at the foot of the tower
    # stairs down at the right end, in front of the landing, then a small side jetty with a mooring post
    for k in range(4): painted_box('step', (0.44, 1.6, 0.22), (LX / 2 + 0.23 + k * 0.42, -1.2, TOP - 0.22 - k * 0.2), (0, 0, rnd.uniform(-2, 2)), color=rnd.choice(('stone_a', 'stone_b')), parent=r, bevel=0.03, along='top', band=0.1, rough=2.0)
    JX0, JX1, JZ = LX / 2 + 1.68, LX / 2 + 5.4, 0.12
    for i in range(int((JX1 - JX0) / 0.3)):
        plank('jetty_plank', (1.6, 0.28, 0.06), (JX0 + 0.15 + i * 0.3, -1.2, JZ), (0, 0, 90 + rnd.uniform(-1.5, 1.5)), 'plank' if i % 3 else 'plank_d', r, bevel=0.012)
    for jx in (JX0 + 0.3, JX0 + 1.9, JX1 - 0.2):
        for sy in (-2.1, -0.3): cyl('jetty_pile', 0.08, 0.07, 1.6, (jx, sy, -1.4), color='timber_dark', parent=r, bevel=0.01, verts=10)
    for sy in (-2.0, -0.4): box('jetty_beam', (JX1 - JX0, 0.12, 0.14), ((JX0 + JX1) / 2, sy, JZ - 0.14), color='timber_dark', parent=r, bevel=0.02)
    cyl('bollard', 0.12, 0.1, 0.5, (JX1 - 0.3, -0.5, JZ + 0.06), color='timber_dark', parent=r, bevel=0.03, verts=12)
    ball('bollard_cap', 0.13, (JX1 - 0.3, -0.5, JZ + 0.58), (1, 1, 0.5), 'timber_dark', r)
    tube('rope', [(JX1 - 0.3, -0.5, JZ + 0.4), (JX1 - 0.2, 0.15, JZ + 0.05), (JX1 - 0.4, 0.85, JZ + 0.25)], 0.02, 0xD9C08E, r)
    bake_cuts()
    return r

def bake_cuts():
    """Apply the window cuts now and paint the new faces (the window reveals): a cut leaves them unpainted, black."""
    dg = bpy.context.evaluated_depsgraph_get()
    for o in [o for o in bpy.data.objects if o.type == 'MESH' and any(m.type == 'BOOLEAN' for m in o.modifiers)]:
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), depsgraph=dg)
        at = me.color_attributes.get('Col')
        if at:
            for d in at.data:
                c = d.color
                if c[0] + c[1] + c[2] < 0.06: d.color = (0.82, 0.8, 0.74, 1.0)
        o.modifiers.clear(); o.data = me
