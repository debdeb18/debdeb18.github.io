"""Close-up renders of one asset's details:  python blender/scenes/closeups.py halt   -> blender/previews/<asset>-<view>.png"""
import sys, os, math, importlib, random
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, here)
import bpy
from mathutils import Vector
import lib
VIEWS = {   # asset: {view: (camera position, look at, lens)}
    'halt': {'vending': ((-2.2, -2.6, 1.9), (-2.7, 1.4, 1.75), 45), 'seats': ((2.6, -2.0, 2.0), (2.1, 1.7, 1.25), 32), 'signal': ((-3.4, -4.8, 2.6), (-4.75, -1.55, 3.0), 38)},
}
name = sys.argv[1]
lib.reset(); random.seed(7)
importlib.import_module('assets.' + name).build()
sc = bpy.context.scene
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.98, 0.78, 0.62, 1); bg.inputs[1].default_value = 0.9
sun = bpy.data.lights.new('s', 'SUN'); sun.energy = 3.0; sun.color = (1, 0.88, 0.75); so = bpy.data.objects.new('s', sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(55), 0, math.radians(-30))
g = lib.box('ground', (40, 40, 0.1), (0, 0, -0.1), color=0xD8CBB0, bevel=0)
cam = bpy.data.cameras.new('c'); co = bpy.data.objects.new('c', cam); sc.collection.objects.link(co); sc.camera = co
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 32; sc.cycles.use_denoising = True; sc.view_settings.view_transform = 'Standard'
sc.render.resolution_x, sc.render.resolution_y = 900, 700
for v, (p, a, lens) in VIEWS[name].items():
    cam.lens = lens; co.location = p; co.rotation_euler = (Vector(a) - Vector(p)).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = '%s/previews/%s-%s.png' % (here, name, v); bpy.ops.render.render(write_still=True); print('RENDERED', v)
