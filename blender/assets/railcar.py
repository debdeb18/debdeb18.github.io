"""A vintage single-car electric railcar: rounded nose with a three-pane windshield, one round headlight up on the roof
dome, pantograph, maroon lower body and cream upper body, wood-framed windows, and a warm interior with benches.
Front faces -Y, the car runs along +Y, wheels sit at z = 0 (on top of the rails)."""
import math
from lib import *

VIEW = dict(angle=35, lift=0.22, res=(1300, 820))
L, W = 13.6, 2.7                      # body length (behind the nose centre) and width
ZF, ZB, ZR = 0.95, 2.05, 3.3          # floor line, belt line (maroon below / cream above), roof line
WZ0, WZ1 = 2.25, 3.0                  # side windows: bottom and top
NOSE = 1.25                           # y of the nose curve's centre
CAR_COLOURS = dict(maroon=0x7A2431, maroon_dark=0x5A1A26, cream_car=0xEFE3C4, roof_car=0x4D5655, roof_dark=0x3A4140,
                   brass=0xD9A441, glass_warm=0xFFD995, seat=0xB73A3A, wood_car=0x8A5A3A, iron=0x2E2D33)

def bogie(r, y):
    box('bogie', (2.0, 2.4, 0.34), (0, y, 0.22), color='iron', parent=r, bevel=0.06)
    for sx in (-1, 1):
        box('bogie_frame', (0.1, 2.7, 0.24), (sx * 1.02, y, 0.3), color='iron', parent=r, bevel=0.04)
        for dy in (-0.75, 0.75):
            cyl('wheel', 0.43, 0.43, 0.12, (sx * 0.72 - 0.06, y + dy, 0.43), (0, 90, 0), 'iron', r, bevel=0.02, verts=26, rough=0.4)
            cyl('hub', 0.14, 0.12, 0.05, (sx * 0.9 - 0.025, y + dy, 0.43), (0, 90, 0), 'brass', r, bevel=0.01, rough=0.4)
        box('spring', (0.12, 0.5, 0.18), (sx * 1.04, y, 0.55), color='iron', parent=r, bevel=0.04)

def window(r, x, y, sx, w=0.95):
    """A wood-framed side window, open so the lit cabin shows through, with a small transom pane above it."""
    h = WZ1 - WZ0
    for zz in (WZ0 - 0.03, WZ1 - 0.03): box('win_frame_h', (0.09, w + 0.1, 0.06), (x, y, zz), color='wood_car', parent=r, bevel=0.015)
    for dy in (-w / 2, w / 2): box('win_frame_v', (0.09, 0.06, h), (x, y + dy, WZ0), color='wood_car', parent=r, bevel=0.015)
    box('win_bar', (0.07, w, 0.04), (x, y, WZ0 + h * 0.5), color='wood_car', parent=r, bevel=0.01)
    box('transom', (0.09, w - 0.1, 0.16), (x, y, WZ1 + 0.06), color='glass_warm', parent=r, bevel=0.01, emit=0.6)

