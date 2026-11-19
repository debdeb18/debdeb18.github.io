"""Mooring post options, standing on a strip of the deck's planks.   python blender/scenes/bollard_options.py -> blender/concepts/bollard-options.png"""
import sys, os, math, random
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, here)
import bpy
from mathutils import Vector
import lib
from lib import *
from assets import halt as H
lib.reset(); PAL.update(H.COLOURS); rnd = random.Random(5); random.seed(5)
PAL.update(dict(rope=0xD9C08E, iron=0x3A3D44, rust=0x8A5236, ring=0x5A5C62))
r = root('opts')
for i in range(26): plank('deck', (1.2, 0.3, 0.12), (-5.2 + i * 0.4, 0, -0.12), (0, 0, 90 + rnd.uniform(-1, 1)), rnd.choice(('plank', 'plank_d')), r, bevel=0.016)
def label(t, x): text('label', t, 0.22, (x, -1.0, 0.02), color=0x3B3A4A)
def coil(x, y, z, rr=0.2):
    for k in range(3): cyl('coil', rr - k * 0.045, rr - k * 0.045, 0.04, (x, y, z + k * 0.035), color='rope', parent=r, bevel=0.018, verts=20)
# A: the current one, a turned timber post with a round cap
X = -4.0
cyl('post', 0.12, 0.1, 0.55, (X, 0, 0), color='plank_d', parent=r, bevel=0.03, verts=12); ball('cap', 0.13, (X, 0, 0.55), (1, 1, 0.5), 'plank_d', r); label('A', X)
# B: an old pile sticking up through the deck, rope wound round it, its top weathered and split
X = -2.0
box('pile', (0.24, 0.24, 0.9), (X, 0, 0), (0, 0, 8), 'plank_d', r, bevel=0.035, jitter=0.02, taper=0.9)
for k in range(5): cyl('wrap', 0.17, 0.17, 0.04, (X, 0, 0.35 + k * 0.045), (rnd.uniform(-6, 6), rnd.uniform(-6, 6), 0), 'rope', r, bevel=0.018, verts=16)
tube('rope', [(X + 0.15, 0, 0.42), (X + 0.45, -0.2, 0.1), (X + 0.9, -0.35, 0.02)], 0.03, 'rope', r); label('B', X)
# C: a cast-iron bollard, the classic mushroom shape, a little rust
X = 0.0
cyl('base', 0.24, 0.24, 0.06, (X, 0, 0), color='iron', parent=r, bevel=0.015, verts=24)
cyl('body', 0.13, 0.16, 0.36, (X, 0, 0.06), color='iron', parent=r, bevel=0.02, verts=24)
cyl('lip', 0.22, 0.2, 0.08, (X, 0, 0.42), color='iron', parent=r, bevel=0.03, verts=24); ball('dome', 0.18, (X, 0, 0.5), (1, 1, 0.45), 'iron', r)
for a in range(6): ball('rust', 0.035, (X + 0.15 * math.cos(a), 0.15 * math.sin(a), 0.2 + 0.04 * a), (1, 1, 0.6), 'rust', r)
coil(X + 0.55, 0.05, 0.0); label('C', X)
# D: a stone bollard cut from the ruin's pale stone, with an iron ring
X = 2.0
painted_box('stone', (0.36, 0.36, 0.6), (X, 0, 0), (0, 0, 10), color='stone_c', parent=r, bevel=0.07, along='x', rough=2.0, chisel=1.0)
cyl('ring', 0.12, 0.12, 0.025, (X, -0.2, 0.42), (90, 0, 0), 'ring', r, bevel=0.012, verts=20)
tube('ring_loop', [(X - 0.12, -0.21, 0.42), (X, -0.24, 0.3), (X + 0.12, -0.21, 0.42)], 0.018, 'ring', r); label('D', X)
# E: two short twin posts (a cleat) with a rope figure-of-eight over them
X = 4.0
for sx in (-1, 1): cyl('twin', 0.085, 0.075, 0.38, (X + sx * 0.16, 0, 0), color='plank_d', parent=r, bevel=0.025, verts=12)
box('bar', (0.5, 0.1, 0.07), (X, 0, 0.26), color='plank', parent=r, bevel=0.015)
tube('fig8', [(X - 0.16, 0.09, 0.3), (X + 0.16, -0.09, 0.33), (X + 0.16, 0.09, 0.35), (X - 0.16, -0.09, 0.37), (X - 0.16, 0.09, 0.39)], 0.025, 'rope', r)
tube('rope', [(X + 0.2, -0.05, 0.3), (X + 0.6, -0.4, 0.06), (X + 1.0, -0.5, 0.02)], 0.025, 'rope', r); label('E', X)
sc = bpy.context.scene
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.62, 0.78, 0.95, 1)
sun = bpy.data.lights.new('s', 'SUN'); sun.energy = 3.4; sun.color = (1, 0.93, 0.82); so = bpy.data.objects.new('s', sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(-30))
cam = bpy.data.cameras.new('c'); co = bpy.data.objects.new('c', cam); sc.collection.objects.link(co); sc.camera = co; cam.lens = 24
co.location = (0.2, -6.4, 2.0); co.rotation_euler = (Vector((0.2, 0, 0.25)) - co.location).to_track_quat('-Z', 'Y').to_euler()
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 32; sc.cycles.use_denoising = True; sc.view_settings.view_transform = 'Standard'
sc.render.resolution_x, sc.render.resolution_y = 1600, 620
sc.render.filepath = here + '/concepts/bollard-options.png'; bpy.ops.render.render(write_still=True); print('RENDERED')
