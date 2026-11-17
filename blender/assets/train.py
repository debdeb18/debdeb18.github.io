"""The train: a rounded two-car country railcar, red below and cream above. Front faces -Y, wheels sit at z = 0."""
from lib import *
VIEW = dict(angle=38, lift=0.25, res=(1200, 800))
W, LEN = 2.7, 12.0

def car(r, y0, front):
    yc = y0 + LEN / 2
    box('underframe', (2.2, LEN - 0.6, 0.3), (0, yc, 0.5), color='iron', parent=r, bevel=0.04)
    for by in (y0 + 2.3, y0 + LEN - 2.3):
        box('bogie', (1.9, 2.3, 0.34), (0, by, 0.22), color='iron', parent=r, bevel=0.06)
        for sx in (-1, 1):
            box('bogie_frame', (0.1, 2.5, 0.2), (sx * 0.98, by, 0.3), color='iron', parent=r, bevel=0.04)
            for dy in (-0.7, 0.7):
                cyl('wheel', 0.42, 0.42, 0.12, (sx * 0.72 - 0.06, by + dy, 0.42), (0, 90, 0), 'iron', r, bevel=0.02, verts=24, rough=0.4)
                cyl('hub', 0.14, 0.12, 0.05, (sx * 0.9 - 0.025, by + dy, 0.42), (0, 90, 0), 'train_roof', r, bevel=0.01)
    box('skirt_tank', (1.6, 2.6, 0.4), (0, yc, 0.28), color='iron', parent=r, bevel=0.08)
    box('body_low', (W, LEN, 1.3), (0, yc, 0.72), color='train_red', parent=r, bevel=0.2, segs=5)
    box('body_high', (W - 0.04, LEN - 0.04, 1.5), (0, yc, 1.92), color='train_cream', parent=r, bevel=0.24, segs=5)
    box('belt', (W + 0.03, LEN + 0.03, 0.07), (0, yc, 1.93), color='brass', parent=r, bevel=0.02, rough=0.4)
    box('sill', (W + 0.03, LEN + 0.03, 0.06), (0, yc, 0.86), color='train_red_dark', parent=r, bevel=0.02)
    box('roof', (W - 0.3, LEN - 0.25, 0.34), (0, yc, 3.3), color='train_roof', parent=r, bevel=0.16, segs=5)
    for i in range(4):
        vy = y0 + 2 + i * 2.7
        box('vent', (0.7, 0.9, 0.16), (0, vy, 3.62), color='train_roof', parent=r, bevel=0.06); box('vent_cap', (0.86, 1.06, 0.05), (0, vy, 3.78), color='iron', parent=r, bevel=0.02)
    # sides: doors at both ends, a row of windows between
    for sx in (-1, 1):
        x = sx * (W / 2)
        for dy in (y0 + 1.25, y0 + LEN - 1.25):
            box('door', (0.05, 0.95, 2.05), (x, dy, 0.95), color='train_red_dark', parent=r, bevel=0.02)
            box('door_window', (0.04, 0.55, 0.75), (x + sx * 0.012, dy, 2.1), color='window', parent=r, bevel=0.01, emit=1.5)
            box('door_step', (0.16, 0.9, 0.05), (x + sx * 0.05, dy, 0.82), color='iron', parent=r, bevel=0.015)
            tube('handrail', [(x + sx * 0.05, dy - 0.56, 1.3), (x + sx * 0.08, dy - 0.56, 1.7), (x + sx * 0.05, dy - 0.56, 2.1)], 0.015, 'brass', r, rough=0.4)
        for i in range(6):
            wy = y0 + 2.55 + i * 1.38
            box('win_frame', (0.05, 1.2, 0.98), (x - sx * 0.005, wy, 2.12), color='wood_dark', parent=r, bevel=0.03)
            box('win_glass', (0.05, 1.04, 0.82), (x + sx * 0.012, wy, 2.2), color='window', parent=r, bevel=0.02, emit=1.5)
            box('win_bar', (0.06, 1.06, 0.03), (x + sx * 0.02, wy, 2.6), color='wood_dark', parent=r, bevel=0.008)
    # ends
    for ey, s in ((y0, -1), (y0 + LEN, 1)):
        cab = (s == -1) == front or True
        for sx in (-0.58, 0.58):
            box('screen_frame', (1.08, 0.05, 1.0), (sx, ey + s * 0.0, 2.1), color='wood_dark', parent=r, bevel=0.04)
            box('screen', (0.94, 0.05, 0.84), (sx, ey + s * 0.02, 2.18), color='window', parent=r, bevel=0.03, emit=1.5)
        box('board', (1.5, 0.06, 0.28), (0, ey + s * 0.03, 3.1), color='lamp', parent=r, bevel=0.03, emit=2.0)
        box('board_frame', (1.62, 0.05, 0.4), (0, ey + s * 0.005, 3.04), color='iron', parent=r, bevel=0.04)
        for sx in (-0.85, 0.85):
            cyl('lamp_housing', 0.2, 0.17, 0.12, (sx, ey + s * -0.02, 1.2), (-s * 90, 0, 0), 'train_roof', r, bevel=0.02, rough=0.4)
            ball('headlight', 0.14, (sx, ey + s * 0.1, 1.2), (1, 0.5, 1), 'lamp', r, emit=4.0 if s == -1 and front else 0.6)
            ball('marker', 0.06, (sx * 1.25, ey + s * 0.06, 0.95), (1, 0.5, 1), 'red', r, emit=1.0)
        box('bumper', (2.5, 0.22, 0.24), (0, ey + s * 0.1, 0.52), color='iron', parent=r, bevel=0.07)
        box('coupler', (0.3, 0.5, 0.2), (0, ey + s * 0.35, 0.45), color='iron', parent=r, bevel=0.05)
        cyl('roof_lamp', 0.13, 0.1, 0.14, (0, ey + s * -0.5, 3.6), color='train_roof', parent=r, bevel=0.02); ball('roof_bulb', 0.08, (0, ey + s * -0.38, 3.68), color='lamp', parent=r, emit=3.0 if s == -1 and front else 0.3)
        for sx in (-0.58, 0.58): box('wiper', (0.02, 0.02, 0.45), (sx + 0.1, ey + s * 0.06, 2.2), (0, 25, 0), 'iron', r, bevel=0)

def build(cars=2):
    r = root('train')
    for i in range(cars):
        car(r, i * (LEN + 0.7), i == 0)
        if i: box('gangway', (1.5, 0.8, 2.3), (0, i * (LEN + 0.7) - 0.35, 0.85), color='iron', parent=r, bevel=0.1)
    return r
