"""The heron in flight: the same low-poly bird as heron.py, its neck tucked back into an S the way herons fly, legs
trailing straight out behind, and broad wings spread wide. Each wing is its own part hinged at the shoulder
('heron_wing_l', '_r') so the website can flap it. The world swaps the standing heron for this one when it takes
off. Origin at its middle; it flies towards -X."""
import math
from mathutils import Vector
from lib import *
from assets.heron import loft, blade, BODY, PALE, WING, TIP, BLACK, BEAK, LEG
VIEW = dict(angle=-30, lift=0.9, res=(900, 700), samples=32)

def build():
    r = root('heron_flying')
    loft('body', [(-0.2, 0, 0.0), (-0.14, 0, 0.0), (-0.03, 0, 0.0), (0.09, 0, 0.0), (0.2, 0, 0.0), (0.3, 0, 0.0)],
         [0.05, 0.09, 0.105, 0.1, 0.07, 0.02], BODY, r, sides=8, squash=(0.85, 1.0))
    neck = [(-0.16, 0, 0.02), (-0.22, 0, 0.06), (-0.2, 0, 0.11), (-0.25, 0, 0.13), (-0.31, 0, 0.12)]   # tucked back in an S
    loft('neck', neck, [0.06, 0.045, 0.04, 0.036, 0.034], PALE, r, sides=7)
    loft('head', [(-0.3, 0, 0.12), (-0.34, 0, 0.12), (-0.37, 0, 0.115)], [0.03, 0.04, 0.02], PALE, r, sides=7)
    loft('beak', [(-0.365, 0, 0.115), (-0.44, 0, 0.11), (-0.53, 0, 0.1)], [0.018, 0.011, 0.002], BEAK, r, sides=5, squash=(1.0, 0.7))
    blade('crest', [(-0.34, -0.003, 0.15), (-0.24, -0.003, 0.16), (-0.235, -0.003, 0.152), (-0.33, -0.003, 0.138)], BLACK, r)
    for sy in (-1, 1):
        blade('eye_stripe', [(-0.36, sy * 0.032, 0.13), (-0.28, sy * 0.028, 0.14), (-0.28, sy * 0.028, 0.128), (-0.36, sy * 0.032, 0.118)], BLACK, r, t=0.002 * sy)
        loft('leg', [(0.2, sy * 0.03, -0.04), (0.45, sy * 0.03, -0.06), (0.62, sy * 0.03, -0.07)], [0.01, 0.009, 0.008], LEG, r, sides=5)   # trailing
        for a in (-20, 0, 20):
            d = Vector((math.cos(math.radians(a)), math.sin(math.radians(a)) * 0.5, -0.1)).normalized()
            loft('toe', [(0.62, sy * 0.03, -0.07), tuple(Vector((0.62, sy * 0.03, -0.07)) + d * 0.08)], [0.005, 0.003], LEG, r, sides=4)
    for sy, nm in ((-1, 'heron_wing_l'), (1, 'heron_wing_r')):               # broad wings, spread
        w = root(nm); w.location = (-0.06, sy * 0.07, 0.03); w.parent = r
        span = [(0.0, 0), (0.05, 0.3), (0.06, 0.55), (0.12, 0.72), (0.24, 0.62), (0.26, 0.3), (0.22, 0.0)]   # (back, out)
        blade('wing', [(x, sy * o, 0) for (x, o) in span[:3]] + [(0.13, sy * 0.66, 0)] + [(x, sy * o, 0) for (x, o) in span[4:]], WING, w, t=0.012, up=True)
        for k in range(5):                                                     # dark flight feathers fanned at the tip
            o0 = 0.42 + k * 0.06
            blade('primary', [(0.05 + k * 0.025, sy * o0, 0.013), (0.06 + k * 0.03, sy * (o0 + 0.22 - k * 0.03), 0.013), (0.11 + k * 0.03, sy * (o0 + 0.2 - k * 0.03), 0.013), (0.12 + k * 0.025, sy * o0, 0.013)], TIP, w, t=0.004, up=True)
        for k in range(4):                                                     # dark trailing edge
            blade('secondary', [(0.2, sy * (0.05 + k * 0.1), 0.013), (0.27, sy * (0.07 + k * 0.1), 0.013), (0.27, sy * (0.15 + k * 0.1), 0.013), (0.2, sy * (0.14 + k * 0.1), 0.013)], 0x8D96A2, w, t=0.004, up=True)
    for k in range(3):
        blade('tail', [(0.27, (k - 1) * 0.03, 0.0), (0.38, (k - 1) * 0.045, 0.0), (0.37, (k - 1) * 0.045 + 0.02, 0.0), (0.27, (k - 1) * 0.03 + 0.012, 0.0)], 0xA9B1BB, r, up=True)
    return r
