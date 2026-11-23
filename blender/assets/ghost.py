"""The traveller as a little ghost: the blob's soft round head (blender/assets/blob.py), its body narrowing below into
a soft pointed tail that curls back behind it, like a floating ghost. Pale, cool white with a faint glow, two dot eyes,
and the headphones over the top. About 1 m from the tail's tip to the top; it floats, the tip a little above the
ground. Origin on the ground under it; it faces -Y."""
import math, bmesh
from lib import *
VIEW = dict(angle=-55, lift=0.22, res=(1200, 900), samples=96, zoom=1.05)
BODY, CUP, PAD, BAND, EYE = 0xF2F7FA, 0x5C5F69, 0x3F424A, 0x6A6D77, 0x1E1E24
H, LIFT, T0 = 1.0, 0.14, 0.58                                                   # height, hover, where the head's dome begins

def radius(z):
    """The radius at height z (0 the tail's tip, H the top): a round dome on top, widest at the head, then narrowing
    smoothly to the pointed tip."""
    t = z / H
    if t >= T0: return 0.40 * math.sqrt(max(0.0, 1 - ((t - T0) / (1 - T0)) ** 2))
    return 0.40 * math.sin(math.pi / 2 * (t / T0)) ** 1.6                   # a long, thin, pointed tail

def bend(z):
    """How far the body is pushed back (+Y) at height z: the tail curls back and a little up at its tip."""
    k = max(0.0, 1 - (z / H) / 0.55)
    return 0.38 * k ** 2.2

def body(r):
    """Rings of the radius above, each pushed back by the bend, joined into one smooth surface; subdivided."""
    bm = bmesh.new(); n, rings = 48, 44
    grid = []
    for i in range(rings + 1):
        z = H * (i / rings) ** 1.1
        rr = radius(z); y0 = bend(z)
        grid.append([bm.verts.new((rr * math.cos(2 * math.pi * k / n), y0 + rr * math.sin(2 * math.pi * k / n), z + LIFT)) for k in range(n)])
    for i in range(rings):
        for k in range(n): bm.faces.new((grid[i][k], grid[i][(k + 1) % n], grid[i + 1][(k + 1) % n], grid[i + 1][k]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new('body'); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new('body', me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat(BODY, rough=0.9, emit=0.03)); o.parent = r
    o.modifiers.new('smooth', 'SUBSURF').levels = 2
    return o

def build():
    set_style(sky=(0.42, 0.55, 0.70), sky_power=0.9, ground=0x8FAABB, sun=(1.0, 0.95, 0.9), sun_power=3.0, sun_height=40)
    r = root('ghost')
    body(r)
    ez = 0.62 * H; er = radius(ez)                                              # the eyes: two small dots
    for sx in (-1, 1):
        x = sx * 0.07; y = -math.sqrt(er * er - x * x) + 0.012
        ball('_eye', 0.032, (x, y, ez + LIFT), (1.0, 0.55, 1.15), EYE, r, rough=0.35)   # rendered, not exported: the site draws its own
    cz = 0.66 * H; cr = radius(cz)                                              # the headphones
    pts = []
    for i in range(25):
        a = math.radians(-84 + 168 * i / 24); dx, dz = math.sin(a), math.cos(a); d = 0.0
        while d < 2 and abs(dx * d) < radius(min(H, cz + dz * d)) and cz + dz * d < H: d += 0.005
        pts.append((dx * (d + 0.04), 0.0, cz + dz * (d + 0.04) + LIFT))
    tube('band', pts, 0.028, BAND, r, rough=0.6)
    for sx in (-1, 1):
        cyl('cup', 0.15, 0.14, 0.12, (sx * (cr - 0.02), 0, cz + LIFT), (0, sx * 90, 0), CUP, r, bevel=0.05, verts=32, rough=0.55)
        cyl('pad', 0.12, 0.12, 0.04, (sx * (cr - 0.03), 0, cz + LIFT), (0, -sx * 90, 0), PAD, r, bevel=0.018, verts=32, rough=0.9)
    return r
