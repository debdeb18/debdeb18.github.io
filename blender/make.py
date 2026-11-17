"""Build one prop:  python blender/make.py chair     (or `all`)
Writes blender/files/<name>.blend, blender/previews/<name>.png and models/<name>.glb"""
import sys, os, importlib, random
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
import lib
names = sys.argv[1:]
if names == ['all']: names = sorted(f[:-3] for f in os.listdir(here + '/assets') if f.endswith('.py'))
for n in names:
    lib.reset(); lib._mats.clear(); random.seed(7)
    mod = importlib.import_module('assets.' + n)
    mod.build()
    lib.output(n, here, **getattr(mod, 'VIEW', {}))
    print('BUILT', n)
