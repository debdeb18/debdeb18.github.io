"""A small catfish for the water by the back stairs: a broad flat head with whiskers, a long soft body, blue-grey back
and a paler belly, rounded fins. It swims just under the surface. Origin at its middle; it faces -X."""
from lib import *
VIEW = dict(angle=30, lift=0.6, res=(700, 500), samples=24)
def build():
    r = root('fish')
    back, belly, fin = 0x55677E, 0xA9B4C2, 0x6E7F96
    ball('head', 0.07, (-0.14, 0, 0.0), (1.2, 1.15, 0.65), back, r)
    ball('body', 0.065, (0.02, 0, 0.0), (2.4, 0.85, 0.75), back, r)
    ball('belly', 0.06, (-0.02, 0, -0.018), (2.5, 0.8, 0.55), belly, r)
    ball('tail_root', 0.04, (0.2, 0, 0.0), (1.6, 0.6, 0.8), back, r)
    for sz in (-1, 1): ball('tail', 0.04, (0.28, 0, sz * 0.02), (1.3, 0.2, 0.7), fin, r)
    ball('back_fin', 0.035, (-0.02, 0, 0.05), (1.4, 0.18, 0.7), fin, r)
    for sy in (-1, 1):
        ball('pec_fin', 0.035, (-0.08, sy * 0.07, -0.02), (1.2, 0.8, 0.18), fin, r)
        ball('eye', 0.012, (-0.18, sy * 0.06, 0.018), (1, 1, 1), 0xF0EEE6, r)
        ball('pupil', 0.007, (-0.188, sy * 0.068, 0.018), (1, 1, 1), 0x1E2228, r)
        tube('whisker', [(-0.22, sy * 0.04, -0.005), (-0.27, sy * 0.09, -0.015), (-0.31, sy * 0.17, -0.035)], 0.007, 0x3E4B5C, r)
        tube('whisker_s', [(-0.22, sy * 0.02, -0.02), (-0.27, sy * 0.06, -0.05)], 0.005, 0x3E4B5C, r)
    for k in range(4): ball('spot', 0.012, (-0.05 + k * 0.05, (k % 2 - 0.5) * 0.04, 0.045), (1.2, 1, 0.3), 0x8FA2BC, r)
    return r
