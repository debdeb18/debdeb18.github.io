"""Concept scene for the terminal: a small country station in an anime-background mood, rendered by day and at dusk.
    python blender/scenes/terminal_concept.py   -> blender/concepts/terminal-day.png, terminal-dusk.png, blender/files/terminal_concept.blend"""
import sys, os, math, random
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, here)
import bpy
from mathutils import Vector
import lib
from lib import box, cyl, ball, tube, shingles, mat, gable
from assets import chair, suitcase, station_sign

random.seed(11)
lib.reset()
lib.set_style(jitter=1.3, lean=1.0, pal=dict(
    wood=0x9A6A45, wood_dark=0x4E3528, wood_pale=0xC9A374, roof=0x41626F, roof_dark=0x2F4B58, cream=0xF1E6CC, stone=0xB9B2A8,
    timber=0x8A5A3C, timber_dark=0x4A3226, plaster=0xF0E4C8, concrete=0xD2CBBC, concrete_dark=0xA39C8F, gravel=0x8F877D, rail=0x7E7A82,
    grass=0x7DB85A, tree=0x2B6A45, tree_mid=0x3F8A4C, tree_light=0x78B85A, pole=0x54483F, yellow=0xF2C230, canopy=0x5E8F7A, canopy_dark=0x45725F,
    lamp=0xFFD28A, window=0xFFC777, vend=0xE8F0F4, vend_glow=0xBFE6FF, train_red=0xB8403A, train_cream=0xF0E2C0, cloud=0xFFFFFF, hill=0x4F7F86))
PZ = 0.95                                   # platform height

# ---------- ground, track ----------
box('ground', (500, 500, 0.1), (60, 0, -0.1), color='grass', bevel=0)
box('ballast', (170, 3.6, 0.28), (45, -3.2, 0), color='gravel', bevel=0.1)
for dy in (-0.72, 0.72): box('rail', (170, 0.07, 0.14), (45, -3.2 + dy, 0.3), color='rail', bevel=0.012, rough=0.3)
x = -22.0
while x < 95: box('sleeper', (0.24, 2.4, 0.14), (x, -3.2, 0.19), color='timber_dark', bevel=0.02, jitter=0.012); x += 0.7

# ---------- platform ----------
box('platform', (46, 4.6, PZ), (12, 0.8, 0), color='concrete', bevel=0.03)
box('platform_base', (46.06, 0.06, 0.55), (12, -1.52, 0), color='concrete_dark', bevel=0.01)
box('coping', (46.1, 0.55, 0.07), (12, -1.27, PZ - 0.02), color='cream', bevel=0.02)
box('tactile', (46, 0.3, 0.02), (12, -0.75, PZ), color='yellow', bevel=0.005)
for i in range(3): box('step', (0.45, 2.2, PZ * (3 - i) / 4), (-11.2 - i * 0.45, 0.2, 0), color='concrete_dark', bevel=0.02)

# ---------- station building ----------
X0, X1, Y0, Y1, H = 5.0, 17.0, 3.1, 8.1, 3.1
CX, L = (X0 + X1) / 2, X1 - X0
box('walls', (L, Y1 - Y0, H), (CX, (Y0 + Y1) / 2, PZ), color='plaster', bevel=0.02)
x = X0
while x < X1 - 0.05:
    if not 9.9 < x + 0.15 < 12.1: box('plank', (0.28, 0.05, 1.1), (x + 0.15, Y0 - 0.02, PZ), color='timber', bevel=0.012, jitter=0.01)
    x += 0.3
