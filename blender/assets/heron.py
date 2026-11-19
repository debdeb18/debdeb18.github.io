"""A grey heron standing on one spot, neck folded back. The wings are their own parts ('heron_wing_l', '_r') so the
website can open them when it flies off. Origin at its feet."""
from lib import *
VIEW = dict(angle=35, lift=0.3, res=(900, 900), samples=32)
def build():
    r = root('heron')
    grey, dgrey, white, black, beak, leg = 0x9AA6B2, 0x6E7884, 0xF2F0EA, 0x2B2D33, 0xE8B34A, 0xC9A35A
    for sy in (-1, 1):
        cyl('leg', 0.012, 0.012, 0.5, (0.02, sy * 0.05, 0), color=leg, parent=r, bevel=0, verts=6)
        for a in (-30, 0, 30): box('toe', (0.12, 0.012, 0.01), (0.04, sy * 0.05, 0), (0, 0, a), leg, r, bevel=0)
    ball('body', 0.16, (0, 0, 0.62), (1.6, 0.85, 0.85), grey, r)
    for sy, nm in ((-1, 'heron_wing_l'), (1, 'heron_wing_r')):
        w = root(nm); w.location = (0.06, sy * 0.075, 0.67); w.parent = r
        ball('wing', 0.14, (0.02, 0, -0.01), (1.75, 0.2, 0.62), dgrey, w)
        ball('primaries', 0.07, (0.22, 0, -0.04), (1.7, 0.18, 0.4), black, w)
    ball('tail', 0.06, (0.26, 0, 0.6), (1.5, 0.8, 0.5), dgrey, r)
    tube('neck', [(-0.18, 0, 0.7), (-0.2, 0, 0.82), (-0.12, 0, 0.9), (-0.17, 0, 1.0)], [0.055, 0.048, 0.045, 0.045], white, r)
    ball('head', 0.06, (-0.19, 0, 1.03), (1.2, 0.85, 0.85), white, r)
    box('crest', (0.12, 0.02, 0.016), (-0.14, 0, 1.06), (0, -15, 0), black, r, bevel=0.004)
    cyl('beak', 0.022, 0.003, 0.17, (-0.25, 0, 1.02), (0, -95, 0), beak, r, bevel=0, verts=8)
    for sy in (-1, 1): ball('eye', 0.009, (-0.23, sy * 0.045, 1.045), (1, 1, 1), 0xF2C94A, r)
    for k in range(3): ball('chest_streak', 0.02, (-0.2, 0, 0.84 - k * 0.05), (0.6, 0.8, 1.4), black, r)
    return r
