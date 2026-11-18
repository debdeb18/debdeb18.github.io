"""The waiting chair, after the chair beside the poster: a warm wooden chair with turned legs, a curved top rail on
spindles, a bentwood arm-like back, and a thick mustard cushion on the seat."""
import math
from lib import *
VIEW = dict(angle=32)

def build():
    PAL.update(chair_wood=0x8A5634, chair_dark=0x5E3820, cushion_m=0xC9A15A, cushion_d=0xA88143)
    r = root('chair')
    # four turned legs, splayed a little, with stretchers
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl('leg', 0.022, 0.03, 0.46, (sx * 0.21, sy * 0.2, 0), (sy * 4, -sx * 4, 0), 'chair_wood', r, bevel=0.006, verts=12)
            ball('leg_turn', 0.034, (sx * 0.215, sy * 0.205, 0.3), (1, 1, 0.6), 'chair_dark', r)
        tube('stretcher', [(sx * 0.22, -0.2, 0.16), (sx * 0.22, 0.2, 0.16)], 0.014, 'chair_dark', r)
    tube('stretcher', [(-0.22, -0.21, 0.22), (0.22, -0.21, 0.22)], 0.014, 'chair_dark', r)
    # the seat: a thick slab with rounded edges
    box('seat', (0.5, 0.48, 0.05), (0, 0, 0.45), color='chair_wood', parent=r, bevel=0.02)
    # the back: two curving back posts, a wide curved top rail, five spindles
    for sx in (-1, 1):
        tube('back_post', [(sx * 0.2, 0.2, 0.48), (sx * 0.21, 0.24, 0.75), (sx * 0.22, 0.29, 1.0)], [0.02, 0.019, 0.017], 'chair_wood', r)
    rail = [(math.sin(t) * 0.26, 0.27 + (1 - math.cos(t)) * -0.06, 1.0 + math.cos(t) * 0.03) for t in [(-1 + k / 6) * 0.95 for k in range(13)]]
    tube('top_rail', rail, 0.032, 'chair_wood', r)
    tube('mid_rail', [(x, 0.235 - (abs(x) * 0.12), 0.62) for x in (-0.2, -0.1, 0, 0.1, 0.2)], 0.014, 'chair_dark', r)
    for k in range(5):
        x = -0.14 + k * 0.07
        tube('spindle', [(x, 0.215, 0.48), (x * 1.04, 0.25, 0.75), (x * 1.08, 0.28 - abs(x) * 0.1, 0.99)], [0.011, 0.013, 0.01], 'chair_wood', r)
    # a thick mustard cushion, slightly puffed, with a piped edge
    ball('cushion', 0.25, (0, -0.01, 0.53), (1.0, 0.95, 0.18), 'cushion_m', r)
    tube('piping', [(math.cos(a) * 0.245, -0.01 + math.sin(a) * 0.235, 0.52) for a in [k * math.pi / 12 for k in range(25)]], 0.012, 'cushion_d', r)
    return r
