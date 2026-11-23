"""The traveller as a little sheet ghost, after the user's reference: a soft round head under a thin, see-through sheet
that hangs down and frays at the bottom into many long, pointed, wispy strands of different lengths, trailing back as
it floats. Big dark oval eyes. Sandstone cream, faintly glowing at the edges. The headphones over the top. About 1.1 m
tall; it floats, the strands' tips a little above the ground. Origin on the ground under it; it faces -Y."""
import math, random, bmesh
from lib import *
VIEW = dict(angle=-28, lift=0.22, res=(1200, 900), samples=128, zoom=1.0)
BODY, CUP, PAD, BAND, EYE = 0xF4ECDD, 0x5C5F69, 0x3F424A, 0x6A6D77, 0x2B2728   # sandstone cream
H, LIFT, R, SPLIT = 1.1, 0.12, 0.30, 0.30                                       # height, hover, head radius, where the hem frays
STRANDS, FOLDS = 18, 9

def radius(z):
    """The sheet's outline: draped round over the head, then hanging below it, flaring out towards the hem."""
    t = z / H; t0 = 1 - R / H
    if t >= t0: return R * math.sqrt(max(0.0, 1 - ((t - t0) / (1 - t0)) ** 2))
    k = (t0 - t) / t0
    return R * (0.97 + 0.30 * k ** 1.4)

def fold(z, a):
    """Soft vertical folds in the cloth, none over the head, deepening towards the hem, a little uneven."""
    t0 = 1 - R / H; k = max(0.0, (t0 - z / H) / t0)
    return 1 + 0.07 * k ** 1.2 * (math.sin(FOLDS * a + 1.3 * k) * 0.7 + math.sin(2.3 * FOLDS * a + 0.6) * 0.3)

def at(z, a, extra=(0.0, 0.0, 0.0)):
    """A point on the sheet at height z and angle a; the cloth trails back a little lower down, as it floats."""
    rr = radius(z) * fold(z, a); k = max(0.0, 1 - z / (H * 0.6))
    return (rr * math.cos(a) + extra[0], rr * math.sin(a) + 0.12 * k * k + extra[1], z + LIFT + extra[2])

def sheet_mat():
    """Sandstone cream, partly see-through (clearer face-on), with a soft glow of the same colour at its edges."""
    m = bpy.data.materials.new('c_%06x' % BODY); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    c = tuple(((v / 255 + 0.055) / 1.055) ** 2.4 for v in (BODY >> 16 & 255, BODY >> 8 & 255, BODY & 255)) + (1,)
    b.inputs['Base Color'].default_value = c; b.inputs['Roughness'].default_value = 0.8
    fr = nt.nodes.new('ShaderNodeLayerWeight'); fr.inputs['Blend'].default_value = 0.35
    mp = nt.nodes.new('ShaderNodeMapRange'); mp.inputs['To Min'].default_value = 0.42; mp.inputs['To Max'].default_value = 0.92
    nt.links.new(fr.outputs['Facing'], mp.inputs['Value']); nt.links.new(mp.outputs['Result'], b.inputs['Alpha'])
    b.inputs['Emission Color'].default_value = c
    em = nt.nodes.new('ShaderNodeMath'); em.operation = 'MULTIPLY'; em.inputs[1].default_value = 0.6
    nt.links.new(fr.outputs['Facing'], em.inputs[0]); nt.links.new(em.outputs['Value'], b.inputs['Emission Strength'])
    return m

def body(r, rnd):
    """The sheet as one piece of cloth: over the head and down to the hem (open at the bottom), its hem fraying into
    short pointed wisps of different lengths that trail and curl a little; thickened slightly and smoothed."""
    bm = bmesh.new(); n = STRANDS * 4
    rings = []
    for i in range(48, -1, -1):
        z = SPLIT + (H - SPLIT) * (i / 48) ** 0.9
        rings.append([bm.verts.new(at(z, 2 * math.pi * k / n)) for k in range(n)])
    for i in range(len(rings) - 1):
        for k in range(n): bm.faces.new((rings[i][k], rings[i][(k + 1) % n], rings[i + 1][(k + 1) % n], rings[i + 1][k]))
    last = rings[-1]
    for s in range(STRANDS):                                                    # the frayed hem
        L = rnd.uniform(0.1, 0.3) * (1.3 if math.sin(2 * math.pi * (s * 4 + 2) / n) > 0.3 else 1.0)   # longer behind
        curl = rnd.uniform(-0.05, 0.05); m = 6
        prev = [last[(s * 4 + c) % n] for c in range(5)]
        for j in range(1, m + 1):
            f = j / m; z = SPLIT - L * f; ex = (curl * f * f, 0.05 * f * f, 0.03 * f ** 3)
            if j == m:
                tip = bm.verts.new(at(z, 2 * math.pi * (s * 4 + 2) / n, ex))
                for c in range(4): bm.faces.new((prev[c], prev[c + 1], tip))
                break
            row = [bm.verts.new(at(z, 2 * math.pi * (s * 4 + 2 + (c - 2) * (1 - f) ** 0.8) / n, ex)) for c in range(5)]
            for c in range(4): bm.faces.new((prev[c], prev[c + 1], row[c + 1], row[c]))
            prev = row
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new('body'); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new('body', me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(sheet_mat()); o.parent = r
    so = o.modifiers.new('thick', 'SOLIDIFY'); so.thickness = 0.01
    o.modifiers.new('smooth', 'SUBSURF').levels = 1
    return o

def build():
    set_style(sky=(0.30, 0.36, 0.42), sky_power=0.8, ground=0x55606A, sun=(1.0, 0.95, 0.9), sun_power=2.6, sun_height=42)
    r = root('ghost'); rnd = random.Random(5)
    body(r, rnd)
    ez = H - R * 0.95; er = radius(ez)                                         # big dark oval eyes
    for sx in (-1, 1):
        x = sx * 0.11; y = -math.sqrt(er * er - x * x) - 0.004                        # on the cloth, not under it
        ball('_eye', 0.072, (x, y, ez + LIFT), (0.82, 0.35, 1.25), EYE, r, rough=0.6)   # rendered, not exported: the site draws its own
    cz = H - R * 0.55; cr = radius(cz)                                         # the headphones
    pts = []
    for i in range(25):
        a = math.radians(-84 + 168 * i / 24); dx, dz = math.sin(a), math.cos(a); d = 0.0
        while d < 2 and abs(dx * d) < radius(min(H, cz + dz * d)) and cz + dz * d < H: d += 0.005
        pts.append((dx * (d + 0.035), 0.0, cz + dz * (d + 0.035) + LIFT))
    tube('band', pts, 0.024, BAND, r, rough=0.6)
    for sx in (-1, 1):
        cyl('cup', 0.12, 0.11, 0.1, (sx * (cr - 0.02), 0, cz + LIFT), (0, sx * 90, 0), CUP, r, bevel=0.04, verts=32, rough=0.55)
        cyl('pad', 0.095, 0.095, 0.035, (sx * (cr - 0.03), 0, cz + LIFT), (0, -sx * 90, 0), PAD, r, bevel=0.015, verts=32, rough=0.9)
    return r
