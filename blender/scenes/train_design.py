"""Design sheet for a train design (TRAIN=railcar, design A, or TRAIN=seatrain, design B): the car on a short stretch of sunken track, from several angles, by day and at dusk.
    python blender/scenes/train_design.py      -> blender/concepts/train-*.png, blender/files/railcar.blend"""
import sys, os, math, random
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, here)
import bpy
from mathutils import Vector
import lib
from lib import box, cyl, mat
import importlib
TRAIN = os.environ.get('TRAIN', 'railcar')
model = importlib.import_module('assets.' + TRAIN)

lib.reset(); random.seed(3)
lib.set_style(jitter=1.0)
car = model.build()
car.location = (0, 0, -0.05)

# a short stretch of the line, just under clear shallow water, like the terminal
box('ballast', (3.0, 60, 0.3), (0, 12, -0.52), color=0xC9BFA8, bevel=0.1)
for dx in (-0.72, 0.72): box('rail', (0.07, 60, 0.14), (dx, 12, -0.19), color=0x7E7A82, bevel=0.012, rough=0.3)
y = -14.0
while y < 42: box('sleeper', (2.4, 0.24, 0.14), (0, y, -0.3), color=0x4A3226, bevel=0.02, jitter=0.012); y += 0.7
box('seabed', (80, 80, 0.1), (0, 6, -0.62), color=0xE6D6A8, bevel=0)
sea = box('sea', (80, 80, 0.6), (0, 6, -0.6), color=0xFFFFFF, bevel=0)
wm = sea.data.materials[0]; wm.name = 'water'; nt = wm.node_tree; b = nt.nodes['Principled BSDF']
b.inputs['Roughness'].default_value = 0.05; b.inputs['Transmission Weight'].default_value = 1.0; b.inputs['IOR'].default_value = 1.33
va = nt.nodes.new('ShaderNodeVolumeAbsorption'); va.inputs['Color'].default_value = (0.2, 0.68, 0.74, 1); va.inputs['Density'].default_value = 0.6
nt.links.new(va.outputs[0], nt.nodes['Material Output'].inputs['Volume'])

sc = bpy.context.scene
w = bpy.data.worlds.new('sky'); sc.world = w; w.use_nodes = True; bg = w.node_tree.nodes['Background']
sun = bpy.data.lights.new('sun', 'SUN'); so = bpy.data.objects.new('sun', sun); sc.collection.objects.link(so); sun.angle = math.radians(4)
inside = []
for i in range(4 if TRAIN == 'railcar' else 7):
    l = bpy.data.lights.new('cabin', 'POINT'); l.color = (1, 0.78, 0.5); l.shadow_soft_size = 0.3
    o = bpy.data.objects.new('cabin', l); o.location = (0, 4.2 + i * (2.6 if TRAIN == 'railcar' else 3.9), 2.6); sc.collection.objects.link(o); inside.append(l)
spot = bpy.data.lights.new('beam', 'SPOT'); spot.spot_size = math.radians(40); spot.color = (1, 0.9, 0.7)
bo = bpy.data.objects.new('beam', spot); bo.location = (0, 0.3, 3.55); bo.rotation_euler = (math.radians(100), 0, 0); sc.collection.objects.link(bo)
cam = bpy.data.cameras.new('cam'); co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = int(os.environ.get('SAMPLES', 64)); sc.cycles.use_denoising = True
sc.cycles.max_bounces = 8; sc.view_settings.view_transform = 'Standard'
try: sc.view_settings.look = 'Medium High Contrast'
except Exception: pass
sc.render.resolution_x, sc.render.resolution_y = 1400, 860
emis = [(m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'], m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value) for m in bpy.data.materials if m.node_tree and 'Principled BSDF' in m.node_tree.nodes]

def mood(day):
    bg.inputs[0].default_value = (0.55, 0.75, 1.0, 1) if day else (0.16, 0.18, 0.4, 1); bg.inputs[1].default_value = 0.9 if day else 0.45
    sun.energy = 4.0 if day else 1.4; sun.color = (1, 0.96, 0.88) if day else (1, 0.55, 0.35)
    so.rotation_euler = (math.radians(50 if day else 82), 0, math.radians(30 if day else 120))
    for l in inside: l.energy = 25 if day else 70
    spot.energy = 0 if day else 400
    for inp, base in emis: inp.default_value = base * (0.6 if day else 2.5)

VIEWS_B = {   # design B is two cars long, and its cab front starts at y = 0
    'front':      ((-6.5, -9.5, 2.4), (0, 4.0, 1.8), 40, True),
    'side':       ((-19, 14.3, 2.2), (0, 14.3, 1.7), 32, True),
    'rear':       ((6.5, 38, 3.0), (0, 22, 1.8), 40, True),
    'nose':       ((-2.6, -3.6, 3.0), (0, 0.6, 2.2), 40, True),
    'inside':     ((0.15, 2.4, 2.35), (0, 14.0, 1.7), 28, True),
    'dusk':       ((-7.5, -11, 1.8), (0, 5.0, 2.0), 38, False),
}
VIEWS = {   # name: camera position, looking at, lens, day?
    'front':      ((-5.5, -8.5, 2.6), (0, 3.0, 1.9), 40, True),
    'side':       ((-12.5, 7.6, 2.4), (0, 7.6, 1.8), 30, True),
    'rear':       ((5.5, 22.5, 3.2), (0, 9.5, 1.8), 40, True),
    'nose':       ((-2.4, -3.2, 3.4), (0, 1.2, 2.7), 42, True),
    'inside':     ((0.3, 3.0, 2.45), (-0.3, 12.0, 1.75), 26, True),
    'dusk':       ((-6.5, -10, 2.0), (0, 3.5, 2.2), 38, False),
}
if TRAIN != 'railcar': VIEWS = VIEWS_B
os.makedirs(here + '/concepts', exist_ok=True)
for name in (sys.argv[1:] or VIEWS):
    pos, at, lens, day = VIEWS[name]
    mood(day); cam.lens = lens
    co.location = pos; co.rotation_euler = (Vector(at) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = '%s/concepts/%s-%s.png' % (here, 'train' if TRAIN == 'railcar' else 'train-b', name)
    bpy.ops.render.render(write_still=True); print('RENDERED', name)
bpy.ops.wm.save_as_mainfile(filepath=here + '/files/%s.blend' % TRAIN)
