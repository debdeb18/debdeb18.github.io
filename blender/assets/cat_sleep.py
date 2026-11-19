"""A low-poly cat curled up asleep, after the user's reference: a round body made of many small flat triangles, a big
head with pointed ears resting on its front paws, eyes shut, the tail wrapped round along the front. Origin under its
middle; it faces -Y. The porch puts it in the tower nook as 'cat_sleep'."""
import math, bmesh
from lib import *
VIEW = dict(angle=-20, lift=0.35, res=(900, 640), samples=32)
FUR = 0xE39C5A

def tri(name, rr, loc, scale, parent, rot=(0, 0, 0), sub=2, color=FUR):
    """An icosphere of flat triangles, squashed into shape."""
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=rr)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = False
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.scale = scale; o.rotation_euler = [math.radians(a) for a in rot]
    o.data.materials.append(mat(color)); o.parent = parent
    return o

def ear(name, loc, rot, parent):
    bm = bmesh.new()
    v = [bm.verts.new(p) for p in ((-0.035, -0.02, 0), (0.035, -0.02, 0), (0, 0.025, 0), (0.005, -0.005, 0.085))]
    for f in ((0, 1, 3), (1, 2, 3), (2, 0, 3), (0, 2, 1)): bm.faces.new([v[i] for i in f])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.rotation_euler = [math.radians(a) for a in rot]; o.data.materials.append(mat(FUR)); o.parent = parent
    return o

def build(parent=None, name='cat_sleep'):
    c = root(name)
    if parent: c.parent = parent
    tri('body', 0.2, (0.05, 0.03, 0.11), (1.25, 1.0, 0.62), c, rot=(0, 0, 8))          # the round curled back
    tri('haunch', 0.13, (0.17, 0.05, 0.11), (1.0, 1.0, 0.85), c)
    tri('chest', 0.11, (-0.11, -0.05, 0.08), (1.1, 1.0, 0.7), c)
    for sx, dx in ((-1, 0.0), (1, 0.06)): tri('paw', 0.045, (-0.18 + dx, -0.17 + sx * 0.0, 0.035), (1.7, 0.9, 0.7), c, rot=(0, 0, 25), sub=1)
    tri('head', 0.115, (-0.2, -0.11, 0.12), (1.0, 1.05, 0.85), c, rot=(0, 0, 25))
    tri('cheeks', 0.07, (-0.23, -0.15, 0.095), (1.25, 1.0, 0.75), c, rot=(0, 0, 25), sub=1)
    tri('muzzle', 0.035, (-0.25, -0.2, 0.085), (1.0, 1.1, 0.8), c, sub=1)
    e1 = ear('ear', (-0.25, -0.06, 0.19), (8, -18, 25), c); e2 = ear('ear', (-0.14, -0.1, 0.2), (8, 15, 25), c)
    for e in (e1, e2): e.scale = (1.35, 1.35, 1.35)
    for (x, y) in ((-0.265, -0.17), (-0.21, -0.2)): box('eye', (0.03, 0.005, 0.006), (x, y - 0.03, 0.125), (0, 0, 25), 0x6A3E22, c, bevel=0)   # shut
    pts = [(0.27, 0.03, 0.05), (0.29, -0.05, 0.047), (0.27, -0.12, 0.044), (0.21, -0.18, 0.04), (0.13, -0.22, 0.04), (0.04, -0.24, 0.04), (-0.05, -0.25, 0.043), (-0.11, -0.24, 0.047)]
    for i in range(len(pts) - 1):                                              # the tail round the front, in faceted pieces
        (ax, ay, az), (bx, by, bz) = pts[i], pts[i + 1]; ln = math.hypot(bx - ax, by - ay)
        tri('tail', 0.04, ((ax + bx) / 2, (ay + by) / 2, (az + bz) / 2), (ln / 0.045, 0.85, 0.8), c, rot=(0, 0, math.degrees(math.atan2(by - ay, bx - ax))), sub=1)
    return c
