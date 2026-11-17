"""The waiting chair: a slightly crooked wooden chair with a red cushion."""
from lib import *
VIEW = dict(angle=32)

def build():
    r = root('chair')
    # legs splay outward a little; the back legs run up into the backrest
    for sx in (-1, 1):
        box('leg_front', (0.065, 0.065, 0.46), (sx * 0.2, -0.19, 0), (-4, sx * 4, 0), 'wood_dark', r, bevel=0.018, jitter=0.006, taper=1.25)
        box('leg_back', (0.065, 0.065, 1.02), (sx * 0.2, 0.2, 0), (-7, sx * 3, 0), 'wood_dark', r, bevel=0.018, jitter=0.006, taper=0.8)
        box('stretcher_side', (0.035, 0.4, 0.035), (sx * 0.2, 0.0, 0.17), (0, 0, 0), 'wood_dark', r, bevel=0.012)
    box('stretcher_front', (0.4, 0.035, 0.035), (0, -0.2, 0.24), color='wood_dark', parent=r, bevel=0.012)
    # seat: three planks with small gaps, none quite straight
    for i, x in enumerate((-0.165, 0.0, 0.165)):
        box('seat_plank', (0.155, 0.5, 0.045), (x, 0.0, 0.445), (0, 0, (i - 1) * 1.5), 'wood', r, bevel=0.016, jitter=0.008)
    box('apron', (0.44, 0.44, 0.05), (0, 0.0, 0.4), color='wood_dark', parent=r, bevel=0.012)
    # backrest: curved top rail and three slats
    box('top_rail', (0.56, 0.05, 0.11), (0, 0.305, 0.9), (-7, 0, 2), 'wood', r, bevel=0.03, jitter=0.008)
    for x in (-0.11, 0.0, 0.11):
        box('slat', (0.06, 0.025, 0.42), (x, 0.265, 0.5), (-7, 0, 0), 'wood_pale', r, bevel=0.01, jitter=0.004)
    # cushion, tied on
    c = ball('cushion', 0.25, (0, -0.01, 0.52), (0.9, 0.9, 0.2), 'red', r)
    for sx in (-1, 1): tube('tie', [(sx * 0.19, 0.2, 0.5), (sx * 0.23, 0.26, 0.46), (sx * 0.2, 0.29, 0.4)], [0.008, 0.008, 0.006], 'red_dark', r)
    return r
