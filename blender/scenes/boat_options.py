"""Boat options side by side on the water.   python blender/scenes/boat_options.py -> blender/concepts/boat-options.png"""
import sys, os, math, random
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, here)
import bpy
from mathutils import Vector
import lib
from lib import *
from assets import boat
lib.reset(); random.seed(2)
box('water', (40, 40, 0.1), (0, 0, -0.1), color=0x5FA8B8, bevel=0)
for i, s in enumerate('ABC'):
    b = boat.build(s); b.location = (-3.6 + i * 3.6, 0, 0.02); b.rotation_euler = (0, 0, math.radians(25))
    text('label', s, 0.35, (-3.6 + i * 3.6, -1.6, 0.0), rot=(0, 0, 0), color=0x3B3A4A)
sc = bpy.context.scene
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.62, 0.78, 0.95, 1)
sun = bpy.data.lights.new('s', 'SUN'); sun.energy = 3.4; sun.color = (1, 0.93, 0.82); so = bpy.data.objects.new('s', sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(-30))
cam = bpy.data.cameras.new('c'); co = bpy.data.objects.new('c', cam); sc.collection.objects.link(co); sc.camera = co; cam.lens = 30
co.location = (0, -9.5, 4.6); co.rotation_euler = (Vector((0, 0, 0.2)) - co.location).to_track_quat('-Z', 'Y').to_euler()
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 32; sc.cycles.use_denoising = True; sc.view_settings.view_transform = 'Standard'
sc.render.resolution_x, sc.render.resolution_y = 1600, 700
sc.render.filepath = here + '/concepts/boat-options.png'; bpy.ops.render.render(write_still=True); print('RENDERED')
