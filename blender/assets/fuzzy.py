"""The traveller as a fuzzy puff: a round, soft ball of sandstone-cream fur (the colour of the ruin's stone), two dark
dot eyes peeking out of the fur, two little rounded feet, and the headphones over the top. The fur is real geometry:
a couple of thousand fine tufts, darker at the root and lighter at the tip, so it reads soft at any distance. About
0.8 m tall. Origin on the ground under it; it faces -Y."""
import math, random, bmesh
from mathutils import Vector, Matrix
from lib import *
VIEW = dict(angle=-25, lift=0.25, res=(1200, 900), samples=128, zoom=1.15)
FUR, FEET, CUP, PAD, BAND, EYE = 0xF4ECDD, 0xC9B79A, 0x5C5F69, 0x3F424A, 0x6A6D77, 0x2B2728
R, CZ, SQ = 0.30, 0.42, 0.92                                                    # body radius, centre height, squash

def surface(d):
    """The point on the (slightly squashed) body in direction d, and its outward normal."""
    p = Vector((d.x * R, d.y * R, d.z * R * SQ))
    nrm = Vector((d.x, d.y, d.z / SQ)).normalized()
    return Vector((p.x, p.y, p.z + CZ)), nrm

def fur(r, rnd, n=7000):
    """Fine tufts all over: thin tapering cones along the normal, each bent a little and of its own length; shorter
    round the face so the eyes show, a little longer on top; colour from root to tip."""
    bm = bmesh.new(); col = bm.verts.layers.color.new('Col')
    base = Vector(((0xC9 / 255) ** 2.2, (0xB7 / 255) ** 2.2, (0x9A / 255) ** 2.2)); tip = Vector(((0xF4 / 255) ** 2.2, (0xEC / 255) ** 2.2, (0xDD / 255) ** 2.2))
    for i in range(n):
        z = 1 - 2 * (i + 0.5) / n; a = i * 2.39996323; s = math.sqrt(1 - z * z)
        d = Vector((s * math.cos(a), s * math.sin(a), z)); d = (d + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * 0.04).normalized()
        if d.z < -0.75: continue                                                    # none underneath
        p, nrm = surface(d)
        face = max(0.0, -d.y) * max(0.0, 1 - abs(d.z - 0.15) * 2.2)                 # round the eyes: short
        L = rnd.uniform(0.045, 0.075) * (1 - 0.5 * face) * (1.15 if d.z > 0.5 else 1.0)
        down = Vector((0, 0, -1)) - nrm * (-nrm.z)                                  # combed down along the body
        down = down.normalized() if down.length > 1e-3 else Vector((0, -1, 0))
        bendv = (down * 1.4 + Vector((rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), 0))).normalized()
        w = rnd.uniform(0.016, 0.024)
        side = nrm.cross(Vector((0, 0, 1)) if abs(nrm.z) < 0.9 else Vector((1, 0, 0))).normalized(); up = nrm.cross(side)
        root = [bm.verts.new(p - nrm * 0.01 + (side * math.cos(k * 2.094) + up * math.sin(k * 2.094)) * w) for k in range(3)]
        mid = [bm.verts.new(p + nrm * L * 0.45 + bendv * L * 0.35 + (side * math.cos(k * 2.094) + up * math.sin(k * 2.094)) * w * 0.7) for k in range(3)]
        end = bm.verts.new(p + nrm * L * 0.55 + bendv * L * 0.95)                  # a soft, lying-down tip
        for k in range(3):
            bm.faces.new((root[k], root[(k + 1) % 3], mid[(k + 1) % 3], mid[k])); bm.faces.new((mid[k], mid[(k + 1) % 3], end))
        shade = rnd.uniform(0.92, 1.05)
        for v, t in [(v, 0.0) for v in root] + [(v, 0.55) for v in mid] + [(end, 1.0)]:
            c = (base.lerp(tip, t)) * shade; v[col] = (min(1, c.x), min(1, c.y), min(1, c.z), 1.0)
    me = bpy.data.meshes.new('fur'); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new('fur', me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat_vc(0xFFFFFF, rough=0.9)); o.parent = r
    return o

def build():
    set_style(sky=(0.62, 0.74, 0.84), sky_power=0.95, ground=0xBFD3DC, sun=(1.0, 0.95, 0.88), sun_power=3.0, sun_height=45)
    r = root('fuzzy'); rnd = random.Random(3)
    ball('core', R * 1.0, (0, 0, CZ), (1, 1, SQ), FUR, r, rough=0.9)            # the soft body under the fur
    fur(r, rnd)
    for sx in (-1, 1):                                                          # two little rounded feet
        ball('foot', 0.085, (sx * 0.12, -0.06, 0.07), (1.0, 1.35, 0.7), FEET, r, rough=0.85)
    ez = CZ + 0.05                                                              # the eyes, peeking out of the fur
    for sx in (-1, 1):
        d = Vector((sx * 0.3, -1.0, 0.16)).normalized(); p, nrm = surface(d)
        ball('_eye', 0.045, tuple(p + nrm * 0.035), (0.85, 0.5, 1.2), EYE, r, rough=0.4)   # rendered, not exported: the site draws its own
    cz = CZ + R * SQ * 0.45; hr = R + 0.07                                      # the headphones, over the fur
    pts = []
    for i in range(25):
        a = math.radians(-80 + 160 * i / 24)
        pts.append((math.sin(a) * hr, 0.0, cz + (CZ + R * SQ + 0.08 - cz) * math.cos(a)))
    tube('band', pts, 0.024, BAND, r, rough=0.6)
    for sx in (-1, 1):
        cyl('cup', 0.11, 0.1, 0.1, (sx * (R + 0.02), 0, cz), (0, sx * 90, 0), CUP, r, bevel=0.04, verts=32, rough=0.55)
        cyl('pad', 0.085, 0.085, 0.035, (sx * (R + 0.01), 0, cz), (0, -sx * 90, 0), PAD, r, bevel=0.015, verts=32, rough=0.9)
    return r
