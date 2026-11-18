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

def mat_vc(color, rough=0.75):
    """A material whose colour is painted on the vertices (the 'Col' attribute). Named after `color` so the website
    still knows what surface it is."""
    hexv = PAL[color] if isinstance(color, str) else color
    key = ('vc', hexv)
    if key in _mats: return _mats[key]
    m = bpy.data.materials.new('c_%06x_vc' % hexv); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']; ca = nt.nodes.new('ShaderNodeVertexColor'); ca.layer_name = 'Col'
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1.0
    mx.inputs['B'].default_value = (_lin(hexv >> 16 & 255) * 1.25, _lin(hexv >> 8 & 255) * 1.25, _lin(hexv & 255) * 1.25, 1)
    nt.links.new(ca.outputs['Color'], mx.inputs['A']); nt.links.new(mx.outputs['Result'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
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

def plank(name, size, loc=(0, 0, 0), rot=(0, 0, 0), color='wood', parent=None, bevel=0.014, wobble=1.0, knots=0, depth=0.0018, paint=None,
          cuts=True, nails=True, corner=0.22, **mk):
    """A stylised carved board along X (the hand-sculpted look): grain grooves cut into the top that flow around a knot
    or two, rings around each knot, chips out of the long edges, splits running in from the ends, soft chunky bevels,
    and a slight bow. With `cuts` (the default) the grain is sculpted as thin, sharp cuts that taper in and out, like
    a hand-sculpted board, instead of grooves; `nails` adds a nail hole near each end; `corner` rounds the corners of
    the board seen from above (a share of its width). `loc` is the centre of its base, like box()."""
    L, W, T = size
    # a fine grid for the carved top, then plain sides and a flat bottom (the carving only needs detail on top)
    nx, ny = (max(16, min(160, int(L / 0.004))), max(12, min(60, int(W / 0.0018)))) if cuts else (max(16, int(L / 0.009)), max(12, int(W / 0.0036)))
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=nx, y_segments=ny, size=0.5)
    for v in bm.verts: v.co.z = 1.0                                          # -0.5..0.5 like the cube, top at z=1
    ix, iy = 0.5 - 1.0 / nx, 0.5 - 1.0 / ny                                   # the row just inside each edge stays, so the
    keep = {v for v in bm.verts if abs(abs(v.co.x) - ix) < 1e-5 or abs(abs(v.co.y) - iy) < 1e-5}   # light edge paint stays thin
    top = set(bm.verts)
    edges = [e for e in bm.edges if e.is_boundary]
    ext = bmesh.ops.extrude_edge_only(bm, edges=edges)
    for v in [g for g in ext['geom'] if isinstance(g, bmesh.types.BMVert)]: v.co.z = 0.0
    bmesh.ops.contextual_create(bm, geom=[e for e in bm.edges if e.is_boundary])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    R = random.uniform; sm = lambda t: t * t * (3 - 2 * t)
    wave = lambda f: (lambda a, b, c, d: (lambda t: math.sin(t * a + b) * 0.6 + math.sin(t * c + d) * 0.4))(R(0.6, 1.4) * f, R(0, 6.3), R(1.8, 3) * f, R(0, 6.3))
    eL, eR, th, flow = wave(9), wave(9), wave(7), wave(11)
    nk = knots if knots is not None else random.choice((0, 1, 1, 2))
    ks = [(R(-0.3, 0.3) * L, R(-0.15, 0.15) * W, R(0.015, 0.022)) for _ in range(nk)]
    spacing = W / R(1.8, 2.6); phase = R(0, 1)
    fades = [wave(5) for _ in range(8)]
    chips = [(R(-0.5, 0.5) * L, random.choice((-1, 1)), R(0.012, 0.025), R(0.3, 0.7)) for _ in range(random.randint(0, 2))]
    splits = [(e, R(-0.25, 0.25) * W, R(0.02, 0.05)) for e in (-1, 1) if random.random() < 0.5]
    bow = R(-1, 1) * 0.006 * wobble; slant = (R(-0.04, 0.04), R(-0.04, 0.04))
    cl = []                                                 # thin grain cuts: (v at start, slope, u0, u1, half-width)
    for _ in range(random.randint(int(W / 0.016), int(W / 0.011)) if cuts else 0):
        ln = R(0.12, 0.45) * L; u0 = R(-0.5 * L + 0.02, 0.5 * L - 0.02 - ln)
        cl.append((R(-0.42, 0.42) * W, R(-0.012, 0.012), u0, u0 + ln, R(0.0016, 0.0024)))
    nl = [(e * (0.5 * L - R(0.03, 0.045)), R(-0.2, 0.2) * W) for e in (-1, 1)] if nails else []
    rc = corner * W
    def groove(u, v):
        if not cuts: return groove_lines(u, v)
        d = 0.0
        for (v0, sl, u0, u1, hw) in cl:                     # a V-shaped cut, tapering to nothing at both ends
            if u0 < u < u1:
                t = (u - u0) / (u1 - u0); tp = math.sin(math.pi * t) ** 0.6
                d = max(d, max(0.0, 1 - abs(v - (v0 + sl * (u - u0))) / (hw * (0.4 + 0.6 * tp))) * tp)
        for (nu, nv) in nl:                                  # nail holes
            rr = math.hypot(u - nu, v - nv)
            if rr < 0.005: d = max(d, 1.4 * sm(1 - rr / 0.005))
        for (e, sv, sl2) in splits:
            de = 0.5 * L - e * u
            if de < sl2: d = max(d, max(0.0, 1 - abs(v - sv) / 0.0018) * (1 - de / sl2) * 1.3)
        return d
    def groove_lines(u, v):                                 # how deep the carving is at (u, v) on the top, 0..1
        vv = v + 0.003 * flow(u / L)
        for (ku, kv, kr) in ks:                                 # grain lines bend around each knot
            fu = math.exp(-((u - ku) / (2.6 * kr)) ** 2); dv = vv - kv
            vv -= math.copysign(1, dv) * kr * 1.25 * fu * math.exp(-(dv / (2.2 * kr)) ** 2) * 1.6
        q = vv / spacing + phase; line = math.floor(q + 0.5); f = abs(q - line)
        d = max(0.0, 1 - f / 0.12); d = sm(d) * (0.55 + 0.45 * fades[int(line) % 8](u / L * 3))
        d *= max(0.0, min(1.0, (0.5 * L - abs(u)) / 0.01))      # grooves fade out just before the ends
        for (ku, kv, kr) in ks:                                 # rings around the knot and a dimple in its eye
            rr = math.hypot((u - ku) / 1.5, v - kv)
            d *= sm(max(0.0, min(1.0, (rr - 1.35 * kr) / (0.5 * kr))))   # keep the grain lines out of the knot
            for ring in (0.62, 1.2):                            # two smooth rings, then a dimple in the eye
                d = max(d, sm(max(0.0, 1 - abs(rr - ring * kr) / 0.0036)) * 0.9)
            if rr < kr * 0.3: d = max(d, sm(1 - rr / (kr * 0.3)) * 0.8)
        for (e, sv, sl) in splits:                              # a split running in from the end, deepest at the end
            de = 0.5 * L - e * u
            if de < sl: d = max(d, sm(max(0.0, 1 - abs(v - sv) / 0.0035)) * (1 - de / sl) * 1.4)
        return d
    P = paint or dict(body=0xE6E6E6, edge=0xFFF0D8, under=0xC8C8C8)          # multiplies the painted grain
    lin = lambda h: Vector(((h >> 16 & 255) / 255, (h >> 8 & 255) / 255, (h & 255) / 255))   # the exporter converts these itself
    C = {k: lin(h) for k, h in P.items()}
    col = bm.verts.layers.color.new('Col')
    for v in bm.verts:
        x, y, z = v.co.x, v.co.y, v.co.z
        c = C['body'] if v in top else C['under']
        u = x * L + (slant[0] if x < 0 else slant[1]) * y * W * (abs(x) * 2) ** 8   # ends cut a little off square
        Y = y * W + (eL(x) if y > 0 else eR(x)) * 0.0005 * wobble * abs(y) * 2       # edges barely wander
        cx_, cy_ = abs(u) - (0.5 * L - rc), abs(Y) - (0.5 * W - rc)              # corners rounded off, seen from above
        if rc > 0 and cx_ > 0 and cy_ > 0:
            k = math.hypot(cx_, cy_)
            if k > rc: u = math.copysign(0.5 * L - rc + cx_ * rc / k, u); Y = math.copysign(0.5 * W - rc + cy_ * rc / k, Y)
        Z = z * T * (1 + th(x) * 0.03 * wobble)
        for (cu, side, cw, cd) in chips:                         # chips out of the long top edges
            if y * side > 0.3:
                k = max(0.0, 1 - abs(u - cu) / cw) * (y * side - 0.3) / 0.2
                if k > 0: Y -= side * sm(k) * 0.006 * cd; Z -= sm(k) * T * 0.3 * cd * z
        for (e, sv, sl) in splits:                               # the end splits notch the end face too
            if x * e > 0.499 and abs(Y - sv) < 0.004: u -= e * 0.004
        if z > 0.99:
            g = groove(u, Y); Z -= g * (0.003 if cuts else depth) * wobble
            if abs(x) > 0.4999 or abs(y) > 0.4999: c = C['edge']                 # light, worn edges all round
            for (cu, side, cw, cd) in chips:
                if y * side > 0.42 and abs(u - cu) < cw: c = c.lerp(C['edge'], 0.7)
        v[col] = (c.x, c.y, c.z, 1.0)
        Z += bow * (1 - (2 * x) ** 2)
        v.co = Vector((u, Y, Z))
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(4), verts=[v for v in bm.verts if v not in keep], edges=[e for e in bm.edges if not (set(e.verts) & keep)])   # thin out the flat parts
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')         # so the bevel stays clean
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = _finish(name, me, color, loc, rot, parent, bevel, segs=2, **mk)
    o.data.materials[0] = mat_vc(color)                                      # the colour comes from the painted vertices
    o.modifiers['bevel'].angle_limit = math.radians(60)                      # bevel the board's edges, not the carving
    return o

