"""The traveller's suitcase: rounded, strapped, with stickers from Semarang and Seoul."""
from lib import *
VIEW = dict(angle=25)

def build():
    r = root('suitcase')
    box('body', (0.62, 0.22, 0.42), (0, 0, 0.03), color='teal', parent=r, bevel=0.05, segs=4)
    box('seam', (0.63, 0.012, 0.43), (0, 0, 0.025), color='teal_dark', parent=r, bevel=0.004)
    for x in (-0.17, 0.17):
        box('strap', (0.05, 0.235, 0.435), (x, 0, 0.023), color='wood_dark', parent=r, bevel=0.012)
        box('buckle', (0.065, 0.02, 0.05), (x, -0.118, 0.3), color='brass', parent=r, bevel=0.008, rough=0.35)
    for sx in (-1, 1):
        for z in (0.03, 0.41):
            ball('corner', 0.045, (sx * 0.285, 0, z + 0.02), (1, 2.3, 1), 'brass', r, rough=0.35)
        cyl('foot', 0.025, 0.03, 0.03, (sx * 0.22, 0, 0), color='iron', parent=r, bevel=0.006)
    tube('handle', [(-0.11, 0, 0.45), (-0.09, 0, 0.5), (0.09, 0, 0.5), (0.11, 0, 0.45)], 0.014, 'wood_dark', r)
    # stickers and a luggage tag
    cyl('sticker_a', 0.06, 0.06, 0.004, (-0.03, -0.112, 0.2), (90, 0, 0), 'red', r, bevel=0)
    box('sticker_b', (0.1, 0.004, 0.065), (0.06, -0.112, 0.1), (0, 12, 0), 'cream', r, bevel=0.002)
    box('sticker_c', (0.07, 0.004, 0.07), (-0.07, -0.112, 0.08), (0, -18, 0), 'pink', r, bevel=0.002)
    tube('tag_string', [(0.09, 0, 0.49), (0.16, -0.06, 0.44), (0.2, -0.125, 0.36)], 0.004, 'cream', r)
    box('tag', (0.07, 0.006, 0.1), (0.2, -0.127, 0.27), (0, 8, 0), 'cream', r, bevel=0.003)
    return r