for x in (5.05, 7, 9, 9.95, 12.05, 13, 15, 16.95): box('post', (0.16, 0.1, H), (x, Y0 - 0.05, PZ), color='timber_dark', bevel=0.02)
box('beam_top', (L + 0.2, 0.12, 0.22), (CX, Y0 - 0.05, PZ + 2.88), color='timber_dark', bevel=0.02)
box('rail_mid', (L + 0.1, 0.1, 0.1), (CX, Y0 - 0.05, PZ + 1.1), color='timber_dark', bevel=0.02)
def lattice(name, x0, x1, z0, z1, nx, nz):
    box(name + '_glow', (x1 - x0, 0.04, z1 - z0), ((x0 + x1) / 2, Y0 - 0.03, PZ + z0), color='window', bevel=0, emit=1.0)
    for i in range(nx + 1): box(name + '_v', (0.035, 0.05, z1 - z0), (x0 + (x1 - x0) * i / nx, Y0 - 0.06, PZ + z0), color='timber_dark', bevel=0.008)
    for i in range(nz + 1): box(name + '_h', (x1 - x0, 0.05, 0.035), ((x0 + x1) / 2, Y0 - 0.06, PZ + z0 + (z1 - z0) * i / nz), color='timber_dark', bevel=0.008)
lattice('door', 10.05, 11.95, 0.0, 2.15, 8, 3)
lattice('win_l', 5.5, 8.6, 1.25, 2.45, 10, 2)
lattice('win_r', 13.4, 16.5, 1.25, 2.45, 10, 2)
for i, (px, c, w, h) in enumerate(((9.25, 0xD9532F, 0.5, 0.7), (12.55, 0x3F8FD1, 0.45, 0.62), (9.3, 0xF2E6B8, 0.42, 0.3))):
    box('poster', (w, 0.02, h), (px, Y0 - 0.06, PZ + (1.35 if i < 2 else 2.2)), (0, random.uniform(-2, 2), 0), c, bevel=0.004)
# gable roof
P, EAVE = 28, 0.75
slope = (2.5 + EAVE) / math.cos(math.radians(P)); EZ = PZ + H - EAVE * math.tan(math.radians(P)) + 0.05; RZ = EZ + (2.5 + EAVE) * math.tan(math.radians(P))
shingles('roof_front', L + 1.6, slope, 8, (CX, Y0 - EAVE, EZ), P, tile=0.45)
shingles('roof_back', L + 1.6, slope, 8, (CX, Y1 + EAVE, EZ), P, yaw=180, tile=0.45)
for sy, yc in ((1, Y0 - EAVE + slope / 2 * math.cos(math.radians(P))), (-1, Y1 + EAVE - slope / 2 * math.cos(math.radians(P)))):
    box('roof_deck', (L + 1.5, slope, 0.05), (CX, yc, (EZ + RZ) / 2 - 0.09), (sy * P, 0, 0), color='timber_dark', bevel=0.01)
box('ridge', (L + 1.8, 0.24, 0.16), (CX, 5.6, RZ - 0.02), color='roof_dark', bevel=0.04)
for gx in (X0 - 0.02, X1 + 0.02):
    gable('gable', 5.0, 2.5 * math.tan(math.radians(P)) + 0.1, 0.12, (gx, 5.6, PZ + H), color='plaster')
    for sy in (-1, 1): box('barge', (0.1, slope + 0.1, 0.16), (gx * 1.0 + (0.72 if gx > CX else -0.72), 5.6 + sy * (2.5 + EAVE) / 2, (EZ + RZ) / 2 - 0.06), (-sy * P, 0, 0), color='timber_dark', bevel=0.02)
    box('gable_vent', (0.14, 0.5, 0.5), (gx + (0.02 if gx > CX else -0.02), 5.6, PZ + H + 0.5), color='timber_dark', bevel=0.02)
box('chimney', (0.5, 0.5, 1.2), (14.5, 6.6, RZ - 0.9), color='stone', bevel=0.04, jitter=0.02); box('chimney_cap', (0.62, 0.62, 0.1), (14.5, 6.6, RZ + 0.3), color='concrete_dark', bevel=0.02)

