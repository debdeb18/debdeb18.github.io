"""Design options for the station's info board, side by side in front of a stretch of the ruin's pale stone wall.
    python blender/scenes/board_options.py   -> blender/concepts/board-options.png"""
import sys, os, math, random
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, here)
import bpy
from mathutils import Vector
import lib
from lib import *
from assets import halt as H

lib.reset(); PAL.update(H.COLOURS); rnd = random.Random(3); random.seed(3)
PAL.update(dict(paper=0xF3EAD2, ink=0x3B3A4A, blue=0x2F6F9A, enamel=0xF4F1EA, brass=0xC9A043, rope=0xD9C08E))
r = root('options')
# ground and a stretch of wall behind
for i in range(14):
    for j in range(4): painted_box('floor', (0.85, 0.8, 0.2), (-5.6 + i * 0.86, -1.2 + j * 0.81, -0.2), color=rnd.choice(('stone_a', 'stone_b', 'stone_c')), parent=r, bevel=0.04, along='top', band=0.1, rough=2.0)
z = 0; row = 0
while z < 2.6:
    a = -5.6 - (0.4 if row % 2 else 0)
    while a < 6:
        l = rnd.uniform(0.7, 1.1); a0, a1 = max(a, -5.6), min(a + l, 6); a += l
        if a1 - a0 > 0.2: H.ruin_block(r, rnd, (a1 - a0 - 0.03, 0.6, 0.42), ((a0 + a1) / 2, 1.9, z), (0, 0, 0), 'x', 0, crack=0.1, backing=True)
    z += 0.45; row += 1

def timetable(x, y, z, w, h, head=0x2F6F9A, rows=7):
    box('paper', (w, 0.02, h), (x, y, z), color='paper', parent=r, bevel=0.004)
    box('head', (w, 0.025, 0.12), (x, y - 0.002, z + h - 0.13), color=head, parent=r, bevel=0.003)
    for i in range(rows):
        for c, lw in ((-w * 0.27, w * 0.35), (w * 0.17, w * 0.45)):
            box('line', (lw, 0.025, 0.026), (x + c, y - 0.004, z + 0.08 + i * (h - 0.25) / rows), color='ink', parent=r, bevel=0)

# A: carved stone stele with a timber frame and a small tiled roof
X = -3.6
painted_box('stele_base', (1.5, 0.5, 0.3), (X, 0.6, 0), color='stone_b', parent=r, bevel=0.05, along='top', band=0.1, rough=2.4, chisel=1.0)
painted_box('stele', (1.3, 0.32, 1.7), (X, 0.62, 0.3), color='stone_c', parent=r, bevel=0.06, along='x', rough=2.0, chisel=0.8)
for sx in (-1, 1): box('frame_v', (0.08, 0.06, 1.28), (X + sx * 0.5, 0.44, 0.55), color='timber', parent=r, bevel=0.012, jitter=0.004)
for zz in (0.53, 1.79): box('frame_h', (1.08, 0.06, 0.08), (X, 0.44, zz), color='timber', parent=r, bevel=0.012, jitter=0.004)
timetable(X, 0.42, 0.68, 0.9, 1.0)
shingles('stele_roof', 1.6, 0.55, 1, (X, 0.15, 2.05), 20, color='roof', dark='roof_dark', parent=r, tile=0.32)
shingles('stele_roof', 1.6, 0.55, 1, (X, 1.1, 2.05), 20, color='roof', dark='roof_dark', parent=r, tile=0.32, yaw=180)
text('label', 'A', 0.3, (X, -1.6, 0.25), color='ink')

# B: weathered plank board on two leaning posts, hand-painted, a lantern hung from the post, rope ties
X = 0.0
for sx in (-1, 1): box('post', (0.14, 0.14, 2.3), (X + sx * 0.85, 0.7, 0), (0, sx * 2, 0), 'plank_d', r, bevel=0.03, jitter=0.012)
for k in range(5): plank('board', (1.85, 0.25, 0.05), (X, 0.62, 0.7 + k * 0.255), (90, 0, rnd.uniform(-1.5, 1.5)), rnd.choice(('plank', 'plank_d')), r, bevel=0.012)
timetable(X - 0.38, 0.57, 0.8, 0.7, 1.0)
box('map', (0.72, 0.02, 0.6), (X + 0.43, 0.57, 1.15), color=0xE8F1F2, parent=r, bevel=0.004)
for (dx, dz, rr) in ((-0.15, 0.3, 0.1), (0.1, 0.38, 0.07), (0.22, 0.2, 0.05)): cyl('isl', rr, rr, 0.02, (X + 0.43 + dx, 0.555, 1.15 + dz), (90, 0, 0), 0x7DB85A, r, bevel=0, verts=14)
box('map_line', (0.62, 0.02, 0.02), (X + 0.43, 0.553, 1.47), color=0xB8403A, parent=r, bevel=0)
box('note', (0.3, 0.02, 0.32), (X + 0.43, 0.57, 0.78), color=0xF2C46A, parent=r, bevel=0.004)
for sx in (-1, 1): tube('tie', [(X + sx * 0.85, 0.6, 1.85), (X + sx * 0.92, 0.55, 1.8), (X + sx * 0.85, 0.6, 1.75)], 0.018, 'rope', r)
tube('hook', [(X + 0.85, 0.62, 2.2), (X + 1.1, 0.62, 2.25), (X + 1.15, 0.62, 2.1)], 0.015, 'iron_d', r)
cyl('lantern', 0.08, 0.08, 0.2, (X + 1.15, 0.62, 1.88), color='lamp_w', parent=r, emit=4.0, verts=12)
text('label', 'B', 0.3, (X, -1.6, 0.25), color='ink')

