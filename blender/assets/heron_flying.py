"""The heron in flight: the same low-poly bird as heron.py, its neck tucked back into an S the way herons fly, legs
trailing straight out behind, and broad wings spread wide. Each wing is its own part hinged at the shoulder
('heron_wing_l', '_r') so the website can flap it. The world swaps the standing heron for this one when it takes
off. Origin at its middle; it flies towards -X."""
import math
from mathutils import Vector
from lib import *
from assets.heron import loft, blade, BODY, PALE, WING, TIP, BLACK, BEAK, LEG
VIEW = dict(angle=-60, lift=0.25, res=(900, 700), samples=32)

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
    def lift(x, o):                                                          # raised in a V, bent at the wrist: the arm
        if o < 0.4: return x, 0.55 * o                                           # rises at about 30 degrees, the hand steeper
        return x + 0.35 * (o - 0.4), 0.22 + 0.95 * (o - 0.4)                     # and swept back
    def feather(nm, w, sy, root_, tip_, width, color, t=0.006):              # one tapered feather from root to tip
        (x0, o0), (x1, o1) = root_, tip_
        dx, do = x1 - x0, o1 - o0; L = math.hypot(dx, do); nx, no = -do / L * width / 2, dx / L * width / 2
        pts = [(x0 + nx, o0 + no), (x0 + dx * 0.7 + nx, o0 + do * 0.7 + no), (x1, o1), (x0 + dx * 0.7 - nx, o0 + do * 0.7 - no), (x0 - nx, o0 - no)]
        out = []
        for (x, o) in pts:
            X, Z = lift(x, o); out.append((X, sy * o, Z))
        return blade(nm, out, color, w, t=t, up=True)
    for sy, nm in ((-1, 'heron_wing_l'), (1, 'heron_wing_r')):
        w = root(nm); w.location = (-0.06, sy * 0.07, 0.03); w.parent = r
        arm = [(0.0, 0.0), (-0.04, 0.2), (-0.05, 0.42), (0.16, 0.44), (0.17, 0.2), (0.16, 0.0)]
        blade('coverts', [(lambda X, Z: (X, sy * o, Z))(*lift(x, o)) for (x, o) in arm], WING, w, t=0.012, up=True)
        for k in range(8):                                                     # secondaries along the trailing edge, overlapping
            o0 = 0.02 + k * 0.055
            feather('secondary', w, sy, (0.08, o0), (0.3 + 0.02 * math.sin(k), o0 + 0.03), 0.075, 0xB1B9C3 if k % 2 else 0xA4ADB8)
        hand = [(-0.05, 0.4), (0.0, 0.62), (0.12, 0.6), (0.17, 0.42)]           # the hand coverts over the primaries' bases
        blade('hand', [(lambda X, Z: (X, sy * o, Z))(*lift(x, o)) for (x, o) in hand], WING, w, t=0.014, up=True)
        for k in range(9):                                                     # primaries: a wide fan of long tapered fingers
            a_ = math.radians(-8 + k * 11); o0 = 0.5 + 0.01 * k; x0 = 0.0 + k * 0.022
            L = 0.36 - abs(k - 2.5) * 0.022
            tip = (x0 + math.sin(a_) * L, o0 + math.cos(a_) * L)
            feather('primary', w, sy, (x0, o0), tip, 0.055, TIP if k < 6 else 0x8D96A2, t=0.005)
    for k in range(3):
        blade('tail', [(0.27, (k - 1) * 0.03, 0.0), (0.38, (k - 1) * 0.045, 0.0), (0.37, (k - 1) * 0.045 + 0.02, 0.0), (0.27, (k - 1) * 0.03 + 0.012, 0.0)], 0xA9B1BB, r, up=True)
    return r
