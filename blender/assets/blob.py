"""The traveller, first and simplest version, after the soft-blob reference (docs/refs/character/soft-blob.png): a soft,
rounded gumdrop body, smooth and matte, two small dot eyes, and a pair of headphones over the top. No arms or legs:
it moves by bobbing and hopping. About 1 m tall. Origin at its base; it faces -Y."""
import math, bmesh
from lib import *
VIEW = dict(angle=-18, lift=0.28, res=(1200, 900), samples=96, zoom=1.15)
BODY, CUP, PAD, BAND, EYE = 0xECEAF0, 0x5C5F69, 0x3F424A, 0x6A6D77, 0x1E1E24
H = 1.0                                                                         # height
T0 = 0.58                                                                       # where the dome begins

def profile(z):
    """The body's radius at height z (0..H): a flat, softly rounded base, widest at the bottom, gently narrowing to a
    round, low dome (about as tall as it is wide, so the top is neither tall nor pointy), like a soft gumdrop."""
    t = z / H
    side = 0.43 - 0.06 * min(t, T0) / T0                                         # widest at the base
    dome = math.sqrt(max(0.0, 1 - max(0.0, (t - T0) / (1 - T0)) ** 2))
    foot = math.sqrt(max(0.0, 1 - ((0.06 - t) / 0.06) ** 2)) if t < 0.06 else 1.0  # the rounded foot
    return side * dome * (0.9 + 0.1 * foot) if t >= 0.06 else side * (0.86 + 0.14 * foot)

def body(r):
    """The body as one smooth surface of revolution, subdivided."""
    bm = bmesh.new(); n, rings = 48, 40
    zs = [H * (i / rings) ** 0.9 for i in range(rings + 1)]
    grid = []
    for z in zs:
        rr = profile(z); grid.append([bm.verts.new((rr * math.cos(2 * math.pi * k / n), rr * math.sin(2 * math.pi * k / n), z)) for k in range(n)])
    for i in range(rings):
        for k in range(n): bm.faces.new((grid[i][k], grid[i][(k + 1) % n], grid[i + 1][(k + 1) % n], grid[i + 1][k]))
    bm.faces.new(grid[0][::-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new('body'); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new('body', me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat(BODY, rough=0.85)); o.parent = r
    o.modifiers.new('smooth', 'SUBSURF').levels = 2
    return o

def build():
    set_style(sky=(0.80, 0.74, 0.90), sky_power=1.0, ground=0xDCD5E8, sun=(1.0, 0.94, 0.88), sun_power=2.6, sun_height=48)
    r = root('blob')
    body(r)
    ez = 0.62 * H                                                              # the eyes: two small dots, low on the face
    er = profile(ez)
    for sx in (-1, 1):
        x = sx * 0.072; y = -math.sqrt(er * er - x * x) + 0.012
        ball('_eye', 0.032, (x, y, ez), (1.0, 0.55, 1.15), EYE, r, rough=0.35)   # rendered, not exported: the website draws its own, to blink
    # the headphones: a band over the top, a padded cup on each side
    cz = 0.66 * H; cr = profile(cz)
    pts = []                                                                    # the band: a smooth arc that hugs the head
    for i in range(25):
        a = math.radians(-84 + 168 * i / 24); dx, dz = math.sin(a), math.cos(a); d = 0.0
        while d < 2 and abs(dx * d) < profile(min(H, cz + dz * d)) and cz + dz * d < H: d += 0.005   # out to the surface
        pts.append((dx * (d + 0.04), 0.0, cz + dz * (d + 0.04)))
    tube('band', pts, 0.028, BAND, r, rough=0.6)
    for sx in (-1, 1):
        cyl('cup', 0.15, 0.14, 0.12, (sx * (cr - 0.02), 0, cz), (0, sx * 90, 0), CUP, r, bevel=0.05, verts=32, rough=0.55)
        cyl('pad', 0.12, 0.12, 0.04, (sx * (cr - 0.03), 0, cz), (0, -sx * 90, 0), PAD, r, bevel=0.018, verts=32, rough=0.9)
    return r
