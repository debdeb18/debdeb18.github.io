"""Shared helpers for building the portfolio's props in Blender (run headless with the bpy module).
Every prop is built at the origin, sitting on the ground (z = 0), facing -Y, in metres."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix

PAL = dict(wood=0xD9A066, wood_dark=0x8F5A3C, wood_pale=0xEBC894, red=0xD8364A, red_dark=0xA8243A, cream=0xFFF0DC,
           teal=0x3F8F9A, teal_dark=0x2C6670, iron=0x3B3A4A, brass=0xE8B84A, roof=0xD9694A, roof_dark=0xB04E3C,
           glow=0xFFD98A, leaf=0x6FBF73, pink=0xFFB7C9, sky=0x8FB4FF, stone=0xB9B2A8, white=0xFFFFFF,
           train_red=0xB8403A, train_red_dark=0x8E2E2C, train_cream=0xF0E2C0, train_roof=0x8D8A86, window=0xFFC777, lamp=0xFFD28A,
           tree=0x2B6A45, tree_mid=0x3F8A4C, tree_light=0x78B85A, tree_hi=0xB4DC6E, trunk=0x5A3F30)

# The active style: how crooked, how chunky, how rounded, and the studio colours. See blender/styles.py.
BASE_PAL = dict(PAL)
STYLE = dict(jitter=1.0, bevel=1.0, chunk=1.0, lean=1.0, emit=1.0, ground=0xBFE3D0, sky=(0.62, 0.78, 1.0), sky_power=0.9, sun=(1, 0.95, 0.85), sun_power=3.2, sun_height=52)
def set_style(pal=None, **kw):
    PAL.clear(); PAL.update(BASE_PAL); PAL.update(pal or {})
    STYLE.update(jitter=1.0, bevel=1.0, chunk=1.0, lean=1.0, emit=1.0, ground=0xBFE3D0, sky=(0.62, 0.78, 1.0), sky_power=0.9, sun=(1, 0.95, 0.85), sun_power=3.2, sun_height=52)
    STYLE.update(kw); _mats.clear()

# ---------- pieces: named groups of objects that are exported as separate models ----------
_piece = None
PIECES = []          # (name, root object, export?) in creation order; repeated names are instances of the same model
def piece(name, anchor=(0, 0, 0), export=True):
    """Everything created after this call belongs to the piece `name`, whose origin is `anchor`."""
    global _piece
    e = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(e); e.location = anchor
    _piece = (e, Matrix.Translation(anchor).inverted()); PIECES.append((name, e, export))
    return e
def adopt(name, obj, export=True):
    """Register an object that already has its own root (a prop built by an asset module) as a piece."""
    PIECES.append((name, obj, export)); return obj
def _attach(o, parent):
    if parent: o.parent = parent
    elif _piece: o.parent = _piece[0]; o.matrix_parent_inverse = _piece[1]

def export_pieces(models_dir, layout_path, lights=()):
    """Write one .glb per piece (at its own origin) and a layout file saying where every instance goes."""
    import json
    layout = dict(note='Blender coordinates: x right, y away, z up, metres.', pieces=[], lights=[dict(pos=[round(v, 3) for v in l[0]], power=l[1], color=list(l[2])) for l in lights])
    seen = set()
    def pick(o):
        o.select_set(True)
        for c in o.children: pick(c)
    for name, obj, exp in PIECES:
        layout['pieces'].append(dict(name=name, pos=[round(v, 3) for v in obj.location], rot_z=round(obj.rotation_euler[2], 4), scale=round(obj.scale[0], 3), model=bool(exp)))
        if not exp or name in seen: continue
        seen.add(name)
        saved = obj.matrix_basis.copy(); obj.matrix_basis = Matrix.Identity(4); bpy.context.view_layer.update()
        bpy.ops.object.select_all(action='DESELECT'); pick(obj)
        bpy.ops.export_scene.gltf(filepath='%s/%s.glb' % (models_dir, name), use_selection=True, export_apply=True)
        obj.matrix_basis = saved
    bpy.context.view_layer.update()
    json.dump(layout, open(layout_path, 'w'), indent=1)
    return sorted(seen)

def reset():
    global _piece
    _piece = None; PIECES.clear()
    bpy.ops.wm.read_factory_settings(use_empty=True)

def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

_mats = {}
def mat(color, rough=0.75, emit=0.0):
    """A flat cartoon material. `color` is a palette name or a hex int."""
    hexv = PAL[color] if isinstance(color, str) else color
    emit *= STYLE['emit']
    key = (hexv, rough, emit)
    if key in _mats: return _mats[key]
    m = bpy.data.materials.new('c_%06x' % hexv); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    rgba = (_lin(hexv >> 16 & 255), _lin(hexv >> 8 & 255), _lin(hexv & 255), 1)
    b.inputs['Base Color'].default_value = rgba; b.inputs['Roughness'].default_value = rough
    if emit:
        b.inputs['Emission Color'].default_value = rgba; b.inputs['Emission Strength'].default_value = emit
    _mats[key] = m
    return m

def root(name):
    e = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(e); return e

def _finish(name, mesh, color, loc, rot, parent, bevel, segs=3, **mk):
    for p in mesh.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, mesh); bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.rotation_euler = [math.radians(a * (STYLE['lean'] if abs(a) < 20 else 1)) for a in rot]
    o.data.materials.append(mat(color, **mk))
    if bevel:
        b = o.modifiers.new('bevel', 'BEVEL'); b.width = bevel * STYLE['bevel']; b.segments = segs; b.limit_method = 'ANGLE'; b.angle_limit = math.radians(35)
    o.modifiers.new('normals', 'WEIGHTED_NORMAL')
    _attach(o, parent)
    return o

def box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), color='wood', parent=None, bevel=0.02, jitter=0.0, taper=1.0, **mk):
    """A rounded box. `loc` is the centre of its base. jitter makes it hand-made and crooked; taper narrows the top."""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    jitter *= STYLE['jitter']; ch = STYLE['chunk']
    size = tuple(d * ch if d < 0.16 else d for d in size)      # chunkier styles thicken the thin parts
    for v in bm.verts:
        k = taper if v.co.z > 0 else 1.0
        v.co = Vector((v.co.x * size[0] * k + random.uniform(-jitter, jitter), v.co.y * size[1] * k + random.uniform(-jitter, jitter), (v.co.z + 0.5) * size[2] + random.uniform(-jitter, jitter) * 0.5))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return _finish(name, me, color, loc, rot, parent, bevel, **mk)

def gable(name, span, height, thick, loc=(0, 0, 0), color='cream', parent=None, **mk):
    """A triangular wall end (under a pitched roof). `span` runs along Y, the point is up."""
    bm = bmesh.new()
    vs = [bm.verts.new(c) for c in ((-thick / 2, -span / 2, 0), (-thick / 2, span / 2, 0), (-thick / 2, 0, height), (thick / 2, -span / 2, 0), (thick / 2, span / 2, 0), (thick / 2, 0, height))]
    for f in ((0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)): bm.faces.new([vs[i] for i in f])
    bm.normal_update(); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return _finish(name, me, color, loc, (0, 0, 0), parent, 0, **mk)

def cyl(name, r1, r2, h, loc=(0, 0, 0), rot=(0, 0, 0), color='wood', parent=None, bevel=0.015, verts=20, **mk):
    """A cylinder or cone standing on its base: r1 at the bottom, r2 at the top."""
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r1, radius2=max(r2, 0.0005), depth=h)
    for v in bm.verts: v.co.z += h / 2
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return _finish(name, me, color, loc, rot, parent, bevel, **mk)

def ball(name, r, loc=(0, 0, 0), scale=(1, 1, 1), color='wood', parent=None, **mk):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=14, radius=r)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = _finish(name, me, color, loc, (0, 0, 0), parent, 0, **mk); o.scale = scale
    return o

def lump(name, r, loc=(0, 0, 0), scale=(1, 1, 1), color='leaf', parent=None, strength=0.3, grain=0.55, **mk):
    """A lumpy, cauliflower-like blob: the building block for leafy canopies, bushes and clouds."""
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=r)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.scale = scale; o.data.materials.append(mat(color, **mk))
    tex = bpy.data.textures.new('lump', 'VORONOI'); tex.noise_scale = r * grain; tex.distance_metric = 'DISTANCE'
    d = o.modifiers.new('lumps', 'DISPLACE'); d.texture = tex; d.texture_coords = 'GLOBAL'; d.strength = -r * strength * 2.2; d.mid_level = 0.35
    _attach(o, parent)
    return o

def tube(name, pts, radii, color='iron', parent=None, **mk):
    """A smooth pipe through `pts`, with a radius per point (so it can taper)."""
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 1.0; cu.bevel_resolution = 4; cu.use_fill_caps = True; cu.resolution_u = 10
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    if not isinstance(radii, (list, tuple)): radii = [radii] * len(pts)
    for p, co, r in zip(sp.bezier_points, pts, radii):
        p.co = co; p.handle_left_type = p.handle_right_type = 'AUTO'; p.radius = r
    o = bpy.data.objects.new(name, cu); bpy.context.scene.collection.objects.link(o)
    cu.materials.append(mat(color, **mk))
    _attach(o, parent)
    return o

def text(name, body, size, loc, rot=(90, 0, 0), color='iron', parent=None):
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.size = size; cu.extrude = 0.004; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    o = bpy.data.objects.new(name, cu); bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.rotation_euler = [math.radians(a) for a in rot]; cu.materials.append(mat(color))
    _attach(o, parent)
    return o

def shingles(name, width, depth, rows, loc, pitch, color='roof', dark='roof_dark', parent=None, yaw=0, tile=0.22):
    """One slope of a shingled roof: overlapping, slightly crooked tiles. Pivot is the eave (lower edge) centre."""
    e = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(e)
    e.location = loc; e.rotation_euler = (math.radians(pitch), 0, math.radians(yaw))
    _attach(e, parent)
    step = depth / rows; n = max(2, round(width / tile))
    for r in range(rows):
        off = (r % 2) * 0.5
        for i in range(-1, n + 1):
            x = (i + off) / n * width - width / 2
            if x < -width / 2 - 0.08 or x > width / 2 + 0.08: continue
            box('%s_t' % name, (width / n * 0.96, step * 1.5, 0.035), (x, r * step + step * 0.6, 0.02 + (rows - r) * 0.0), (random.uniform(4, 9), 0, random.uniform(-4, 4)),
                color if random.random() > 0.3 else dark, e, bevel=0.012, jitter=0.012, segs=1)
    return e

# ---------- preview render, .blend and .glb ----------
def _bounds(objs):
    lo, hi = Vector((1e9,) * 3), Vector((-1e9,) * 3)
    bpy.context.view_layer.update()
    for o in objs:
        if o.type not in ('MESH', 'CURVE', 'FONT'): continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
    return lo, hi

def output(name, out_dir, angle=35, lift=0.42, res=(1000, 800), samples=72, export=True, preview=None, zoom=1.0):
    sc = bpy.context.scene
    assets = list(sc.collection.all_objects)
    bpy.ops.object.select_all(action='DESELECT')
    for o in assets: o.select_set(True)
    if export: bpy.ops.export_scene.gltf(filepath='%s/../models/%s.glb' % (out_dir, name), use_selection=True, export_apply=True)
    lo, hi = _bounds(assets); c = (lo + hi) / 2; rad = (hi - lo).length / 2
    # studio: soft ground, warm key light, cool fill
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=60); me = bpy.data.meshes.new('ground'); bm.to_mesh(me); bm.free()
    g = bpy.data.objects.new('_ground', me); sc.collection.objects.link(g); g.data.materials.append(mat(STYLE['ground'], 1.0))
    sun = bpy.data.lights.new('_sun', 'SUN'); sun.energy = STYLE['sun_power']; sun.angle = math.radians(12); sun.color = STYLE['sun']
    so = bpy.data.objects.new('_sun', sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(STYLE['sun_height']), 0, math.radians(angle + 70))
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (*STYLE['sky'], 1); bg.inputs[1].default_value = STYLE['sky_power']
    cam = bpy.data.cameras.new('_cam'); cam.lens = 70; co = bpy.data.objects.new('_cam', cam); sc.collection.objects.link(co); sc.camera = co
    a = math.radians(angle); d = rad * 4.6 / zoom
    co.location = c + Vector((math.sin(a) * d, -math.cos(a) * d, d * lift))
    co.rotation_euler = (c - co.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = samples
    try: sc.cycles.use_denoising = True
    except Exception: pass
    sc.view_settings.view_transform = 'Standard'
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = preview or '%s/previews/%s.png' % (out_dir, name)
    try: bpy.ops.render.render(write_still=True)
    except Exception:
        sc.cycles.use_denoising = False; bpy.ops.render.render(write_still=True)
    if export: bpy.ops.wm.save_as_mainfile(filepath='%s/files/%s.blend' % (out_dir, name))
