"""The traveller as a little ghost: the blob's soft rounded dome (blender/assets/blob.py) with, instead of a flat base,
a soft hem that flares out a little and ends in a few gentle waves, hollowed underneath, so it floats above the ground.
Pale, cool white with a faint glow, two dot eyes, and the headphones over the top. About 1 m tall. Origin on the
ground under it (it hovers a little above); it faces -Y."""
import math, bmesh
from lib import *
VIEW = dict(angle=-18, lift=0.28, res=(1200, 900), samples=96, zoom=1.1)
BODY, CUP, PAD, BAND, EYE = 0xF2F7FA, 0x5C5F69, 0x3F424A, 0x6A6D77, 0x1E1E24
H, LIFT, T0 = 1.0, 0.12, 0.58                                                   # height, hover, where the dome begins
WAVES, WAVE = 5, 0.045                                                          # the hem's waves

def radius(z):
    """The radius of the body above the hem (as the blob, slim, with a low round dome)."""
    t = z / H
    side = 0.40 - 0.04 * min(t, T0) / T0
    return side * math.sqrt(max(0.0, 1 - max(0.0, (t - T0) / (1 - T0)) ** 2))

def outline():
    """The profile (r, z) from the middle of the hollow underside, out to the hem's rim, up the side and over the dome."""
    pts = [(0.0, 0.16), (0.12, 0.15), (0.24, 0.12), (0.33, 0.07), (0.40, 0.025), (0.44, 0.0)]    # the hollow underneath
    pts += [(0.445, 0.02), (0.43, 0.06), (0.41, 0.11)]                                          # the hem flaring out
    for i in range(1, 33):
        z = 0.14 + (H - 0.14) * (i / 32) ** 0.9
        pts.append((max(radius(z), 0.0), z))
    pts[-1] = (0.0, H)
    return pts

def body(r):
    """A surface of revolution of the outline; the hem's rim rises and falls in gentle waves; subdivided smooth."""
    bm = bmesh.new(); n = 60; prof = outline(); rings = []
    for (rr, z) in prof:
        ring = []
        for k in range(n):
            a = 2 * math.pi * k / n
            w = max(0.0, 1 - z / 0.2) * (1 if rr > 0.3 else 0.4)                  # waves strongest at the rim
            zz = z + WAVE * w * math.cos(WAVES * a) + 0.012 * w * math.cos(2 * WAVES * a + 1)
            ring.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), zz + LIFT)))
        rings.append(ring)
    for i in range(len(rings) - 1):
        for k in range(n): bm.faces.new((rings[i][k], rings[i + 1][k], rings[i + 1][(k + 1) % n], rings[i][(k + 1) % n]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new('body'); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new('body', me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat(BODY, rough=0.9, emit=0.12)); o.parent = r
    o.modifiers.new('smooth', 'SUBSURF').levels = 2
    return o

def build():
    set_style(sky=(0.74, 0.84, 0.92), sky_power=1.0, ground=0xD2E3EA, sun=(1.0, 0.95, 0.9), sun_power=2.6, sun_height=48)
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
