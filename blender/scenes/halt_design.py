"""Design sheet for the halt (step 1) and the layout (step 2).
    python blender/scenes/halt_design.py [view ...]   -> blender/concepts/halt-*.png, layout-*.png
Views: halt34, haltlow, booth (the halt alone on its stretch of line), plan (top-down layout), view (the layout as a scene)."""
import sys, os, math, random
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, here)
import bpy
from mathutils import Vector
import lib
from lib import box, cyl, ball, tube, mat, lump, text
from assets import halt, chair, suitcase, station_sign, tree as tree_asset

TRACK = -3.2
lib.reset(); random.seed(5)
lib.set_style(jitter=1.0, pal=dict(tree=0x256B45, tree_mid=0x3C8C4C, tree_light=0x7CBC58, tree_hi=0xC2E272, trunk=0x5A3F30,
                                   grass=0x7DB85A, sand=0xE6D6A8))
# ---------- sea, sea floor, the line on its ballast bank ----------
box('seabed', (500, 500, 0.1), (0, 0, -2.6), color=0x24508C, bevel=0)
sea = box('sea', (500, 500, 2.4), (0, 0, -2.4), color=0xFFFFFF, bevel=0)
wm = sea.data.materials[0]; wm.name = 'water'; nt = wm.node_tree; b = nt.nodes['Principled BSDF']
b.inputs['Roughness'].default_value = 0.02; b.inputs['Transmission Weight'].default_value = 1.0; b.inputs['IOR'].default_value = 1.33
va = nt.nodes.new('ShaderNodeVolumeAbsorption'); va.inputs['Color'].default_value = (0.12, 0.42, 0.72, 1); va.inputs['Density'].default_value = 0.9
nt.links.new(va.outputs[0], nt.nodes['Material Output'].inputs['Volume'])
box('bank', (300, 3.6, 0.6), (0, TRACK, -0.85), color=0x8C97A3, bevel=0.3)
for dy in (-0.72, 0.72): box('rail', (300, 0.07, 0.14), (0, TRACK + dy, -0.19 + 0.25), color=0x7E7A82, bevel=0.012, rough=0.3)
x = -150.0
while x < 150: box('sleeper', (0.24, 2.4, 0.14), (x, TRACK, -0.3 + 0.25), color=0x4A3226, bevel=0.02); x += 0.7

# ---------- the halt, with the chair, the suitcase and the sign on it ----------
H = halt.build(); H.location = (0, 0.5, 0)                      # its front edge sits 1.5 m from the track centre
c = chair.build(); c.location = (-1.0, -0.6, halt.TOP); c.rotation_euler = (0, 0, 0.15)
s = suitcase.build(); s.location = (-0.2, -0.65, halt.TOP); s.rotation_euler = (0, 0, -0.3)
g = station_sign.build(); g.location = (-1.6, 2.1, halt.TOP); g.scale = (0.7, 0.7, 0.7)