# ---------- platform canopy ----------
CA0, CA1, CP = 1.0, 23.0, 4.5
CL, CC = CA1 - CA0, (CA0 + CA1) / 2
shingles('canopy', CL, 4.25, 5, (CC, -1.1, PZ + 2.5), CP, color='canopy', dark='canopy_dark', tile=0.55)
box('canopy_deck', (CL - 0.1, 4.2, 0.05), (CC, 1.0, PZ + 2.6), (CP, 0, 0), color='timber_dark', bevel=0.01)
box('fascia', (CL + 0.2, 0.06, 0.24), (CC, -1.14, PZ + 2.32), color='canopy_dark', bevel=0.015)
box('canopy_beam', (CL, 0.14, 0.18), (CC, -0.45, PZ + 2.36), color='timber_dark', bevel=0.02)
x = CA0 + 0.5
while x < CA1:
    box('cpost', (0.16, 0.16, 2.38), (x, -0.45, PZ), color='timber_dark', bevel=0.025, taper=0.9)
    box('cpost_foot', (0.3, 0.3, 0.16), (x, -0.45, PZ), color='stone', bevel=0.03)
    for s in (-1, 1): box('bracket', (0.07, 0.07, 0.85), (x + s * 0.62, -0.45, PZ + 1.75), (0, -s * 45, 0), color='timber_dark', bevel=0.015)
    box('cross', (0.1, 3.6, 0.14), (x, 1.3, PZ + 2.5), (CP, 0, 0), color='timber_dark', bevel=0.02)
    if x < X0 or x > X1: box('cpost_back', (0.14, 0.14, 2.6), (x, 2.95, PZ), color='timber_dark', bevel=0.02)
    x += 3.5
LAMPS = []
for x in (3.0, 8.3, 13.7, 19.2):
    tube('cord', [(x, 0.6, PZ + 2.55), (x, 0.6, PZ + 2.2)], 0.008, 'pole')
    cyl('shade', 0.2, 0.05, 0.12, (x, 0.6, PZ + 2.1), color='canopy_dark', bevel=0.01)
    ball('bulb', 0.07, (x, 0.6, PZ + 2.07), color='lamp', emit=4.0); LAMPS.append(((x, 0.6, PZ + 1.95), 260, (1, 0.72, 0.42)))
