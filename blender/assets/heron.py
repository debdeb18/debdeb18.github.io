"""A grey heron, low-poly (flat facets), after the user's reference: a slim upright body that tapers to the tail, a long
neck flowing out of it in one curve, a small head with a dark crest and eye stripe, a long orange beak, thin grey legs.
Unlike the reference it has wings: folded flat along its sides, each its own part hinged at the shoulder
('heron_wing_l', '_r'), so the website can open them when it flies off. Origin at its feet; it faces -X."""
import math, bmesh
from mathutils import Vector
from lib import *
VIEW = dict(angle=35, lift=0.3, res=(900, 900), samples=32)
BODY, PALE, WING, TIP, BLACK, BEAK, LEG = 0xE9ECEF, 0xF6F6F2, 0xBFC6CF, 0x5E6672, 0x2B2D33, 0xEE8A32, 0x9AA0A8

def loft(name, pts, radii, color, parent, sides=7, squash=(1.0, 1.0)):
    """A faceted tube through pts (x, y, z) with a radius at each point, closed at both ends: one smooth flowing shape
    made of flat facets."""
    bm = bmesh.new(); rings = []
    for i, p in enumerate(pts):
        p = Vector(p); a = Vector(pts[min(i + 1, len(pts) - 1)]) - Vector(pts[max(i - 1, 0)]); a.normalize()
        u = a.cross(Vector((0, 1, 0))); u = u.normalized() if u.length > 1e-6 else Vector((1, 0, 0)); v = a.cross(u)
        rings.append([bm.verts.new(p + (u * math.cos(t) * squash[0] + v * math.sin(t) * squash[1]) * max(radii[i], 0.002))
                      for t in [2 * math.pi * k / sides for k in range(sides)]])
    for i in range(len(rings) - 1):
        for k in range(sides): bm.faces.new((rings[i][k], rings[i][(k + 1) % sides], rings[i + 1][(k + 1) % sides], rings[i + 1][k]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bmesh.ops.triangulate(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = False
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.data.materials.append(mat(color)); o.parent = parent
    return o

def blade(name, pts, color, parent, t=0.005, up=False):
    """A flat feather or plume with a little thickness: sideways (for upright pieces) or upward (up=True, lying flat)."""
    bm = bmesh.new(); n = len(pts)
    a = [bm.verts.new(p) for p in pts]; b = [bm.verts.new((x, y, z + t) if up else (x, y + t, z)) for (x, y, z) in pts]
    bm.faces.new(a); bm.faces.new(b[::-1])
    for i in range(n): bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='EAR_CLIP')   # (concave outlines too)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = False
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.data.materials.append(mat(color)); o.parent = parent
    return o

def build():
    r = root('heron')
    # the body: chest high at the front, tapering down and back to the tail
    loft('body', [(-0.15, 0, 0.8), (-0.11, 0, 0.78), (-0.03, 0, 0.72), (0.07, 0, 0.65), (0.17, 0, 0.57), (0.26, 0, 0.49), (0.31, 0, 0.45)],
         [0.04, 0.085, 0.11, 0.11, 0.085, 0.045, 0.01], BODY, r, sides=8, squash=(1.0, 0.85))
    # the neck flows out of the chest in one S-curve to the head
    neck = [(-0.12, 0, 0.78), (-0.16, 0, 0.88), (-0.16, 0, 0.98), (-0.12, 0, 1.07), (-0.11, 0, 1.15), (-0.14, 0, 1.21), (-0.18, 0, 1.235)]
    loft('neck', neck, [0.07, 0.05, 0.04, 0.035, 0.032, 0.033, 0.035], PALE, r, sides=7)
    loft('head', [(-0.13, 0, 1.235), (-0.17, 0, 1.24), (-0.21, 0, 1.235), (-0.235, 0, 1.228)], [0.02, 0.042, 0.036, 0.018], PALE, r, sides=7)
    loft('beak', [(-0.23, 0, 1.228), (-0.3, 0, 1.222), (-0.4, 0, 1.212)], [0.019, 0.012, 0.002], BEAK, r, sides=5, squash=(0.7, 1.0))
    for sy in (-1, 1):
        blade('eye_stripe', [(-0.215, sy * 0.034, 1.25), (-0.13, sy * 0.03, 1.262), (-0.13, sy * 0.03, 1.248), (-0.215, sy * 0.034, 1.236)], BLACK, r, t=0.002 * sy)
        loft('eye', [(-0.205, sy * 0.034, 1.243), (-0.2, sy * 0.037, 1.243)], [0.007, 0.007], 0xF2C94A, r, sides=5)
    blade('crest', [(-0.15, -0.003, 1.27), (-0.04, -0.003, 1.29), (-0.03, -0.003, 1.283), (-0.14, -0.003, 1.255)], BLACK, r)
    blade('crest', [(-0.15, 0.0, 1.262), (-0.06, 0.0, 1.258), (-0.055, 0.0, 1.25), (-0.15, 0.0, 1.25)], BLACK, r)
    for k in range(3): loft('neck_streak', [(-0.205, 0, 0.93 - k * 0.04), (-0.205, 0, 0.9 - k * 0.04)], [0.006, 0.004], BLACK, r, sides=4)
    # legs: thin, from under the body to long toes
    for sy in (-1, 1):
        loft('thigh', [(0.04, sy * 0.04, 0.63), (0.04, sy * 0.04, 0.55)], [0.03, 0.016], BODY, r, sides=6)
        loft('leg', [(0.04, sy * 0.04, 0.56), (0.03, sy * 0.045, 0.3), (0.02, sy * 0.05, 0.02)], [0.011, 0.01, 0.009], LEG, r, sides=5)
        for a in (-30, 0, 30):
            d = Vector((-math.cos(math.radians(a)), math.sin(math.radians(a)), 0))
            loft('toe', [(0.02, sy * 0.05, 0.012), tuple(Vector((0.02, sy * 0.05, 0.008)) + d * 0.11)], [0.006, 0.003], LEG, r, sides=4)
        loft('back_toe', [(0.02, sy * 0.05, 0.012), (0.075, sy * 0.05, 0.008)], [0.005, 0.003], LEG, r, sides=4)
    # the wings, folded along the sides, hinged at the shoulder so they can open
    for sy, nm in ((-1, 'heron_wing_l'), (1, 'heron_wing_r')):
        w = root(nm); w.location = (-0.08, sy * 0.085, 0.77); w.parent = r      # the shoulder
        blade('wing', [(0.0, 0, 0.02), (0.12, 0, -0.03), (0.3, 0, -0.2), (0.36, 0, -0.29), (0.3, 0, -0.27), (0.12, 0, -0.16), (0.0, 0, -0.08)], WING, w, t=0.012 * sy)
        for k in range(4):                                                     # dark flight feathers at the tip, layered
            x0 = 0.18 + k * 0.035
            blade('primary', [(x0, sy * 0.004, -0.12 - k * 0.025), (x0 + 0.17, sy * 0.004, -0.26 - k * 0.012), (x0 + 0.16, sy * 0.004, -0.28 - k * 0.012), (x0 - 0.01, sy * 0.004, -0.15 - k * 0.025)], TIP, w, t=0.004 * sy)
        for k in range(3):
            blade('covert', [(0.02 + k * 0.06, sy * 0.008, -0.02 - k * 0.03), (0.12 + k * 0.06, sy * 0.008, -0.08 - k * 0.04), (0.1 + k * 0.06, sy * 0.008, -0.1 - k * 0.04), (0.0 + k * 0.06, sy * 0.008, -0.05 - k * 0.03)], 0xA9B1BB, w, t=0.004 * sy)
    return r
