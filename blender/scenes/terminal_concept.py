"""Concept scene for the terminal: a small country station in an anime-background mood, rendered by day and at dusk.
    python blender/scenes/terminal_concept.py   -> blender/concepts/terminal-day.png, terminal-dusk.png, blender/files/terminal_concept.blend"""
import sys, os, math, random
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, here)
import bpy
from mathutils import Vector
import lib
from lib import box, cyl, ball, tube, shingles, mat, gable, lump, root
from assets import chair, suitcase, station_sign, train, tree as tree_asset

random.seed(11)
lib.reset()
lib.set_style(jitter=1.3, lean=1.0, pal=dict(
    wood=0x9A6A45, wood_dark=0x4E3528, wood_pale=0xC9A374, roof=0x41626F, roof_dark=0x2F4B58, cream=0xF1E6CC, stone=0xB9B2A8,
    timber=0x8A5A3C, timber_dark=0x4A3226, plaster=0xF0E4C8, concrete=0xD2CBBC, concrete_dark=0xA39C8F, gravel=0x8F877D, rail=0x7E7A82,
    grass=0x7DB85A, sand=0xE6D6A8, tree=0x256B45, tree_mid=0x3C8C4C, tree_light=0x7CBC58, tree_hi=0xC2E272, trunk=0x5A3F30, boat=0x4F8FA0, pole=0x54483F, yellow=0xF2C230, canopy=0x5E8F7A, canopy_dark=0x45725F,
    lamp=0xFFD28A, window=0xFFC777, vend=0xE8F0F4, vend_glow=0xBFE6FF, train_red=0xB8403A, train_cream=0xF0E2C0, cloud=0xFFFFFF, hill=0x4F7F86))
PZ = 0.95                                   # platform height

