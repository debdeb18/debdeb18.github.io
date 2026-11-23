"""The traveller as a little ghost: the blob's soft round head (blender/assets/blob.py), its body narrowing below into
a soft pointed tail that curls back behind it, like a floating ghost. Pale, cool white with a faint glow, two dot eyes,
and the headphones over the top. About 1 m from the tail's tip to the top; it floats, the tip a little above the
ground. Origin on the ground under it; it faces -Y."""
import math, bmesh
from lib import *
VIEW = dict(angle=-30, lift=0.22, res=(1200, 900), samples=96, zoom=1.05)
BODY, CUP, PAD, BAND, EYE = 0xF4ECDD, 0x5C5F69, 0x3F424A, 0x6A6D77, 0x2A2626   # body: pale sandstone cream (the ruin's stone)
H, LIFT, T0, R = 1.15, 0.16, 0.74, 0.30                                          # height, hover, where the head's dome begins, its radius

def radius(z):
    """A soft teardrop: a round dome for the head, flowing without a neck into a body that tapers smoothly to the tail."""
    t = z / H
    if t >= T0: return R * math.sqrt(max(0.0, 1 - ((t - T0) / (1 - T0)) ** 2))
    s = math.sin(math.pi / 2 * t / T0)
    return R * s ** 1.55                                                    # a long teardrop, thin at the tail

def bend(z):
    """The tail sweeps back (+Y) and its tip curls up a little: (push back, lift)."""
    k = max(0.0, 1 - (z / H) / 0.6)
    return 0.30 * k ** 2.0, 0.12 * k ** 3.0

def body(r):
    """Rings of the radius above, each pushed back by the bend, joined into one smooth surface; subdivided."""
    bm = bmesh.new(); n, rings = 48, 44
    grid = []
    for i in range(rings + 1):
        z = H * (i / rings) ** 1.1
        rr = radius(z); y0, up = bend(z); kk = max(0.0, 1 - (z / H) / 0.6); x0 = 0.11 * math.sin(kk * math.pi * 1.3) * kk   # sways side to side
        grid.append([bm.verts.new((x0 + rr * math.cos(2 * math.pi * k / n), y0 + rr * math.sin(2 * math.pi * k / n), z + LIFT + up)) for k in range(n)])
    for i in range(rings):
        for k in range(n): bm.faces.new((grid[i][k], grid[i][(k + 1) % n], grid[i + 1][(k + 1) % n], grid[i + 1][k]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new('body'); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new('body', me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat(BODY, rough=0.9, emit=0.04)); o.parent = r
    o.modifiers.new('smooth', 'SUBSURF').levels = 2
    return o

def build():
    set_style(sky=(0.42, 0.55, 0.70), sky_power=0.9, ground=0x8FAABB, sun=(1.0, 0.95, 0.9), sun_power=3.0, sun_height=40)
    r = root('ghost')
    body(r)
    ez = (T0 - 0.05) * H; er = radius(ez)                                              # the eyes: two small dots
    for sx in (-1, 1):
        x = sx * 0.08; y = -math.sqrt(er * er - x * x) + 0.012
        ball('_eye', 0.032, (x, y, ez + LIFT), (1.0, 0.55, 1.15), EYE, r, rough=0.35)   # rendered, not exported: the site draws its own
    az = 0.56 * H; ar = radius(az)                                              # two little stubby arms, out to the sides
    for sx in (-1, 1):
        ball('arm', 0.062, (sx * (ar + 0.02), -0.03, az + LIFT), (1.35, 0.9, 0.85), BODY, r, rough=0.9, emit=0.04).rotation_euler = (0, sx * math.radians(-25), sx * math.radians(-15))
    cz = (T0 + 0.03) * H; cr = radius(cz)                                      # the headphones
    pts = []
    for i in range(25):
        a = math.radians(-84 + 168 * i / 24); dx, dz = math.sin(a), math.cos(a); d = 0.0
        while d < 2 and abs(dx * d) < radius(min(H, cz + dz * d)) and cz + dz * d < H: d += 0.005
        pts.append((dx * (d + 0.04), 0.0, cz + dz * (d + 0.04) + LIFT))
    tube('band', pts, 0.028, BAND, r, rough=0.6)
    for sx in (-1, 1):
        cyl('cup', 0.13, 0.12, 0.11, (sx * (cr - 0.02), 0, cz + LIFT), (0, sx * 90, 0), CUP, r, bevel=0.05, verts=32, rough=0.55)
        cyl('pad', 0.10, 0.10, 0.04, (sx * (cr - 0.03), 0, cz + LIFT), (0, -sx * 90, 0), PAD, r, bevel=0.018, verts=32, rough=0.9)
    return r
