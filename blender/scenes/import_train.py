"""Prepare the Sketchfab train for the terminal.
    "Spirited Away Train" by judpro, CC BY 4.0: https://sketchfab.com/3d-models/spirited-away-train-2f7c2bbc09614f1eba8e6ec7d8eb00e0
    python blender/scenes/import_train.py <path to spirited_away_train.glb>   -> blender/export/terminal/seatrain.glb
Re-orients it like our other train pieces: running along +Y from y = 0 (the leading cab), centred on x, wheels on z = 0."""
import sys, os, math
import bpy
from mathutils import Vector, Matrix
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
for o in bpy.context.scene.objects: o.select_set(o.type == 'MESH')
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
lo = Vector((1e9,) * 3); hi = Vector((-1e9,) * 3)
for o in meshes:
    for v in o.data.vertices: lo = Vector(map(min, lo, v.co)); hi = Vector(map(max, hi, v.co))
# the model runs along x; turn it to run along +y, then move the leading end to y = 0 and the wheels to z = 0
M = Matrix.Translation((0, 0, 0)) @ Matrix.Rotation(math.pi / 2, 4, 'Z')
for o in meshes: o.data.transform(M)
lo2 = Vector((1e9,) * 3); hi2 = Vector((-1e9,) * 3)
for o in meshes:
    for v in o.data.vertices: lo2 = Vector(map(min, lo2, v.co)); hi2 = Vector(map(max, hi2, v.co))
T = Matrix.Translation((-(lo2.x + hi2.x) / 2, -lo2.y, -lo2.z))
for o in meshes: o.data.transform(T); o.data.update()
for o in [o for o in bpy.context.scene.objects if o.type == 'EMPTY']: bpy.data.objects.remove(o)
print('length %.2f width %.2f height %.2f' % (hi2.y - lo2.y, hi2.x - lo2.x, hi2.z - lo2.z))
out = here + '/export/terminal/seatrain.glb'
bpy.ops.export_scene.gltf(filepath=out, export_apply=True, export_image_format='AUTO')
print('EXPORTED', out)
