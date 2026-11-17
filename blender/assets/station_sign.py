"""The station sign: plank board on two crooked posts, a little shingled roof, and a lantern on an iron arm.
The name itself (어딘가 / SOMEWHERE / ENTAH DI MANA) is drawn in the browser so it stays crisp in three languages."""
from lib import *
VIEW = dict(angle=28, lift=0.3)

def build():
    r = root('station_sign')
    for sx in (-1, 1):
        box('post', (0.13, 0.13, 2.75), (sx * 1.45, 0, 0), (0, sx * -2.5, 0), 'wood_dark', r, bevel=0.03, jitter=0.012, taper=0.82)
        box('post_foot', (0.3, 0.3, 0.16), (sx * 1.47, 0, 0), color='stone', parent=r, bevel=0.04, jitter=0.02)
        ball('post_cap', 0.075, (sx * 1.39, 0, 2.78), (1, 1, 0.8), 'brass', r, rough=0.35)
    # board: three planks in a frame
    for i, z in enumerate((1.36, 1.72, 2.08)):
        box('board_plank', (2.7, 0.05, 0.345), (0, 0, z), (0, (i - 1) * 0.7, 0), 'cream', r, bevel=0.015, jitter=0.01)
    box('frame_top', (2.86, 0.08, 0.07), (0, 0, 2.43), color='wood', parent=r, bevel=0.02, jitter=0.008)
    box('frame_bottom', (2.86, 0.08, 0.07), (0, 0, 1.3), color='wood', parent=r, bevel=0.02, jitter=0.008)
    for x in (-1.2, -0.4, 0.4, 1.2): ball('nail', 0.018, (x, -0.035, 2.465), color='iron', parent=r)
    box('stripe', (2.5, 0.012, 0.05), (0, -0.03, 1.47), color='red', parent=r, bevel=0.004)
    text('label', 'SOMEWHERE', 0.3, (0, -0.032, 1.9), color='iron', parent=r)
    # roof: two shingled slopes and a ridge beam
    shingles('roof_front', 3.3, 0.42, 3, (0, -0.36, 2.62), 28, parent=r)
    shingles('roof_back', 3.3, 0.42, 3, (0, 0.36, 2.62), 28, parent=r, yaw=180)
    box('ridge', (3.36, 0.07, 0.07), (0, 0, 2.81), color='roof_dark', parent=r, bevel=0.02, jitter=0.01)
    box('rafter', (3.1, 0.6, 0.04), (0, 0, 2.58), color='wood_dark', parent=r, bevel=0.01)
    # lantern on a curled iron arm
    tube('arm', [(1.45, 0, 2.35), (1.75, 0, 2.5), (2.05, 0, 2.42), (2.1, 0, 2.25), (2.02, 0, 2.2)], [0.022, 0.02, 0.016, 0.012, 0.01], 'iron', r)
    tube('chain', [(2.1, 0, 2.25), (2.1, 0, 2.08)], 0.006, 'iron', r)
    cyl('lantern_top', 0.02, 0.1, 0.07, (2.1, 0, 2.0), (180, 0, 0), 'iron', r, bevel=0.006)
    cyl('lantern_glass', 0.065, 0.08, 0.17, (2.1, 0, 1.83), color='glow', parent=r, bevel=0.01, emit=2.5)
    cyl('lantern_base', 0.085, 0.06, 0.03, (2.1, 0, 1.8), color='iron', parent=r, bevel=0.006)
    return r
