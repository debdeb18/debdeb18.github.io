"""A low-poly cat curled up asleep, after the user's reference: sculpted as one continuous shape (body, head on its
paws, the tail wrapped round the front, all flowing into each other), then cut down into flat triangles like folded
paper. Big pointed ears, eyes shut. Origin under its middle; it faces -Y. The porch puts it in the tower nook."""
import math, bmesh
from mathutils import Vector
from lib import *
VIEW = dict(angle=-25, lift=0.4, res=(900, 640), samples=32)
FUR, DARK = 0xE39C5A, 0x6A3E22

def build(parent=None, name='cat_sleep'):
    c = root(name)
    if parent: c.parent = parent
    mb = bpy.data.metaballs.new('cat_shape'); mb.resolution = 0.012; mb.threshold = 0.6
    def blob(p, rr, stiff=2.0):
        e = mb.elements.new(); e.co = p; e.radius = rr; e.stiffness = stiff
    for p, rr in (((0.02, 0.04, 0.11), 0.24), ((0.14, 0.06, 0.1), 0.2), ((-0.09, 0.0, 0.09), 0.18), ((0.08, -0.05, 0.08), 0.17)):
        blob(p, rr)                                                            # the round curled body
    blob((-0.23, -0.17, 0.13), 0.17)                                           # the head, resting forward
    blob((-0.26, -0.23, 0.105), 0.06, 1.5)                                        # the muzzle
    for p in ((-0.2, -0.24, 0.05), (-0.12, -0.25, 0.045)): blob(p, 0.09, 1.6)  # front paws under the chin
    pts = [(0.27, 0.06), (0.3, -0.04), (0.27, -0.14), (0.2, -0.22), (0.11, -0.28), (0.02, -0.31), (-0.05, -0.33)]
    for i in range(len(pts) - 1):                                              # the tail, a smooth run round the front
        for t in (0.0, 0.33, 0.66):
            x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t; y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t
            blob((x, y, 0.045), 0.065, 2.2)
    ob = bpy.data.objects.new('cat_mb', mb); bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg)); bpy.data.objects.remove(ob)
    body = bpy.data.objects.new('cat_body', me); bpy.context.scene.collection.objects.link(body)
    d = body.modifiers.new('facets', 'DECIMATE'); d.ratio = 0.035                # into big flat triangles
    dg = bpy.context.evaluated_depsgraph_get(); me2 = bpy.data.meshes.new_from_object(body.evaluated_get(dg))
    body.modifiers.clear(); body.data = me2
    for p in me2.polygons: p.use_smooth = False
    body.data.materials.append(mat(FUR)); body.parent = c
    face = Vector((-0.35, -0.94, 0)).normalized(); side = Vector((0.94, -0.35, 0)); hc = Vector((-0.23, -0.17, 0.13))
    for sx in (-1, 1):                                                         # big pointed ears, a little apart
        bm = bmesh.new(); base = hc + side * (sx * 0.075) + face * 0.01 + Vector((0, 0, 0.1))
        tip = base + Vector((0, 0, 0.12)) + side * (sx * 0.035) - face * 0.015
        v = [bm.verts.new(base + side * 0.05), bm.verts.new(base - side * 0.05), bm.verts.new(base - face * 0.055), bm.verts.new(tip)]
        for f in ((0, 1, 3), (1, 2, 3), (2, 0, 3), (0, 2, 1)): bm.faces.new([v[i] for i in f])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); em = bpy.data.meshes.new('ear'); bm.to_mesh(em); bm.free()
        for p in em.polygons: p.use_smooth = False
        eo = bpy.data.objects.new('cat_ear', em); bpy.context.scene.collection.objects.link(eo); eo.data.materials.append(mat(FUR)); eo.parent = c
        e0 = hc + face * 0.135 + side * (sx * 0.045) + Vector((0, 0, 0.02))        # a closed eye: a short dark curve on the face
        tube('cat_eye', [tuple(e0 - side * 0.018), tuple(e0 + Vector((0, 0, -0.006))), tuple(e0 + side * 0.018)], 0.004, DARK, c)
    return c
