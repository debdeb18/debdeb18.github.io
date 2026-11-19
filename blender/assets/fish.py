"""A small silver fish for the shallows by the back stairs: dark back, pale belly, a forked tail. Origin at its middle."""
from lib import *
VIEW = dict(angle=30, lift=0.6, res=(700, 500), samples=24)
def build():
    r = root('fish')
    ball('body', 0.06, (0, 0, 0), (2.3, 0.62, 0.8), 0xC9D3D6, r)
    ball('back', 0.052, (-0.005, 0, 0.022), (2.3, 0.62, 0.55), 0x50707E, r)         # the dark back shows over the pale belly
    for sz in (-1, 1): cyl('tail', 0.035, 0.004, 0.08, (0.12, 0, sz * 0.012), (0, 90 + sz * 35, 0), 0x6E8592, r, bevel=0, verts=6)   # a forked tail
    cyl('fin', 0.02, 0.002, 0.04, (0.0, 0, 0.055), (0, -30, 0), 0x6E8592, r, bevel=0, verts=5)
    for sy in (-1, 1): ball('eye', 0.009, (-0.11, sy * 0.035, 0.012), (1, 1, 1), 0x1E2228, r)
    return r
