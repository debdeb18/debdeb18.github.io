"""A small low-poly orange fish for the water by the back stairs, after the user's reference: a faceted body, a big
dorsal fin, a broad tail, little fins underneath and a round eye. Flat shaded. Origin under its belly fins; it faces -X."""
import bmesh
from lib import *
VIEW = dict(angle=30, lift=0.35, res=(700, 500), samples=24)
ORANGE, FIN = 0xEE6A2C, 0xE45A22

def facet(name, verts, faces, color, parent):
    bm = bmesh.new(); vs = [bm.verts.new(v) for v in verts]
    for f in faces: bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat(color)); o.parent = parent
    return o

def fin(name, pts, color, parent):                          # a flat fin with a little thickness
    t = 0.004; vs = [(x, y - t, z) for (x, y, z) in pts] + [(x, y + t, z) for (x, y, z) in pts]; n = len(pts)
    faces = [list(range(n)), list(range(2 * n - 1, n - 1, -1))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    return facet(name, vs, faces, color, parent)

def build():
    r = root('fish')
    body = root('fish_body'); body.location = (0, 0, 0.125); body.parent = r     # lifted, so the belly fins sit at the origin
    r_, r = r, body
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=1.0)
    for v in bm.verts:                                       # a plump body: blunt head, tapering to the tail
        x = v.co.x; k = 1.0 - max(0.0, x) * 0.55
        v.co.x *= 0.17; v.co.y *= 0.065 * k; v.co.z *= 0.085 * k + (0.008 if v.co.z > 0 else 0)
    me = bpy.data.meshes.new('body'); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = False             # flat facets
    b = bpy.data.objects.new('body', me); bpy.context.scene.collection.objects.link(b); b.data.materials.append(mat(ORANGE)); b.parent = r
    fin('tail', [(0.15, 0, 0.0), (0.27, 0, 0.09), (0.25, 0, 0.0), (0.27, 0, -0.08)], FIN, r)
    fin('dorsal', [(-0.04, 0, 0.08), (0.02, 0, 0.16), (0.08, 0, 0.13), (0.09, 0, 0.06)], FIN, r)
    for (x, sy) in ((-0.06, -1), (-0.06, 1), (0.04, -1), (0.04, 1)):
        fin('belly_fin', [(x, sy * 0.03, -0.06), (x + 0.015, sy * 0.045, -0.12), (x + 0.045, sy * 0.045, -0.12), (x + 0.03, sy * 0.03, -0.06)], FIN, r)
    for sy in (-1, 1):
        ball('eye', 0.016, (-0.12, sy * 0.05, 0.025), (1, 0.4, 1), 0xFFFFFF, r)
        ball('pupil', 0.009, (-0.123, sy * 0.056, 0.025), (1, 0.4, 1), 0x1E2228, r)
    return r_
