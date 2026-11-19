"""A small wooden rowing boat with a proper hull: a pointed bow that rises, a flat transom stern, overlapping planks
(clinker) along the sides, a rail along the top, ribs and two seats inside, oars resting in their oarlocks.
build(style): 'A' varnished wood, 'B' painted teal with a cream stripe and a red bottom, 'C' white with a red stripe
and a little canvas awning. Origin at its keel line (sit it about 0.12 below the water); the bow points -X."""
import math, bmesh
from mathutils import Vector
from lib import *
VIEW = dict(angle=35, lift=0.45, res=(1000, 700), samples=32)
L, W, D, H = 3.0, 0.62, 0.42, 0.28                     # length, half beam, depth of the keel below the rail, rail height

def width(t): return W * (math.sin(t / 0.45 * math.pi / 2) if t < 0.45 else 1 - 0.32 * ((t - 0.45) / 0.55) ** 2)
def depth(t): return D * (0.45 + 0.55 * math.sin(math.pi * (0.08 + 0.84 * t)))
def sheer(t): return H + 0.16 * (1 - t) ** 3            # the rail rises towards the bow

def point(t, phi, out=0.0):
    """A point on the hull: t along (0 bow, 1 stern), phi round the section (-90 one rail, 0 keel, 90 other rail)."""
    w, d, s = width(t) + out, depth(t), sheer(t)
    return Vector((-L / 2 + t * L, w * math.sin(math.radians(phi)), s - d * math.cos(math.radians(phi)) ** 0.8 * (1 if abs(phi) < 90 else 0) - (0 if abs(phi) < 90 else 0)))

def strake(name, phi0, phi1, color, parent, n=26, out=0.0):
    """One plank band of the hull between two section angles, on both sides at once."""
    bm = bmesh.new(); rows = []
    for i in range(n + 1):
        t = i / n
        rows.append([bm.verts.new(point(t, ph, out)) for ph in (phi0, phi1)])
    for i in range(n):
        a, b = rows[i], rows[i + 1]
        if (a[0].co - a[1].co).length + (b[0].co - b[1].co).length > 1e-5: bm.faces.new((a[0], b[0], b[1], a[1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat(color)); o.parent = parent
    s = o.modifiers.new('thick', 'SOLIDIFY'); s.thickness = 0.03; s.offset = -1
    return o

def build(style='A'):
    r = root('boat'); hull = r
    if style == 'A': bands = [0xA9713F, 0x9A6338, 0xA9713F, 0x8E5A32, 0x7C4D2C, 0x6B4227]; inside, rail = 0x8E5A32, 0x5E3A22
    elif style == 'B': bands = [0x4F8FA0, 0x4F8FA0, 0xF1E6CC, 0x4F8FA0, 0xB8403A, 0xB8403A]; inside, rail = 0xC9A374, 0x2F5C6A
    else: bands = [0xF1EEE6, 0xF1EEE6, 0xB8403A, 0xF1EEE6, 0xE4E0D6, 0x6E7884]; inside, rail = 0xC9A374, 0x8A5A3C
    edges = [90, 72, 56, 41, 27, 13, 0]
    for k in range(6):                                                         # clinker: each band a little proud of the one below
        for sg in (1, -1):
            strake('strake', sg * edges[k], sg * edges[k + 1], bands[k], r, out=0.012 * (5 - k) / 5)
    st = [point(1.0, ph) for ph in range(-90, 91, 15)]                          # the transom: a flat stern board
    bm = bmesh.new(); bm.faces.new([bm.verts.new(p + Vector((0.01, 0, 0))) for p in st][::-1]); me = bpy.data.meshes.new('transom'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('transom', me); bpy.context.scene.collection.objects.link(o); o.data.materials.append(mat(bands[1])); o.parent = r
    o.modifiers.new('thick', 'SOLIDIFY').thickness = 0.04
    for sg in (1, -1):                                                          # the rail along the top
        tube('rail', [tuple(point(i / 20, sg * 90, 0.02)) for i in range(1, 21)], 0.03, rail, r)
    for k in range(9):                                                          # ribs inside
        t = 0.12 + k * 0.095
        tube('rib', [tuple(point(t, ph, -0.035)) for ph in range(-85, 86, 17)], 0.014, inside, r)
    box('floorboards', (L * 0.55, 0.36, 0.02), (0.05, 0, sheer(0.5) - depth(0.5) + 0.06), color=inside, parent=r, bevel=0.005)
    for t in (0.38, 0.72):                                                     # seats across
        wv = width(t) * 2 - 0.06
        plank('thwart', (0.24, wv, 0.04), (-L / 2 + t * L, 0, sheer(t) - 0.14), (0, 0, 0), inside, r, bevel=0.01, nails=False)
    plank('stern_seat', (0.3, width(0.93) * 2 - 0.08, 0.04), (-L / 2 + 0.93 * L, 0, sheer(0.93) - 0.12), (0, 0, 0), inside, r, bevel=0.01, nails=False)
    t0 = 0.55                                                                   # oarlocks; the oars shipped, resting
    for sg in (1, -1):                                                          # along each side, blades towards the bow
        p = point(t0, sg * 90, 0.03); cyl('oarlock', 0.012, 0.012, 0.08, tuple(p), color=0x3A3D44, parent=r, bevel=0, verts=8)
        a = Vector((-L / 2 + 0.95 * L, sg * (width(0.9) - 0.12), sheer(0.9) - 0.1)); b = Vector((-L / 2 + 0.2 * L, sg * (width(0.2) - 0.1), sheer(0.2) - 0.06))
        tube('oar', [tuple(a), tuple(b)], 0.02, 0xC9A374, r)
        d = (b - a).normalized()
        box('oar_blade', (0.34, 0.12, 0.015), tuple(b + d * 0.17 - Vector((0, 0, 0.0075))), (0, 0, math.degrees(math.atan2(d.y, d.x))), 0xC9A374, r, bevel=0.01)
    cyl('bow_post', 0.025, 0.025, 0.22, tuple(point(0.0, 0) + Vector((0.02, 0, depth(0.0) - 0.02))), color=rail, parent=r, bevel=0.005, verts=8)
    if style == 'C':                                                            # a canvas awning over the stern on bent sticks
        for t in (0.68, 0.86):
            x = -L / 2 + t * L
            tube('hoop', [(x, -width(t) + 0.02, sheer(t)), (x, -width(t) * 0.6, sheer(t) + 0.45), (x, 0, sheer(t) + 0.55), (x, width(t) * 0.6, sheer(t) + 0.45), (x, width(t) - 0.02, sheer(t))], 0.015, 0x8A5A3C, r)
        bm = bmesh.new(); rows = []
        for t in (0.66, 0.88):
            x = -L / 2 + t * L
            rows.append([bm.verts.new((x, width(t) * math.sin(a), sheer(t) + 0.55 * math.cos(a) ** 0.6)) for a in [math.radians(v) for v in range(-80, 81, 20)]])
        for i in range(len(rows[0]) - 1): bm.faces.new((rows[0][i], rows[0][i + 1], rows[1][i + 1], rows[1][i]))
        me = bpy.data.meshes.new('awning'); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new('awning', me); bpy.context.scene.collection.objects.link(o); o.data.materials.append(mat(0xE8DDC2)); o.parent = r
        o.modifiers.new('thick', 'SOLIDIFY').thickness = 0.01
    return r