def build():
    PAL.update(CAR_COLOURS)                                                  # added here, after any style has been set
    r = root('railcar')
    # ---------------- running gear ----------------
    box('underframe', (2.3, L - 0.4, 0.3), (0, NOSE + L / 2 - 0.2, 0.55), color='iron', parent=r, bevel=0.04)
    for y in (NOSE + 2.3, NOSE + L - 2.6): bogie(r, y)
    for y, w in ((NOSE + 5.2, 1.6), (NOSE + 7.6, 1.2), (NOSE + 9.4, 0.9)):
        box('equipment', (1.7, w, 0.45), (0, y, 0.3), color=0x3A3A40, parent=r, bevel=0.06)
    # ---------------- body ----------------
    yc = NOSE + L / 2
    for sx in (-1, 1):                                                       # lower body: two side panels (hollow, so there is a cabin)
        box('body_low', (0.12, L, ZB - ZF), (sx * (W / 2 - 0.06), yc, ZF), color='maroon', parent=r, bevel=0.05, segs=3)
    box('body_low_end', (W - 0.1, 0.12, ZB - ZF), (0, NOSE + L - 0.06, ZF), color='maroon', parent=r, bevel=0.04)
    # upper body is hollow: a sill below the windows, a header above them, pillars between (so you can see inside)
    for sx in (-1, 1):
        x = sx * (W / 2 - 0.05)
        box('sill', (0.1, L, WZ0 - ZB), (x, yc, ZB), color='cream_car', parent=r, bevel=0.03)
        box('header', (0.1, L, ZR - WZ1), (x, yc, WZ1), color='cream_car', parent=r, bevel=0.03)
        for py in [NOSE + 0.35 + k * 0.01 for k in range(1)] + [NOSE + 1.58 + i * 1.32 for i in range(8)] + [NOSE + L - 0.55]:
            box('pillar', (0.1, 0.42 if NOSE + 1 < py < NOSE + L - 1 else 0.7, WZ1 - WZ0), (x, py, WZ0), color='cream_car', parent=r, bevel=0.02)
    box('end_wall', (W - 0.1, 0.1, ZR - ZB), (0, NOSE + L - 0.05, ZB), color='cream_car', parent=r, bevel=0.04)
    box('skirt', (W + 0.02, L - 0.2, 0.18), (0, yc, ZF - 0.05), color='maroon_dark', parent=r, bevel=0.06)
    for sx in (-1, 1): box('belt', (0.05, L + 0.02, 0.08), (sx * (W / 2 + 0.005), yc, ZB - 0.04), color='brass', parent=r, bevel=0.015, rough=0.4)
    box('belt_rear', (W, 0.05, 0.08), (0, NOSE + L + 0.01, ZB - 0.04), color='brass', parent=r, bevel=0.015, rough=0.4)
    box('gutter', (W + 0.08, L + 0.05, 0.05), (0, yc, ZR - 0.03), color='roof_dark', parent=r, bevel=0.02)
    # the rounded nose: the same two colours wrapped round a half-ellipse
    cyl('nose_low', W / 2, W / 2, ZB - ZF, (0, NOSE, ZF), color='maroon', parent=r, verts=40, bevel=0.06).scale = (1, 0.55, 1)
    cyl('nose_high', W / 2 - 0.01, W / 2 - 0.01, ZR - ZB, (0, NOSE, ZB), color='cream_car', parent=r, verts=40, bevel=0.06).scale = (1, 0.55, 1)
    cyl('nose_belt', W / 2 + 0.025, W / 2 + 0.025, 0.08, (0, NOSE, ZB - 0.04), color='brass', parent=r, verts=40, bevel=0.01, rough=0.4).scale = (1, 0.56, 1)
    cyl('nose_skirt', W / 2 + 0.01, W / 2 + 0.01, 0.2, (0, NOSE, ZF - 0.05), color='maroon_dark', parent=r, verts=40, bevel=0.04).scale = (1, 0.56, 1)
    # three-pane curved windshield, wood frames, a little sun visor
    a_, b_ = W / 2, W / 2 * 0.55
    for th, wd in ((-50, 0.62), (0, 0.86), (50, 0.62)):                     # each pane sits flush on the curve
        t = math.radians(th); px, py = a_ * math.sin(t), -b_ * math.cos(t)
        nx, ny = math.sin(t) / a_, -math.cos(t) / b_; nl = math.hypot(nx, ny); nx, ny = nx / nl, ny / nl
        phi = math.degrees(math.atan2(nx, -ny))
        box('screen_frame', (wd + 0.12, 0.05, 0.94), (px + nx * 0.02, NOSE + py + ny * 0.02, WZ0 - 0.05), (0, 0, phi), 'wood_car', r, bevel=0.025)
        box('screen', (wd, 0.06, 0.78), (px + nx * 0.035, NOSE + py + ny * 0.035, WZ0 + 0.03), (0, 0, phi), 0x3A2E2A, r, bevel=0.02, rough=0.15)
        if th == 0: box('wiper', (0.03, 0.03, 0.5), (px - 0.15, NOSE + py - 0.07, WZ0 + 0.1), (0, 18, 0), 'iron', r, bevel=0)
    # ---------------- roof ----------------
    roof = cyl('roof', W / 2 + 0.05, W / 2 + 0.05, L, (0, NOSE, ZR - 0.05), (-90, 0, 0), 'roof_car', r, verts=36, bevel=0.03)
    roof.scale = (1, 0.24, 1)
    ball('roof_dome', W / 2 + 0.05, (0, NOSE, ZR - 0.05), (1, 0.6, 0.24), 'roof_car', r)
    box('clerestory', (1.0, L - 3.2, 0.3), (0, yc + 0.6, ZR + 0.22), color='roof_dark', parent=r, bevel=0.08)
    for i in range(9):
        box('clere_window', (1.04, 0.5, 0.12), (0, NOSE + 2.4 + i * 1.18, ZR + 0.3), color=0xD9CFB2, parent=r, bevel=0.02)
    for i in range(4):
        vy = NOSE + 2.6 + i * 3.0
        for sx in (-1, 1): box('vent', (0.34, 0.6, 0.22), (sx * 0.85, vy, ZR + 0.2), color='roof_dark', parent=r, bevel=0.06)
    # the single round headlight on the roof dome, and the destination board under it
    cyl('lamp_body', 0.24, 0.21, 0.32, (0, NOSE - 0.5, ZR + 0.32), (90, 0, 0), 'iron', r, bevel=0.03, verts=24, rough=0.4)
    cyl('lamp_rim', 0.22, 0.22, 0.05, (0, NOSE - 0.82, ZR + 0.32), (90, 0, 0), 'brass', r, bevel=0.01, verts=24, rough=0.3)
    ball('headlight', 0.18, (0, NOSE - 0.86, ZR + 0.32), (1, 0.4, 1), 'glass_warm', r, emit=6.0)
    box('lamp_stand', (0.16, 0.3, 0.2), (0, NOSE - 0.5, ZR + 0.08), color='iron', parent=r, bevel=0.03)
    box('dest_board', (0.95, 0.06, 0.2), (0, NOSE - 0.72, ZR - 0.06), color='glass_warm', parent=r, bevel=0.02, emit=2.0)
    box('dest_frame', (1.05, 0.05, 0.28), (0, NOSE - 0.70, ZR - 0.1), color='iron', parent=r, bevel=0.03)
    for sx in (-1, 1):                                                       # small marker lamps and a horn
        ball('marker', 0.08, (sx * 0.95, NOSE - 0.58, ZF + 0.6), (1, 0.6, 1), 0xFF6A4A, r, emit=1.5)
    cyl('horn', 0.06, 0.12, 0.35, (0.7, NOSE + 0.6, ZR + 0.25), (90, 0, 0), 'brass', r, bevel=0.01, rough=0.3)
    # ---------------- pantograph ----------------
    py = NOSE + L * 0.55
    for sx in (-1, 1):
        for sy in (-1, 1): cyl('panto_insulator', 0.06, 0.05, 0.22, (sx * 0.45, py + sy * 0.6, ZR + 0.35), color=0xD9D2C4, parent=r, bevel=0.01, verts=12)
    box('panto_base', (1.1, 1.5, 0.08), (0, py, ZR + 0.57), color='iron', parent=r, bevel=0.02)
    for sy in (-1, 1):
        tube('panto_arm', [(-0.4, py + sy * 0.55, ZR + 0.65), (0, py + sy * 0.15, ZR + 1.35), (0.4, py + sy * 0.55, ZR + 0.65)], 0.025, 'iron', r)
        tube('panto_arm', [(-0.25, py, ZR + 1.35), (0, py + sy * 0.15, ZR + 1.35)], 0.02, 'iron', r)
    box('panto_shoe', (1.5, 0.12, 0.05), (0, py, ZR + 1.38), color='iron', parent=r, bevel=0.02)
    for sx in (-1, 1): tube('panto_horn', [(sx * 0.75, py, ZR + 1.4), (sx * 0.95, py, ZR + 1.3)], 0.02, 'iron', r)
    # ---------------- sides: windows and doors ----------------
    for sx in (-1, 1):
        x = sx * (W / 2 + 0.005)
        for dy in (NOSE + 1.0, NOSE + L - 1.4):                              # doors with a window and a brass handrail
            box('door', (0.06, 1.05, 2.15), (x, dy, ZF + 0.02), color='maroon_dark', parent=r, bevel=0.03)
            box('door_window', (0.08, 0.6, 0.72), (x, dy, WZ0), color=0x3A2E2A, parent=r, bevel=0.02, rough=0.15)
            box('step', (0.25, 1.0, 0.06), (x + sx * 0.1, dy, ZF - 0.12), color='iron', parent=r, bevel=0.015)
            tube('handrail', [(x + sx * 0.07, dy - 0.62, 1.3), (x + sx * 0.1, dy - 0.62, 1.75), (x + sx * 0.07, dy - 0.62, 2.25)], 0.018, 'brass', r, rough=0.3)
        for i in range(7): window(r, x, NOSE + 2.25 + i * 1.32, sx, 0.9)
        for i in range(30): ball('rivet', 0.022, (x + sx * 0.02, NOSE + 0.9 + i * 0.42, ZF + 0.12), color='maroon_dark', parent=r)
    # ---------------- rear end ----------------
    ye = NOSE + L
    for sx in (-0.62, 0.62):
        box('rear_frame', (0.92, 0.06, 0.95), (sx, ye + 0.01, ZB + 0.18), color='wood_car', parent=r, bevel=0.03)
        box('rear_window', (0.78, 0.08, 0.8), (sx, ye + 0.02, ZB + 0.25), color=0x2A1E1A, parent=r, bevel=0.02)
        ball('tail_light', 0.09, (sx * 1.45, ye + 0.05, ZF + 0.55), (1, 0.6, 1), 0xFF4A3A, r, emit=2.0)
    box('bumper', (2.4, 0.22, 0.24), (0, ye + 0.1, 0.55), color='iron', parent=r, bevel=0.07)
    box('coupler', (0.3, 0.5, 0.2), (0, ye + 0.35, 0.48), color='iron', parent=r, bevel=0.05)
    box('front_bumper', (1.8, 0.2, 0.22), (0, NOSE - 0.75, 0.55), color='iron', parent=r, bevel=0.07)
    # ---------------- inside: what you see through the windows ----------------
    box('floor', (W - 0.2, L - 0.4, 0.05), (0, yc, ZF + 0.02), color='wood_car', parent=r, bevel=0)
    box('inner_wall', (W - 0.3, L - 0.6, 0.02), (0, yc, ZR - 0.15), color='cream_car', parent=r, bevel=0)
    for sx in (-1, 1):
        box('bench', (0.5, L - 3.6, 0.42), (sx * 0.95, yc, ZF + 0.05), color='wood_car', parent=r, bevel=0.03)
        box('cushion', (0.46, L - 3.7, 0.1), (sx * 0.95, yc, ZF + 0.47), color='seat', parent=r, bevel=0.04)
        box('backrest', (0.1, L - 3.7, 0.55), (sx * 1.17, yc, ZF + 0.55), color='seat', parent=r, bevel=0.04)
        tube('strap_rail', [(sx * 0.55, NOSE + 2, ZR - 0.25), (sx * 0.55, NOSE + L - 2, ZR - 0.25)], 0.02, 'brass', r)
        for i in range(10):
            sy = NOSE + 2.4 + i * 1.0
            tube('strap', [(sx * 0.55, sy, ZR - 0.25), (sx * 0.55, sy, ZR - 0.55)], 0.012, 0xE8DCC0, r)
            cyl('strap_ring', 0.07, 0.07, 0.02, (sx * 0.55, sy, ZR - 0.62), (90, 0, 0), 0xE8DCC0, r, bevel=0.005, verts=12)
    for i in range(4): cyl('ceiling_lamp', 0.16, 0.1, 0.1, (0, NOSE + 3 + i * 2.6, ZR - 0.27), color='glass_warm', parent=r, bevel=0.02, emit=3.0, verts=16)
    return r
