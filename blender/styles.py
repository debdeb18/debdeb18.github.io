"""Render the same little scene (chair, suitcase, station sign) in several styles, to choose one.
    python blender/styles.py            -> blender/styles/<letter>-<name>.png"""
import sys, os, random
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
import lib
from assets import chair, suitcase, station_sign

STYLES = {
    # A: what the first three props used. Warm wood, gently hand-made.
    'A-storybook': dict(),
    # B: soft clay toy. Chunky, very rounded, straight, pastel.
    'B-clay-toy': dict(jitter=0.2, bevel=2.4, chunk=1.5, lean=0.4, ground=0xEFC9D9, sky=(1.0, 0.8, 0.88), sky_power=0.6, sun=(1, 0.97, 0.95), sun_power=2.0,
        pal=dict(wood=0xF2C4A0, wood_dark=0xD99A86, wood_pale=0xFFE6CF, red=0xFF8FA3, red_dark=0xE86F88, cream=0xFFF8EE, teal=0x9FD8D0, teal_dark=0x79BDB6,
                 iron=0x6A6299, brass=0xFFD98A, roof=0xB7A5E8, roof_dark=0x9C88D6, stone=0xE6DDF0, pink=0xFFC9DE)),
    # C: crooked fairytale. Everything leans, saturated teal and orange, darker timber.
    'C-crooked-fairytale': dict(jitter=1.9, bevel=1.3, chunk=1.2, lean=2.3, ground=0xD8C79A, sky=(0.35, 0.62, 0.95), sun=(1, 0.9, 0.72), sun_power=3.8,
        pal=dict(wood=0xC98A4B, wood_dark=0x6E4630, wood_pale=0xE2B877, red=0xD9532F, red_dark=0xA63A22, cream=0xE9DDB8, teal=0x3FA79A, teal_dark=0x2A7A72,
                 iron=0x2E2B33, brass=0xD9A441, roof=0xE8772E, roof_dark=0xB9551F, stone=0x9C9488, pink=0xE8A27A)),
    # D: dusk and glow. Muted and quiet, low warm sun, lantern doing the work.
    'D-dusk-glow': dict(jitter=0.8, bevel=1.6, chunk=1.1, lean=1.0, emit=40.0, ground=0x7F79B0, sky=(0.3, 0.32, 0.7), sky_power=0.9, sun=(1.0, 0.62, 0.45), sun_power=2.6, sun_height=76,
        pal=dict(wood=0xB89AA0, wood_dark=0x6B5A78, wood_pale=0xD9C6CC, red=0xE0607A, red_dark=0xA84462, cream=0xE9E4F5, teal=0x6FA3C4, teal_dark=0x4D7FA3,
                 iron=0x35345A, brass=0xFFD08A, roof=0x8F7FC4, roof_dark=0x6F5FA8, stone=0x9A96B8, pink=0xF0B4D0, glow=0xFFE2A0)),
}
os.makedirs(here + '/styles', exist_ok=True)
for name in (sys.argv[1:] or STYLES):
    cfg = dict(STYLES[name]); lib.reset(); lib.set_style(cfg.pop('pal', None), **cfg); random.seed(7)
    station_sign.build()
    c = chair.build(); c.location = (-0.35, -1.25, 0); c.rotation_euler = (0, 0, 0.35)
    s = suitcase.build(); s.location = (0.55, -1.2, 0); s.rotation_euler = (0, 0, -0.25)
    lib.output(name, here, angle=22, lift=0.3, res=(1100, 800), samples=80, export=False, preview='%s/styles/%s.png' % (here, name), zoom=1.12)
    print('BUILT', name)
