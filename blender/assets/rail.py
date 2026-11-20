"""A stretch of railway track lying on the sea floor, after the user's reference: heavy steel rails with a real rail
profile (rounded head, thin web, wide foot), blue-grey with a bright worn line along the top; dark, weathered sleepers
laid close together, each a little different; spikes and tie plates holding the rails; pebbles and sand settled
between the sleepers, no raised bank. Built along X, centred; origin on the sea floor at the track's middle."""
import math, random, bmesh
from mathutils import Vector, Matrix
from lib import *
VIEW = dict(angle=-25, lift=0.35, res=(1100, 650), samples=32, zoom=1.6)
LEN, GAUGE = 12.0, 1.435
STEEL, STEEL_TOP, SLEEPER, SLEEPER_D, PLATE, BED = 0x5E6B7C, 0xC9D3DD, 0x55493F, 0x433A34, 0x3A3D44, 0xA9A08A

def rail_bar(name, y, parent):
    """One rail: an extruded rail profile along X, with its worn top as a separate bright strip."""
    prof = [(-0.07, 0.0), (0.07, 0.0), (0.07, 0.012), (0.012, 0.024), (0.01, 0.1), (0.034, 0.112), (0.036, 0.14), (0.026, 0.15),
            (-0.026, 0.15), (-0.036, 0.14), (-0.034, 0.112), (-0.01, 0.1), (-0.012, 0.024), (-0.07, 0.012)]
    bm = bmesh.new(); n = len(prof)
    ends = [[bm.verts.new((x, y + py, pz)) for (py, pz) in prof] for x in (-LEN / 2, LEN / 2)]
    for i in range(n): bm.faces.new((ends[0][i], ends[0][(i + 1) % n], ends[1][(i + 1) % n], ends[1][i]))
    bm.faces.new(ends[0][::-1]); bm.faces.new(ends[1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.data.materials.append(mat(STEEL, rough=0.35)); o.parent = parent
    box('rail_top', (LEN, 0.04, 0.006), (0, y, 0.148), color=STEEL_TOP, parent=parent, bevel=0.002, rough=0.25)   # the worn shine
    return o

def pebble_bed(r, rnd):
    """A light scatter of real 3D stones where the rails meet the ground, the rest of the bed being the painted gravel
    below: smooth, flattened river stones (under 100 faces each), sunk halfway in so only their rounded tops show
    between the sleepers, in the bed's own stone tones so they blend into it from afar."""
    tones = [Vector(((h >> 16 & 255) / 255, (h >> 8 & 255) / 255, (h & 255) / 255)) for h in (0x648791, 0x648791, 0x7A9BA4, 0x9EBBC0, 0x55747E)]
    bm = bmesh.new(); col = bm.verts.layers.color.new('Col')
    for _ in range(240):
        y = rnd.uniform(-1.3, 1.3)
        if abs(y) > 0.95 and rnd.random() < 0.6: continue                         # fewer out at the sides
        x = rnd.uniform(-LEN / 2, LEN / 2); rr = rnd.uniform(0.045, 0.085)
        sq = (rnd.uniform(1.0, 1.4), rnd.uniform(0.8, 1.05), rnd.uniform(0.45, 0.6))   # flattened: a river stone
        m = Matrix.Translation((x, y, 0.0)) @ Matrix.Rotation(rnd.uniform(0, 6.3), 4, 'Z') @ Matrix.Diagonal((sq[0] * rr, sq[1] * rr, sq[2] * rr, 1))
        res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=m)   # 80 faces, smooth shaded; its centre on the
        base = rnd.choice(tones)                                                        # ground, so half of it is sunk in
        for v in res['verts']:
            t = max(0.0, min(1.0, v.co.z / (rr * sq[2])))
            c = base * (0.8 + 0.35 * t)                                               # lighter on top
            v[col] = (min(1, c.x), min(1, c.y), min(1, c.z), 1.0)
    me = bpy.data.meshes.new('pebbles'); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new('pebbles', me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat_vc(0xFFFFFF, rough=0.6)); o.parent = r
    return o

def build():
    r = root('rail'); rnd = random.Random(4)
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)   # the track bed: painted gravel
    for v in bm.verts: v.co.x *= LEN; v.co.y *= 2.8; v.co.z = 0.0                          # (src/paint.js, 'pebbles')
    me = bpy.data.meshes.new('underlayer'); bm.to_mesh(me); bm.free()
    ul = bpy.data.objects.new('underlayer', me); bpy.context.scene.collection.objects.link(ul); ul.data.materials.append(mat(BED)); ul.parent = r
    pebble_bed(r, rnd)
    x = -LEN / 2 + 0.25
    while x < LEN / 2:                                                          # sleepers close together, each a bit different
        w = rnd.uniform(0.2, 0.24)
        plank('sleeper', (2.5 + rnd.uniform(-0.05, 0.05), w, 0.13), (x, rnd.uniform(-0.03, 0.03), -0.02), (0, 0, 90 + rnd.uniform(-2.5, 2.5)),
              rnd.choice((SLEEPER, SLEEPER, SLEEPER_D)), r, bevel=0.02, nails=False)
        for sy in (-1, 1):                                                      # tie plates and spikes
            yy = sy * GAUGE / 2
            box('plate', (w * 0.9, 0.3, 0.012), (x, yy, 0.11), color=PLATE, parent=r, bevel=0.003)
            for dy in (-0.09, 0.09): cyl('spike', 0.012, 0.012, 0.03, (x + rnd.uniform(-0.03, 0.03), yy + dy, 0.115), color=PLATE, parent=r, bevel=0.003, verts=6)
        x += rnd.uniform(0.42, 0.48)
    for sy in (-1, 1):
        o = rail_bar('rail', sy * GAUGE / 2, r); o.location = (0, 0, 0.122)
    for o in [c for c in r.children if c.name.startswith('rail_top')]: o.location.z += 0.122
    return r