def painted_box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), color='stone', parent=None, bevel=0.02, jitter=0.0, along='x',
                band=0.18, paint=None, sculpt=True, face=0, **mk):
    """A box with hand-painted light and shade on its vertices, like a painted stone or tile: a light band along the
    top and the left, a darker, stained band along the bottom and the right. `along` is the face's horizontal axis
    ('x' or 'y'); a flat tile (along='top') gets a light rim all round its top. The colour multiplies `color`."""
    P = paint or dict(light=0xFFFDF6, mid=0xE8E5DC, low=0xB8B2A0, right=0xD0CABA)
    C = {k: Vector(((h >> 16 & 255) / 255, (h >> 8 & 255) / 255, (h & 255) / 255)) for k, h in P.items()}
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    cut = lambda co, no: bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=co, plane_no=no)
    b = 0.5 - band
    for k in (-b, b): cut((k, 0, 0), (1, 0, 0)); cut((0, k, 0), (0, 1, 0)); cut((0, 0, k), (0, 0, 1))
    nax = {'x': 1, 'y': 0, 'top': 2}[along]                                   # the axis the visible face looks along
    if sculpt:                                                                # a finer grid on the face, for the sculpting
        for ax in range(3):
            if ax == nax: continue
            n = max(2, int(size[ax] / 0.06))
            for i in range(1, n):
                k = -0.5 + i / n
                if abs(abs(k) - b) > 0.01: cut(tuple(k if j == ax else 0 for j in range(3)), tuple(1 if j == ax else 0 for j in range(3)))
    R = random.uniform
    bumps = [(R(-0.5, 0.5), R(-0.5, 0.5), R(0.15, 0.4), R(-1, 1)) for _ in range(4)]          # gentle swells in the face
    chips = [(random.choice((-0.5, 0.5)), R(-0.5, 0.5), R(0.04, 0.09)) for _ in range(random.randint(0, 2))]   # bites out of an edge
    crack = (R(-0.3, 0.3), R(-0.5, 0.5), R(0.6, 1.4)) if random.random() < 0.3 else None              # a hairline crack
    jitter *= STYLE['jitter']; ch = STYLE['chunk']
    size = tuple(d * ch if d < 0.16 else d for d in size)
    col = bm.verts.layers.color.new('Col')
    for v in bm.verts:
        x, y, z = v.co.x, v.co.y, v.co.z
        cl01 = lambda t: max(0.0, min(1.0, t)); sm = lambda t: t * t * (3 - 2 * t)
        if along == 'top':                                                    # a soft light rim round the top, darker below
            c = C['mid'].lerp(C['light'], sm(cl01((max(abs(x), abs(y)) - 0.28) / 0.22))) if z > 0.49 else C['low']
        else:                                                                 # light from the top left, stains at the foot
            h = x if along == 'x' else -y
            c = C['mid'].lerp(C['light'], sm(cl01((z - 0.1) / 0.4)))
            c = c.lerp(C['low'], sm(cl01((-z - 0.05) / 0.45)))
            c = c.lerp(C['light'], 0.5 * sm(cl01((-h - 0.25) / 0.25)))
            c = c.lerp(C['right'], 0.6 * sm(cl01((h - 0.25) / 0.25)))
        v[col] = (c.x, c.y, c.z, 1.0)
        co = [x * size[0] + random.uniform(-jitter, jitter), y * size[1] + random.uniform(-jitter, jitter), (z + 0.5) * size[2] + random.uniform(-jitter, jitter) * 0.5]
        cc = (x, y, z)
        if sculpt and abs(cc[nax]) > 0.499:                                   # on a face: sculpt it
            a1, a2 = [j for j in range(3) if j != nax]; p, q = cc[a1], cc[a2]
            off = sum(h * math.exp(-((p - bp) ** 2 + (q - bq) ** 2) / (2 * br * br)) for (bp, bq, br, h) in bumps) * 0.0045
            e = min(0.5 - abs(p), 0.5 - abs(q)) * min(size[a1], size[a2])        # soft, pillowy edges
            off -= 0.004 * max(0.0, 1 - e / 0.05) ** 2
            for (cp, cq, cw) in chips:
                dd = math.hypot((p - cp) * size[a1], (q - cq) * size[a2])
                if dd < cw: off -= 0.012 * (1 - dd / cw) ** 1.5
            if crack:
                cp, cq, ang = crack
                dline = abs((p - cp) * size[a1] * math.sin(ang) - (q - cq) * size[a2] * math.cos(ang))
                if dline < 0.004 and abs(p - cp) < 0.35: off -= 0.004 * (1 - dline / 0.004)
            co[nax] += math.copysign(off, cc[nax])
        v.co = Vector(co)
    hide = -1 if along == 'top' else -face                                    # the face nobody sees (against the core, or
    if hide:                                                                  # underneath): drop it, it only costs triangles
        k = nax; lim = 0.49 * size[k] if k != 2 else 0.01 * size[2]
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if all((v.co[k] * hide > lim) if k != 2 else (v.co[2] < lim) for v in f.verts)], context='FACES')
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = _finish(name, me, color, loc, rot, parent, bevel, segs=2, **mk)
    o.data.materials[0] = mat_vc(color)
    return o

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
