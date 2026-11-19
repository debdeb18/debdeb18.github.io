"""A stretch of railway track lying on the sea floor, after the user's reference: heavy steel rails with a real rail
profile (rounded head, thin web, wide foot), blue-grey with a bright worn line along the top; dark, weathered sleepers
laid close together, each a little different; spikes and tie plates holding the rails; pebbles and sand settled
between the sleepers, no raised bank. Built along X, centred; origin on the sea floor at the track's middle."""
import math, random, bmesh
from mathutils import Vector
from lib import *
VIEW = dict(angle=-25, lift=0.35, res=(1100, 650), samples=32, zoom=1.6)
LEN, GAUGE = 12.0, 1.435
STEEL, STEEL_TOP, SLEEPER, SLEEPER_D, PLATE, BED = 0x5E6B7C, 0xC9D3DD, 0x4A3B34, 0x3A2E2A, 0x3A3D44, 0xB8AE96

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

def build():
    r = root('rail'); rnd = random.Random(4)
    box('bed', (LEN + 0.6, 3.2, 0.08), (0, 0, -0.08), color=BED, parent=r, bevel=0.03)
    for i in range(1400):                                                        # pebbles settled on the bed and between sleepers
        x, y = rnd.uniform(-LEN / 2, LEN / 2), rnd.uniform(-1.5, 1.5)
        rock('pebble', rnd.uniform(0.03, 0.08), (x, y, -0.015), (1.3, 1.0, 0.55), (0, 0, rnd.uniform(0, 360)),
             rnd.choice((0x9AA3AB, 0xB4AC98, 0x8C8F92, 0xA89C84)), r, flat=0.4, detail=1)
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