# C: a niche in the ruin wall: an arched recess with a timber-framed glass case, a small lamp over it
X = 3.6
painted_box('niche_back', (1.3, 0.1, 1.5), (X, 1.58, 0.45), color='joint', parent=r, bevel=0.01, along='x', rough=1.0)
for sx in (-1, 1): painted_box('jamb', (0.22, 0.4, 1.3), (X + sx * 0.76, 1.48, 0.45), color='stone_c', parent=r, bevel=0.03, along='x', rough=1.6)
pts = [(X + 0.8 * math.cos(math.pi * i / 12), 1.27, 1.75 + 0.8 * math.sin(math.pi * i / 12)) for i in range(13)]
tube('arch', [(pts[0][0], 1.27, 0.45)] + pts + [(pts[-1][0], 1.27, 0.45)], 0.07, 'stone_c', r)
painted_box('tympanum', (1.5, 0.08, 0.8), (X, 1.6, 1.75), color='joint', parent=r, bevel=0.01, along='x', rough=1.0)
painted_box('sill', (1.6, 0.5, 0.12), (X, 1.42, 0.33), color='stone_a', parent=r, bevel=0.03, along='top', rough=1.6)
box('case', (1.15, 0.1, 1.25), (X, 1.5, 0.48), color='timber', parent=r, bevel=0.02)
timetable(X - 0.27, 1.44, 0.6, 0.5, 1.0)
box('map', (0.5, 0.02, 0.5), (X + 0.28, 1.44, 1.08), color=0xE8F1F2, parent=r, bevel=0.004)
cyl('isl', 0.09, 0.09, 0.02, (X + 0.24, 1.43, 1.36), (90, 0, 0), 0x7DB85A, r, bevel=0, verts=14)
box('note', (0.4, 0.02, 0.38), (X + 0.28, 1.44, 0.62), color=0xE8A0A0, parent=r, bevel=0.004)
for sx in (-1, 1): box('case_side', (0.05, 0.12, 1.25), (X + sx * 0.55, 1.42, 0.48), color='timber_dark', parent=r, bevel=0.01)
for zz in (0.46, 1.71): box('case_rail', (1.15, 0.12, 0.05), (X, 1.42, zz), color='timber_dark', parent=r, bevel=0.01)
tube('lamp_arm', [(X + 1.0, 1.6, 2.0), (X + 1.0, 1.3, 2.05), (X + 1.0, 1.15, 1.95)], 0.02, 'iron_d', r)
cyl('lamp', 0.08, 0.08, 0.18, (X + 1.0, 1.15, 1.75), color='lamp_w', parent=r, emit=4.0, verts=12)
text('label', 'C', 0.3, (X, -1.6, 0.25), color='ink')

sc = bpy.context.scene
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.62, 0.78, 0.95, 1); bg.inputs[1].default_value = 1.0
sun = bpy.data.lights.new('s', 'SUN'); sun.energy = 3.4; sun.color = (1, 0.93, 0.82); so = bpy.data.objects.new('s', sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(-30))
cam = bpy.data.cameras.new('c'); co = bpy.data.objects.new('c', cam); sc.collection.objects.link(co); sc.camera = co; cam.lens = 30
co.location = (0.5, -7.5, 2.4); co.rotation_euler = (Vector((0, 0.8, 1.1)) - co.location).to_track_quat('-Z', 'Y').to_euler()
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 32; sc.cycles.use_denoising = True; sc.view_settings.view_transform = 'Standard'
sc.render.resolution_x, sc.render.resolution_y = 1600, 760
os.makedirs(here + '/concepts', exist_ok=True)
sc.render.filepath = here + '/concepts/board-options.png'; bpy.ops.render.render(write_still=True); print('RENDERED')