# under the canopy: bench, vending machine, bin, clock
for z, y in ((0.45, 2.75), (0.45, 2.55), (0.45, 2.35), (0.8, 2.92), (1.0, 2.94)): box('bench_slat', (2.2, 0.16 if z < 0.5 else 0.03, 0.04 if z < 0.5 else 0.14), (14.9, y, PZ + z), color='wood', bevel=0.012, jitter=0.006)
for x in (13.95, 15.85): box('bench_leg', (0.07, 0.6, 0.45), (x, 2.6, PZ), color='pole', bevel=0.015)
box('vending', (0.95, 0.6, 1.85), (8.95, 2.72, PZ), color='vend', bevel=0.04); box('vending_front', (0.8, 0.02, 0.95), (8.95, 2.41, PZ + 0.78), color='vend_glow', bevel=0, emit=2.0)
for i in range(8): cyl('can', 0.035, 0.035, 0.11, (8.64 + (i % 4) * 0.205, 2.39, PZ + 1.2 + (i // 4) * 0.25), color=(0xD9532F, 0x3F8FD1, 0xF2C230, 0x5FA46B)[i % 4], bevel=0.005, verts=10)
box('vending_slot', (0.8, 0.02, 0.22), (8.95, 2.41, PZ + 0.3), color='pole', bevel=0.004)
cyl('bin', 0.2, 0.24, 0.6, (12.7, 2.7, PZ), color='canopy_dark', bevel=0.02)
cyl('clock', 0.24, 0.24, 0.07, (4.5, -0.55, PZ + 1.95), (90, 0, 0), color='cream', bevel=0.02); cyl('clock_rim', 0.27, 0.27, 0.05, (4.5, -0.53, PZ + 1.95), (90, 0, 0), color='pole', bevel=0.01)

# ---------- the chair, the suitcase, the sign ----------
c = chair.build(); c.location = (-2.6, -0.2, PZ); c.rotation_euler = (0, 0, 0.15)
s = suitcase.build(); s.location = (-1.75, -0.25, PZ); s.rotation_euler = (0, 0, -0.3)
g = station_sign.build(); g.location = (-6.2, 1.9, PZ); g.scale = (0.8, 0.8, 0.8)

# ---------- fences, planters, platform lamps ----------
def fence(xa, xb, y):
    x = xa
    while x <= xb + 0.01: box('fpost', (0.1, 0.1, 1.05), (x, y, PZ), color='cream', bevel=0.02, jitter=0.01, taper=0.9); x += 1.5
    for z in (0.45, 0.85): box('frail', (xb - xa, 0.05, 0.09), ((xa + xb) / 2, y, PZ + z), color='cream', bevel=0.015)
fence(-10.5, 0.4, 3.0); fence(23.6, 34.6, 3.0)
def bush(x, y, z, r, n=6):
    for i in range(n * 2): ball('bush', r * random.uniform(0.35, 0.6), (x + random.uniform(-r, r), y + random.uniform(-r, r) * 0.6, z + r * random.uniform(0.3, 0.8)), (1, 1, 0.8), random.choice(('tree_mid', 'tree_light', 'tree_light')), rough=1)
for x in (-9, -6.3, -3.4, 25, 28, 31):
    box('planter', (1.5, 0.55, 0.42), (x, 2.55, PZ), color='timber', bevel=0.03, jitter=0.015); bush(x, 2.55, PZ + 0.35, 0.36)
for x in (-8.2, 27.5):
    cyl('lamp_post', 0.07, 0.05, 4.2, (x, 2.4, PZ), color='pole', bevel=0.01)
    tube('lamp_arm', [(x, 2.4, PZ + 4.1), (x, 2.1, PZ + 4.45), (x, 1.5, PZ + 4.5), (x, 1.2, PZ + 4.35)], 0.03, 'pole')
    cyl('lamp_head', 0.2, 0.08, 0.14, (x, 1.2, PZ + 4.2), color='pole', bevel=0.01); ball('lamp_bulb', 0.1, (x, 1.2, PZ + 4.17), color='lamp', emit=5.0)
    LAMPS.append(((x, 1.2, PZ + 4.0), 500, (1, 0.75, 0.45)))

# ---------- utility poles and wires ----------
POLES = [-7.0, 11.0, 29.0, 47.0, 65.0, 83.0]
for i, x in enumerate(POLES):
    cyl('upole', 0.14, 0.1, 9.2, (x, -5.9, 0), (0, random.uniform(-1, 1), 0), color='pole', bevel=0.01)
    for z, w in ((8.5, 2.3), (7.7, 1.8)):
        box('crossarm', (0.1, w, 0.1), (x, -5.9, z), color='pole', bevel=0.015)
        for k in (-1, 0, 1): cyl('insulator', 0.045, 0.03, 0.14, (x, -5.9 + k * w * 0.42, z + 0.1), color='cream', bevel=0.008, verts=10)
    if i in (1, 3): cyl('transformer', 0.28, 0.28, 0.75, (x, -5.5, 6.2), color='concrete_dark', bevel=0.04)
    if i in (0, 2):
        tube('street_arm', [(x, -5.9, 6.4), (x, -5.3, 6.9), (x, -4.6, 6.85)], 0.03, 'pole'); ball('street_bulb', 0.11, (x, -4.6, 6.75), (1.4, 1, 0.6), 'lamp', emit=5.0)
        LAMPS.append(((x, -4.6, 6.5), 700, (1, 0.8, 0.55)))
for a, b in zip(POLES, POLES[1:]):
    for z, w in ((8.66, 2.3), (7.86, 1.8)):
        for k in (-1, 0, 1):
            y = -5.9 + k * w * 0.42; sag = random.uniform(0.35, 0.6)
            tube('wire', [(a, y, z), ((a + b) / 2, y, z - sag), (b, y, z)], 0.012, 'pole')
tube('service_wire', [(11, -5.9, 7.2), (11.5, -1, 5.6), (12, 3.2, PZ + 3.2)], 0.012, 'pole')
tube('service_wire', [(-7, -5.9, 7.2), (-7.6, -1.5, 5.9), (-8.2, 2.4, PZ + 4.2)], 0.012, 'pole')

# ---------- trees, hills ----------
def tree(x, y, h, r, n=40):
    cyl('trunk', r * 0.16, r * 0.1, h, (x, y, 0), (random.uniform(-4, 4), random.uniform(-4, 4), 0), color='timber_dark', bevel=0.02, verts=12)
    for i in range(n):
        a, up = random.uniform(0, 6.28), random.uniform(-0.3, 1); d = random.uniform(0.2, 1) * r * (1 - max(0, up) * 0.55)
        ball('leaf', r * random.uniform(0.24, 0.42), (x + math.cos(a) * d, y + math.sin(a) * d, h + up * r * 0.75), (1, 1, 0.82),
             'tree_light' if up > 0.55 else 'tree_mid' if up > 0.1 else 'tree', rough=1)
for x, y, h, r in ((0, 12, 6, 4), (7, 13.5, 8, 5), (15, 12.5, 7, 4.4), (22, 11, 5.5, 3.6), (-7, 10.5, 6.5, 4), (29, 10, 7, 4.2), (37, 9, 6, 3.8), (-15, 12, 7, 4.5),
                   (3, -11.5, 6.5, 4), (19, -12, 8, 5), (36, -10.5, 6.5, 4), (-9, -12.5, 7, 4.5), (52, -11, 7, 4.5), (50, 9, 7, 4.5), (64, 10, 8, 5), (70, -12, 8, 5)):
    tree(x, y, h, r)
for x, y, r in ((6, -7.4, 0.7), (16, -7.6, 0.9), (24, -7.2, 0.6), (-3, -7.6, 0.8), (33, -7.5, 0.8), (20, 9.2, 0.9), (2, 8.6, 0.8)): bush(x, y, 0, r, 7)
for x, y, r, z in ((170, 90, 80, 0.2), (210, -70, 95, 0.22), (120, 160, 70, 0.18), (130, -150, 70, 0.16)): ball('hill', r, (x, y, -2), (1, 1, z), 'hill', rough=1)

for i in range(260):
    x, side = random.uniform(-16, 60), random.choice((-1, 1)); y = -5.3 - random.uniform(0, 3.5) if side < 0 else random.uniform(3.6, 7) if (x < 4.5 or x > 17.5) else 9
    for k in range(3): box('blade', (0.07, 0.03, random.uniform(0.25, 0.6)), (x + random.uniform(-0.12, 0.12), y + random.uniform(-0.12, 0.12), 0), (random.uniform(-18, 18), random.uniform(-18, 18), 0), random.choice(('tree_mid', 'tree_light')), bevel=0, taper=0.2)
    if i % 6 == 0: ball('flower', 0.06, (x + 0.2, y, 0.3), color=random.choice((0xFFFFFF, 0xFFE27A, 0xFFB7C9)))

# ---------- the train, far down the line ----------
TX = 58.0
box('train_low', (15, 2.7, 1.25), (TX + 7.5, -3.2, 0.5), color='train_red', bevel=0.12)
box('train_high', (15, 2.7, 1.5), (TX + 7.5, -3.2, 1.75), color='train_cream', bevel=0.12)
box('train_roof', (15.1, 2.5, 0.25), (TX + 7.5, -3.2, 3.2), color='concrete_dark', bevel=0.1)
box('train_window', (0.04, 1.9, 0.85), (TX - 0.01, -3.2, 2.05), color='window', bevel=0, emit=1.5)
for i in range(6): box('train_side_win', (1.5, 0.04, 0.8), (TX + 1.6 + i * 2.3, -3.2 - 1.36, 2.05), color='window', bevel=0, emit=1.5)
for dy in (-0.85, 0.85): ball('headlight', 0.17, (TX - 0.03, -3.2 + dy, 1.15), color='lamp', emit=30.0)
LAMPS.append(((TX - 1.5, -3.2, 1.3), 2500, (1, 0.9, 0.7)))

# ---------- clouds ----------
def cloud(cx, cy, cz, size, n=22):
    for i in range(n):
        dx = random.uniform(-1, 1); r = size * random.uniform(0.45, 0.9) * (1 - abs(dx) * 0.45)
        ball('cloud', r, (cx + random.uniform(-0.5, 0.5) * size, cy + dx * size * 2.2, cz + r * 0.55 + random.uniform(0, size * 0.9) * (1 - abs(dx))), (1, 1, 0.8), 'cloud', rough=1)
for cx, cy, cz, sz in ((230, 40, 30, 30), (260, -70, 45, 36), (300, 130, 60, 44), (210, -160, 28, 26), (330, -10, 95, 40), (190, 190, 40, 30), (150, 230, 70, 34), (280, 250, 110, 44), (240, -260, 70, 40)):
    cloud(cx, cy, cz, sz)

# ---------- camera, sky, light: two moods ----------
sc = bpy.context.scene
cam = bpy.data.cameras.new('cam'); cam.lens = 25; cam.clip_end = 2000
co = bpy.data.objects.new('camera', cam); sc.collection.objects.link(co); sc.camera = co
co.location = (-13.2, -4.6, 1.85); co.rotation_euler = (Vector((11, 1.2, 3.6)) - co.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new('sky'); sc.world = w; w.use_nodes = True; nt = w.node_tree
bg = nt.nodes['Background']; tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); ramp = nt.nodes.new('ShaderNodeValToRGB')
mth = nt.nodes.new('ShaderNodeMath'); mth.operation = 'MULTIPLY_ADD'; mth.inputs[1].default_value = 0.5; mth.inputs[2].default_value = 0.5
nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs[2], mth.inputs[0]); nt.links.new(mth.outputs[0], ramp.inputs[0]); nt.links.new(ramp.outputs[0], bg.inputs[0])
els = ramp.color_ramp.elements; els.new(0.62)
sun = bpy.data.lights.new('sun', 'SUN'); so = bpy.data.objects.new('sun', sun); sc.collection.objects.link(so)
lights = []
for loc, power, col in LAMPS:
    l = bpy.data.lights.new('lamp', 'POINT'); l.color = col; l.shadow_soft_size = 0.2; o = bpy.data.objects.new('lamp', l); o.location = loc; sc.collection.objects.link(o); lights.append((l, power))
emis = [(m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'], m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value) for m in bpy.data.materials if m.node_tree]

MOODS = {
    'day': dict(sky=((0.80, 0.93, 1.0), (0.30, 0.62, 1.0), (0.05, 0.25, 0.85)), sky_power=1.15, sun_dir=(0.35, 0.62, -0.7), sun=(1.0, 0.97, 0.9), sun_power=5.0, lamps=0.0, emit=0.5),
    'dusk': dict(sky=((1.0, 0.55, 0.3), (0.2, 0.36, 0.72), (0.03, 0.07, 0.3)), sky_power=0.55, sun_dir=(-0.9, 0.42, -0.16), sun=(1.0, 0.5, 0.28), sun_power=3.2, lamps=1.0, emit=5.0),
}
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = int(os.environ.get('SAMPLES', 110)); sc.cycles.use_denoising = True
sc.view_settings.view_transform = 'Standard'
for lk in ('Medium High Contrast', 'High Contrast'):
    try: sc.view_settings.look = lk; break
    except Exception: pass
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
for name in (sys.argv[1:] or MOODS):
    m = MOODS[name]
    els[0].position = 0.5; els[1].position = 0.62; els[2].position = 1.0
    for e, c in zip(els, m['sky']): e.color = (*c, 1)
    bg.inputs[1].default_value = m['sky_power']
    sun.energy = m['sun_power']; sun.color = m['sun']; sun.angle = math.radians(3)
    so.rotation_euler = Vector(m['sun_dir']).normalized().to_track_quat('-Z', 'Y').to_euler()
    for l, p in lights: l.energy = p * m['lamps']
    for inp, base in emis: inp.default_value = base * m['emit']
    sc.render.filepath = '%s/concepts/terminal-%s.png' % (here, name)
    bpy.ops.render.render(write_still=True); print('RENDERED', name)
bpy.ops.wm.save_as_mainfile(filepath=here + '/files/terminal_concept.blend')