# ---------- the sea, and the railway causeway across it ----------
sea = box('sea', (900, 900, 0.1), (150, 0, -0.1), color=0x1F6F86, bevel=0)
wm = sea.data.materials[0]; nt = wm.node_tree; b = nt.nodes['Principled BSDF']; b.inputs['Roughness'].default_value = 0.07; b.inputs['Alpha'].default_value = 0.68      # see-through, so the sunken rails show
tco = nt.nodes.new('ShaderNodeTexCoord'); nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.9; nz.inputs['Detail'].default_value = 3
bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.12
nt.links.new(tco.outputs['Object'], nz.inputs['Vector']); nt.links.new(nz.outputs[0], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
box('seabed', (900, 900, 0.1), (150, 0, -2.5), color=0x2F8FA0, bevel=0)
box('causeway', (190, 3.0, 0.3), (55, -3.2, -0.52), color='gravel', bevel=0.1)
for dy in (-0.72, 0.72): box('rail', (190, 0.07, 0.14), (55, -3.2 + dy, -0.19), color='rail', bevel=0.012, rough=0.3)
x = -22.0
while x < 110: box('sleeper', (0.24, 2.4, 0.14), (x, -3.2, -0.3), color='timber_dark', bevel=0.02, jitter=0.012); x += 0.7
x = -20.0
while x < 110:
    for sy in (-1, 1): cyl('pile', 0.11, 0.1, 0.9, (x, -3.2 + sy * 1.62, -0.6), (random.uniform(-3, 3), 0, 0), color='timber_dark', bevel=0.01, verts=10)
    x += 3.0

# ---------- platform ----------
box('platform', (46, 4.6, PZ), (12, 0.8, 0), color='concrete', bevel=0.03)
box('deck', (34, 7.4, 0.3), (12, 6.7, PZ - 0.3), color='timber', bevel=0.03)                      # timber deck on stilts, behind the platform
for i in range(22): box('deck_plank', (34, 0.3, 0.03), (12, 3.25 + i * 0.335, PZ - 0.02), color='wood' if i % 3 else 'wood_pale', bevel=0.008, jitter=0.006)
for sx in range(-5, 30, 3):
    for sy in (3.6, 6.7, 10.1): cyl('stilt', 0.13, 0.12, 1.6, (sx, sy, -0.9), (random.uniform(-2, 2), random.uniform(-2, 2), 0), color='timber_dark', bevel=0.01, verts=10)
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
for x in (-9, -6.3, -3.4, 25, 28, 31):
    box('planter', (1.5, 0.55, 0.42), (x, 2.55, PZ), color='timber', bevel=0.03, jitter=0.015)
    for i in range(5): lump('shrub', random.uniform(0.2, 0.32), (x + random.uniform(-0.5, 0.5), 2.55 + random.uniform(-0.08, 0.08), PZ + random.uniform(0.45, 0.62)), (1, 1, 0.85), random.choice(('tree_mid', 'tree_light')), rough=1)
for x in (-8.2, 27.5):
    cyl('lamp_post', 0.07, 0.05, 4.2, (x, 2.4, PZ), color='pole', bevel=0.01)
    tube('lamp_arm', [(x, 2.4, PZ + 4.1), (x, 2.1, PZ + 4.45), (x, 1.5, PZ + 4.5), (x, 1.2, PZ + 4.35)], 0.03, 'pole')
    cyl('lamp_head', 0.2, 0.08, 0.14, (x, 1.2, PZ + 4.2), color='pole', bevel=0.01); ball('lamp_bulb', 0.1, (x, 1.2, PZ + 4.17), color='lamp', emit=5.0)
    LAMPS.append(((x, 1.2, PZ + 4.0), 500, (1, 0.75, 0.45)))

# ---------- utility poles and wires ----------
POLES = [-7.0, 11.0, 29.0, 47.0, 65.0, 83.0]
for i, x in enumerate(POLES):
    cyl('upole', 0.14, 0.1, 9.2, (x, -5.9, 0), (0, random.uniform(-1, 1), 0), color='pole', bevel=0.01)
    cyl('pole_footing', 0.35, 0.3, 0.5, (x, -5.9, -0.2), color='concrete_dark', bevel=0.04, verts=12)
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

# ---------- islets with leafy trees, far islands ----------
def islet(x, y, r):
    ball('islet_sand', r, (x, y, -0.05), (1, 1, 0.16), 'sand', rough=1)
    ball('islet_grass', r * 0.86, (x, y, 0.08), (1, 1, 0.2), 'grass', rough=1)
    for i in range(int(r * 7)):
        a, d = random.uniform(0, 6.283), random.uniform(0.1, 0.7) * r; gx, gy = x + math.cos(a) * d, y + math.sin(a) * d; gz = 0.08 + r * 0.86 * 0.2 * math.sqrt(max(0, 1 - (d / (r * 0.86)) ** 2)) - 0.05
        for k in range(3): box('blade', (0.08, 0.03, random.uniform(0.3, 0.7)), (gx + random.uniform(-0.15, 0.15), gy + random.uniform(-0.15, 0.15), gz), (random.uniform(-18, 18), random.uniform(-18, 18), 0), random.choice(('tree_mid', 'tree_light')), bevel=0, taper=0.2)
        if i % 5 == 0: ball('flower', 0.07, (gx + 0.2, gy, gz + 0.32), color=random.choice((0xFFFFFF, 0xFFE27A, 0xFFB7C9)))
    for i in range(int(r)): lump('rock', random.uniform(0.25, 0.5), (x + math.cos(i * 2.4) * r * 0.8, y + math.sin(i * 2.4) * r * 0.8, 0.1), (1.2, 1, 0.7), 'stone', strength=0.2, grain=1.2)
def bush(x, y, z, r, n=5):
    for i in range(n): lump('bush', r * random.uniform(0.5, 0.8), (x + random.uniform(-r, r), y + random.uniform(-r, r) * 0.6, z + r * random.uniform(0.2, 0.6)), (1, 1, 0.8), random.choice(('tree_mid', 'tree_light', 'tree')), rough=1)
for i, (x, y, h, r) in enumerate(((0, 14, 6, 4), (8, 15.5, 8, 5), (16, 14.5, 7, 4.4), (24, 14, 5.5, 3.6), (-8, 13.5, 6.5, 4), (32, 13, 7, 4.2), (41, 12, 6, 3.8), (-17, 14, 7, 4.5),
                   (4, -12.5, 6.5, 4), (21, -13.5, 8, 5), (38, -12, 6.5, 4), (-10, -14, 7, 4.5), (56, -12.5, 7, 4.5), (54, 13, 7, 4.5), (70, 13, 8, 5), (76, -14, 8, 5))):
    islet(x, y, r * 0.95)
    t = tree_asset.build(h, r, seed=i, kind='pine' if i in (3, 10, 13) else 'broad'); t.location = (x, y, 0.3)
    bush(x + r * 0.5, y - r * 0.45, 0.4, 0.55)
for x, y, r, z in ((190, 100, 80, 0.2), (230, -80, 95, 0.22), (140, 190, 70, 0.18), (150, -180, 70, 0.16)):
    ball('island', r, (x, y, -2), (1, 1, z), 'hill', rough=1)
    for k in range(4): box('far_house', (5, 5, 4), (x - r * 0.5 + k * 9, y + (k % 2) * 8 - r * 0.2, r * z * 0.75), color='cream', bevel=0.2); box('far_roof', (6, 6, 1.6), (x - r * 0.5 + k * 9, y + (k % 2) * 8 - r * 0.2, r * z * 0.75 + 4), color='roof', bevel=0.3, taper=0.3)

# ---------- the train, coming down the line ----------
tr = train.build(2); tr.location = (38, -3.2, -0.05); tr.rotation_euler = (0, 0, math.radians(-90))
LAMPS.append(((36.5, -3.2, 1.4), 700, (1, 0.9, 0.7)))
for i in range(60):                       # the bow wave and wake the train pushes through the shallow water
    k = random.uniform(0, 1); sy = random.choice((-1, 1))
    lump('spray', random.uniform(0.1, 0.32) * (1 - k * 0.6), (37.6 + k * 16 + random.uniform(-0.3, 0.3), -3.2 + sy * (1.45 + k * 1.3 + random.uniform(0, 0.3)), random.uniform(0.0, 0.5) * (1 - k)), (1.3, 1, 0.7), 0xFFFFFF, strength=0.25, rough=1)

# ---------- small details ----------
# hanging name board and platform number under the canopy
box('nameboard', (2.6, 0.06, 0.5), (16.5, -0.2, PZ + 1.72), color='cream', bevel=0.02); box('nameboard_stripe', (2.6, 0.065, 0.07), (16.5, -0.2, PZ + 1.74), color='red', bevel=0.005)
for dx in (-1.1, 1.1): tube('nameboard_chain', [(16.5 + dx, -0.2, PZ + 2.2), (16.5 + dx, -0.2, PZ + 2.36)], 0.008, 'pole')
box('platform_no', (0.5, 0.05, 0.5), (6.6, -0.5, PZ + 1.85), color=0x2F6F9A, bevel=0.03)
# timetable board, mailbox, umbrella stand, potted plants, crates, broom
box('timetable', (1.3, 0.05, 0.95), (7.9, Y0 - 0.1, PZ + 1.3), color='wood_dark', bevel=0.02); box('timetable_paper', (1.14, 0.02, 0.8), (7.9, Y0 - 0.13, PZ + 1.375), color='cream', bevel=0.004)
for i in range(5): box('timetable_line', (0.95, 0.01, 0.03), (7.9, Y0 - 0.145, PZ + 1.5 + i * 0.12), color='pole', bevel=0)
box('mailbox', (0.42, 0.34, 0.55), (12.75, 2.85, PZ + 0.75), color='red', bevel=0.06); cyl('mailbox_post', 0.04, 0.04, 0.75, (12.75, 2.85, PZ), color='pole', bevel=0.005); box('mail_slot', (0.26, 0.02, 0.04), (12.75, 2.67, PZ + 1.12), color='pole', bevel=0)
cyl('umbrella_stand', 0.16, 0.2, 0.5, (9.75, 2.8, PZ), color='canopy_dark', bevel=0.02)
for i, c in enumerate((0xD9532F, 0x3F8FD1, 0xF2C230)): cyl('umbrella', 0.035, 0.02, 0.85, (9.7 + i * 0.06, 2.8 + (i - 1) * 0.05, PZ + 0.1), (random.uniform(-9, 9), random.uniform(-9, 9), 0), c, bevel=0.005, verts=8)
for x, y, sz in ((5.5, 2.65, 1.0), (6.2, 2.75, 0.7), (16.6, 2.7, 0.9), (1.6, -0.1, 0.8), (22.4, -0.1, 0.8), (17.4, 2.75, 0.6)):
    cyl('pot', 0.2 * sz, 0.26 * sz, 0.34 * sz, (x, y, PZ), color=random.choice((0xC97B5A, 0x6F8FB0, 0xD9B48A)), bevel=0.02)
    for i in range(4): lump('pot_leaf', 0.17 * sz, (x + random.uniform(-0.1, 0.1) * sz, y + random.uniform(-0.1, 0.1) * sz, PZ + 0.38 * sz + i * 0.07 * sz), (1, 1, 0.9), random.choice(('tree_mid', 'tree_light')), rough=1)
    if sz > 0.75:
        for i in range(3): ball('pot_flower', 0.05 * sz, (x + random.uniform(-0.2, 0.2) * sz, y - 0.1 * sz, PZ + 0.62 * sz), color=random.choice((0xFFB7C9, 0xFFE27A, 0xFFFFFF)))
for i, (x, y, w) in enumerate(((19.2, 2.6, 0.7), (19.95, 2.7, 0.6), (19.5, 2.62, 0.55))): box('crate', (w, w * 0.8, w * 0.7), (x, y, PZ + (0.5 if i == 2 else 0)), (0, 0, random.uniform(-8, 8)), color='wood_pale' if i % 2 else 'wood', bevel=0.02, jitter=0.01)
box('broom_stick', (0.03, 0.03, 1.4), (4.75, 2.9, PZ), (-8, 0, 0), color='wood_pale', bevel=0.005); box('broom_head', (0.3, 0.08, 0.24), (4.75, 2.85, PZ), color=0xD9B46A, bevel=0.02, taper=1.4)
# a cat asleep on the bench
cat = root('cat'); cat.location = (14.35, 2.55, PZ + 0.49)
ball('cat_body', 0.2, (0, 0, 0.11), (1.5, 0.95, 0.72), 0xE8A05A, cat); ball('cat_head', 0.12, (-0.27, -0.05, 0.14), (1, 1, 0.9), 0xE8A05A, cat)
for sy in (-1, 1): cyl('cat_ear', 0.045, 0.004, 0.08, (-0.29, -0.05 + sy * 0.07, 0.22), color=0xE8A05A, parent=cat, bevel=0, verts=6)
tube('cat_tail', [(0.27, 0.02, 0.1), (0.36, -0.12, 0.06), (0.22, -0.22, 0.05), (0.02, -0.21, 0.05)], [0.035, 0.032, 0.028, 0.022], 0xD98C45, cat)
# lanterns strung under the canopy edge
for i in range(9):
    x = 2.2 + i * 2.5
    tube('lantern_string', [(x, -1.05, PZ + 2.24), (x, -1.05, PZ + 2.1)], 0.005, 'pole'); cyl('paper_lantern', 0.1, 0.1, 0.2, (x, -1.05, PZ + 1.9), color=(0xFF8A5A, 0xFFD27A, 0xFF9AB4)[i % 3], bevel=0.04, emit=1.2, verts=12)
# roof: a weather vane and a little moss
cyl('vane_post', 0.02, 0.02, 0.8, (7.5, 5.6, RZ + 0.05), color='pole', bevel=0); box('vane_arrow', (0.7, 0.03, 0.1), (7.5, 5.6, RZ + 0.75), (0, 0, 25), color='pole', bevel=0.01, taper=0.4)
for i in range(7): lump('moss', random.uniform(0.12, 0.22), (random.uniform(6, 16), Y0 - EAVE + 0.5 + random.uniform(0, 1.2), EZ + 0.35 + random.uniform(0, 0.5)), (1.4, 1, 0.35), 'tree_light', strength=0.2, rough=1)
# on the water: a rowing boat, buoys with lights, lily pads, mooring posts
bt = root('boat'); bt.location = (12.5, -8.6, 0.0); bt.rotation_euler = (0, 0, 0.35)
box('hull', (3.2, 1.25, 0.5), (0, 0, -0.12), color='boat', parent=bt, bevel=0.2, segs=4, taper=1.25); box('hull_inside', (2.7, 0.95, 0.06), (0, 0, 0.34), color='wood_dark', parent=bt, bevel=0.02)
for dx in (-0.6, 0.5): box('thwart', (0.22, 1.3, 0.05), (dx, 0, 0.36), color='wood_pale', parent=bt, bevel=0.015)
box('oar', (2.3, 0.05, 0.04), (0.2, 0.3, 0.42), (0, 0, 14), color='wood_pale', parent=bt, bevel=0.01); cyl('boat_lamp', 0.07, 0.08, 0.16, (1.35, 0, 0.42), color='lamp', parent=bt, bevel=0.01, emit=4.0)
cyl('mooring', 0.1, 0.09, 1.5, (14.8, -7.6, -0.5), (4, 3, 0), color='timber_dark', bevel=0.01, verts=10); tube('rope', [(14.8, -7.6, 0.75), (14.4, -7.9, 0.25), (13.95, -8.1, 0.42)], 0.015, 'wood_pale')
for x, y, c in ((-4, -9.5, 0xD9532F), (19, -6.6, 0xF2C230), (30, -7.6, 0xD9532F), (48, -8.2, 0xF2C230), (-9, -6.6, 0xF2C230)):
    cyl('buoy', 0.28, 0.2, 0.42, (x, y, -0.1), color=c, bevel=0.06, verts=14); cyl('buoy_mast', 0.02, 0.02, 0.5, (x, y, 0.3), color='pole', bevel=0); ball('buoy_light', 0.07, (x, y, 0.82), color='lamp', emit=4.0)
    LAMPS.append(((x, y, 0.95), 30, (1, 0.8, 0.5)))
for i in range(46):
    x, y = random.uniform(-12, 34), random.uniform(-11.5, -5.2)
    rl = random.uniform(0.16, 0.34); cyl('lily', rl, rl, 0.014, (x, y, 0.004), (0, 0, random.uniform(0, 360)), color=random.choice(('tree_mid', 'tree_light')), bevel=0, verts=10)
    if i % 6 == 0: ball('lily_flower', 0.07, (x, y, 0.06), (1, 1, 0.7), 0xFFD6E4)
# gulls
for x, y, z in ((60, 14, 16), (66, 18, 17.5), (72, 12, 15), (90, -30, 22), (97, -26, 23.5), (55, 40, 26)):
    for s in (-1, 1): box('gull_wing', (0.12, 0.9, 0.04), (x, y + s * 0.42, z), (s * 22, 0, 0), color=0xFFFFFF, bevel=0.01)

# ---------- clouds ----------
def cloud(cx, cy, cz, size, n=22):
    for i in range(n):
        dx = random.uniform(-1, 1); r = size * random.uniform(0.45, 0.9) * (1 - abs(dx) * 0.45)
        lump('cloud', r, (cx + random.uniform(-0.5, 0.5) * size, cy + dx * size * 2.2, cz + r * 0.55 + random.uniform(0, size * 0.9) * (1 - abs(dx))), (1, 1, 0.8), 'cloud', strength=0.16, grain=0.9, rough=1)
for cx, cy, cz, sz in ((230, 40, 30, 30), (260, -70, 45, 36), (300, 130, 60, 44), (210, -160, 28, 26), (330, -10, 95, 40), (190, 190, 40, 30), (150, 230, 70, 34), (280, 250, 110, 44), (240, -260, 70, 40)):
    cloud(cx, cy, cz, sz)

# ---------- camera, sky, light: two moods ----------
sc = bpy.context.scene
cam = bpy.data.cameras.new('cam'); cam.lens = 25; cam.clip_end = 2000
co = bpy.data.objects.new('camera', cam); sc.collection.objects.link(co); sc.camera = co
co.location = (-13.2, -5.0, 2.2); co.rotation_euler = (Vector((11, 1.2, 3.6)) - co.location).to_track_quat('-Z', 'Y').to_euler()
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