LAYOUT = 'plan' in sys.argv or 'view' in sys.argv
if LAYOUT:
    # ---------- step 2: the layout ----------
    def island(x, y, r, sq=(1.0, 1.0), sand=True):
        if sand: ball('isl_sand', r * 1.12, (x, y, -0.25), (sq[0], sq[1], 0.06), 0xE6D6A8, rough=1)
        ball('isl_grass', r, (x, y, -0.1), (sq[0], sq[1], 0.07), 0x7DB85A, rough=1)
    # the big island behind the halt, a boardwalk across to it
    BX, BY, BR = 2.0, 15.0, 10.0
    island(BX, BY, BR, (1.25, 0.8))
    for i in range(12): box('boardwalk', (1.4, 0.36, 0.06), (3.2, 3.1 + i * 0.4, 0.55 - i * 0.02), color=0xA07650, bevel=0.01)
    for i in range(0, 12, 3):
        for sx in (-0.65, 0.65): cyl('bw_post', 0.06, 0.06, 1.6, (3.2 + sx, 3.1 + i * 0.4, -1.0), color=0x5C4033, bevel=0.005, verts=8)
    # the house (step 3, a placeholder for now): white walls, red roof, like the reference
    box('house', (5.0, 4.0, 3.0), (0.5, 17.0, 0.6), color=0xF2EEE4, bevel=0.05)
    box('house_roof', (5.6, 4.6, 1.5), (0.5, 17.0, 3.6), color=0xB8483A, bevel=0.1, taper=0.25)
    text('label', 'house (step 3)', 0.6, (0.5, 14.6, 1.8), color=0x3B3A4A)
    for (x, y, h, rr, sd) in ((8.5, 19, 6, 3.6, 0), (-6, 13, 5, 3.0, 2)):
        t = tree_asset.build(h, rr, seed=sd); t.location = (x, y, 0.1)
    # the small islets that stay: the footbridge pair and the boat, beside the big island to the east
    island(19, 13, 3.6); island(31, 15, 4.2)
    p0, p1 = (22.2, 13.6), (27.4, 14.4); n = 14
    for k in range(n + 1):
        t = k / n; px, py = p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t
        box('fb', (0.36, 1.2, 0.06), (px, py, 0.45 + math.sin(math.pi * t) * 0.9), (0, 0, 8), color=0xA07650, bevel=0.01)
    tube('fb_rail', [(p0[0], p0[1] + 0.6, 1.3), ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + 0.6, 2.2), (p1[0], p1[1] + 0.6, 1.3)], 0.04, 0xC23B3B)
    tube('fb_rail', [(p0[0], p0[1] - 0.6, 1.3), ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - 0.6, 2.2), (p1[0], p1[1] - 0.6, 1.3)], 0.04, 0xC23B3B)
    box('boat', (3.2, 1.25, 0.5), (16, 6.5, -0.12), (0, 0, 20), color=0x4F8FA0, bevel=0.2, taper=1.25)
    for (x, y, h, rr, sd) in ((19, 13.5, 5.5, 3.2, 1), (31, 15.5, 6, 3.5, 0)):
        t = tree_asset.build(h, rr, seed=sd); t.location = (x, y, 0.1)
    # a couple more islets out on the open sea, south of the line
    island(-14, -16, 3.0); island(24, -18, 2.6)
    t = tree_asset.build(5, 3, seed=2); t.location = (-14, -16, 0.1)

# ---------- light, sky, cameras ----------
sc = bpy.context.scene
w = bpy.data.worlds.new('sky'); sc.world = w; w.use_nodes = True; bg = w.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.42, 0.62, 0.95, 1); bg.inputs[1].default_value = 1.0
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 3.6; sun.color = (1, 0.95, 0.86); sun.angle = math.radians(3)
so = bpy.data.objects.new('sun', sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(55), 0, math.radians(-35))
cam = bpy.data.cameras.new('cam'); co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = int(os.environ.get('SAMPLES', 40)); sc.cycles.use_denoising = True
sc.cycles.max_bounces = 8; sc.view_settings.view_transform = 'Standard'
sc.render.resolution_x, sc.render.resolution_y = 1300, 820
VIEWS = {   # name: (position, look at, lens, orthographic scale or 0)
    'halt34':  ((9, -11, 6.5), (0, 0.3, 0.8), 32, 0),
    'haltlow': ((-11, -6.5, 1.6), (0, 0.5, 1.6), 30, 0),
    'booth':   ((5.5, -3.2, 2.2), (2.75, 1.6, 1.9), 35, 0),
    'plan':    ((8, 3, 80), (8, 3.01, 0), 0, 62),
    'view':    ((-30, -12, 8), (8, 9, 0.5), 28, 0),
}
os.makedirs(here + '/concepts', exist_ok=True)
for name in (sys.argv[1:] or ['halt34', 'haltlow', 'booth']):
    pos, at, lens, ortho = VIEWS[name]
    cam.type = 'ORTHO' if ortho else 'PERSP'
    if ortho: cam.ortho_scale = ortho
    else: cam.lens = lens
    co.location = pos; co.rotation_euler = (Vector(at) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = '%s/concepts/%s-%s.png' % (here, 'layout' if name in ('plan', 'view') else 'halt', name)
    bpy.ops.render.render(write_still=True); print('RENDERED', name)
