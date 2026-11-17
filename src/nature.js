// Organic, hand-painted-looking nature: lumpy rocks, twisted trees, curved grass, flowers.
// Shapes are sculpted with noise; colour is painted per vertex (light on top, dark underneath, streaks).
import * as THREE from 'three';
import { M, group, uTime } from './kit.js';

const C = (h) => new THREE.Color(h);
const hash = (x, y, z) => { const s = Math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453; return s - Math.floor(s); };
function noise(x, y, z) {
  const ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z), fx = x - ix, fy = y - iy, fz = z - iz;
  const s = (t) => t * t * (3 - 2 * t), ux = s(fx), uy = s(fy), uz = s(fz), L = THREE.MathUtils.lerp;
  const h = (a, b, c) => hash(ix + a, iy + b, iz + c);
  return L(L(L(h(0, 0, 0), h(1, 0, 0), ux), L(h(0, 1, 0), h(1, 1, 0), ux), uy), L(L(h(0, 0, 1), h(1, 0, 1), ux), L(h(0, 1, 1), h(1, 1, 1), ux), uy), uz);
}
const paint = () => M(0xffffff, { vertexColors: true });
function colorize(geo, fn) {
  const p = geo.attributes.position, col = new Float32Array(p.count * 3), c = new THREE.Color();
  for (let i = 0; i < p.count; i++) { fn(c, p.getX(i), p.getY(i), p.getZ(i), i); col.set([c.r, c.g, c.b], i * 3); }
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
}

// A lumpy blob: used for rocks and for tree canopies.
export function blob(p, x, y, z, s, dark, light, o = {}) {
  const seed = Math.random() * 100, geo = new THREE.SphereGeometry(1, 30, 22), pos = geo.attributes.position, v = new THREE.Vector3();
  const sq = o.squash || [1, 0.75, 1], lump = o.lump ?? 0.35;
  for (let i = 0; i < pos.count; i++) {
    v.fromBufferAttribute(pos, i);
    const n = noise(v.x * 1.6 + seed, v.y * 1.6, v.z * 1.6) + noise(v.x * 3.7, v.y * 3.7 + seed, v.z * 3.7) * 0.4;
    v.multiplyScalar(1 + (n - 0.7) * lump);
    if (o.chisel) for (let k = 0; k < 5; k++) {                       // flat chiselled faces, like a carved rock
      const a = hash(seed, k, 1) * 6.28, b = hash(seed, k, 2) * 1.4 - 0.3, nx = Math.cos(a) * Math.cos(b), ny = Math.sin(b), nz = Math.sin(a) * Math.cos(b);
      const d = v.x * nx + v.y * ny + v.z * nz - 0.78; if (d > 0) v.addScaledVector(new THREE.Vector3(nx, ny, nz), -d * 0.85);
    }
    pos.setXYZ(i, v.x * sq[0], v.y * sq[1], v.z * sq[2]);
  }
  geo.computeVertexNormals();
  const cd = C(dark), cl = C(light);
  colorize(geo, (c, px, py, pz) => {
    const k = THREE.MathUtils.smoothstep(py / sq[1], -0.7, 0.9), n = noise(px * 4 + seed, py * 4, pz * 4);
    c.lerpColors(cd, cl, THREE.MathUtils.clamp(k * 0.85 + (n - 0.5) * 0.45, 0, 1));
  });
  const m = new THREE.Mesh(geo, paint());
  m.position.set(x, y, z); m.scale.setScalar(s); m.rotation.y = seed; p.add(m);
  return m;
}
export const rock = (p, x, y, z, s, dark = 0x6f6a78, light = 0xd9cfc4) => blob(p, x, y + s * 0.45, z, s, dark, light, { chisel: true, lump: 0.25, squash: [1.15, 0.72, 0.95] });

// A twisted, ropey trunk that tapers along a curve, with painted grain. Returns the tip position(s).
export function trunk(p, pts, r0, r1, dark = 0x8a4a22, light = 0xf0a54a) {
  const curve = new THREE.CatmullRomCurve3(pts.map((a) => new THREE.Vector3(...a)));
  const T = 48, R = 14, geo = new THREE.TubeGeometry(curve, T, 1, R, false), pos = geo.attributes.position, v = new THREE.Vector3(), c0 = new THREE.Vector3();
  const grain = [];
  for (let i = 0; i <= T; i++) {
    const k = i / T; curve.getPointAt(k, c0);
    const rad = THREE.MathUtils.lerp(r0, r1, Math.pow(k, 0.8)) * (1 + Math.pow(1 - k, 6) * 0.9);     // flare at the roots
    for (let j = 0; j <= R; j++) {
      const idx = i * (R + 1) + j, a = (j / R) * 6.283;
      const g = Math.sin(a * 3 + k * 9) * 0.5 + 0.5;                                               // spiral ridges = the twist
      v.fromBufferAttribute(pos, idx).sub(c0).multiplyScalar(rad * (0.86 + g * 0.24)).add(c0);
      pos.setXYZ(idx, v.x, v.y, v.z); grain[idx] = g;
    }
  }
  geo.computeVertexNormals();
  const cd = C(dark), cl = C(light);
  colorize(geo, (c, x, y, z, i) => { c.lerpColors(cd, cl, THREE.MathUtils.clamp(grain[i] * 0.8 + noise(x * 5, y * 5, z * 5) * 0.3, 0, 1)); });
  const m = new THREE.Mesh(geo, paint()); p.add(m);
  return curve.getPointAt(1);
}

// A whole twisted tree: curling trunk, a side branch, lumpy canopies.
export function twistedTree(p, x, y, z, s = 1, o = {}) {
  const g = group(p, x, y, z, o.ry || 0); g.scale.setScalar(s);
  const lean = o.lean ?? 1, [cd, cl] = o.leaf || [0x2f6f55, 0x7fcf8f];
  const tip = trunk(g, [[0, -0.1, 0], [0.5 * lean, 0.7, 0.1], [-0.2 * lean, 1.5, -0.2], [0.5 * lean, 2.3, 0.1], [0.2 * lean, 3.1, 0]], 0.42, 0.12, o.dark, o.light);
  const tip2 = trunk(g, [[0.25 * lean, 1.0, 0], [-0.6 * lean, 1.5, 0.3], [-1.1 * lean, 2.2, 0.2], [-1.0 * lean, 2.8, 0.1]], 0.2, 0.07, o.dark, o.light);
  const puff = (t, r) => { for (let i = 0; i < 3; i++) blob(g, t.x + (i - 1) * r * 0.6, t.y + r * 0.45 + (i % 2) * r * 0.3, t.z + (i - 1) * 0.2, r * (1 - Math.abs(i - 1) * 0.25), cd, cl, { lump: 0.45, squash: [1.1, 0.8, 1] }); };
  puff(tip, o.canopy || 1.1); puff(tip2, (o.canopy || 1.1) * 0.62);
  return g;
}

// Curved grass blades that sway. Scatter with `place(x, y, z, scale)`.
export function grass(p, count, dark = 0x2f8f58, light = 0xa6e27a) {
  const geo = new THREE.PlaneGeometry(0.16, 1, 2, 6), pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const k = pos.getY(i) + 0.5;
    pos.setXYZ(i, pos.getX(i) * (1 - k * k * 0.95), k, k * k * 0.35 + Math.abs(pos.getX(i)) * -0.25);   // taper, lean, slight fold
  }
  geo.computeVertexNormals();
  const cd = C(dark), cl = C(light);
  colorize(geo, (c, x, y) => c.lerpColors(cd, cl, y));
  const mat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 1, side: THREE.DoubleSide });
  mat.onBeforeCompile = (sh) => {
    sh.uniforms.uTime = uTime;
    sh.vertexShader = 'uniform float uTime;\n' + sh.vertexShader.replace('#include <begin_vertex>',
      '#include <begin_vertex>\nfloat bend = position.y * position.y;\ntransformed.x += sin(uTime*1.6 + instanceMatrix[3].x*.7 + instanceMatrix[3].z*.5) * bend * .3;\ntransformed.z += cos(uTime*1.2 + instanceMatrix[3].z*.6) * bend * .18;');
  };
  const mesh = new THREE.InstancedMesh(geo, mat, count); mesh.count = 0; mesh.receiveShadow = true; mesh.userData.noShadow = true; p.add(mesh);
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), sc = new THREE.Vector3(), ps = new THREE.Vector3();
  mesh.clump = (x, y, z, s = 1, n = 6) => {
    for (let i = 0; i < n && mesh.count < count; i++) {
      const h = s * (0.45 + Math.random() * 0.75);
      q.setFromEuler(e.set((Math.random() - 0.5) * 0.5, Math.random() * 6.28, (Math.random() - 0.5) * 0.5, 'YXZ'));
      m4.compose(ps.set(x + (Math.random() - 0.5) * 0.3 * s, y, z + (Math.random() - 0.5) * 0.3 * s), q, sc.set(s * 1.3, h, s * 1.3));
      mesh.setMatrixAt(mesh.count++, m4);
    }
    mesh.instanceMatrix.needsUpdate = true;
  };
  return mesh;
}

// A little flower on a bent stem.
export function flower(p, x, y, z, s = 1, petal = 0xffffff, heart = 0xffc93c) {
  const g = group(p, x, y, z, Math.random() * 6.28); g.scale.setScalar(s);
  const curve = new THREE.CatmullRomCurve3([new THREE.Vector3(0, 0, 0), new THREE.Vector3(0.05, 0.25, 0), new THREE.Vector3(0.14, 0.5, 0)]);
  g.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 8, 0.014, 6), M(0x5fae5a)));
  const head = group(g, 0.14, 0.5, 0); head.rotation.z = -0.5;
  const pg = new THREE.SphereGeometry(0.06, 10, 8);
  for (let i = 0; i < 7; i++) { const m = new THREE.Mesh(pg, M(petal)); const a = (i / 7) * 6.283; m.position.set(Math.cos(a) * 0.075, 0, Math.sin(a) * 0.075); m.scale.set(1, 0.25, 0.6); m.rotation.y = -a; head.add(m); }
  const c = new THREE.Mesh(new THREE.SphereGeometry(0.045, 10, 8), M(heart)); c.scale.y = 0.6; c.position.y = 0.015; head.add(c);
  const leaf = new THREE.Mesh(pg, M(0x5fae5a)); leaf.scale.set(1.3, 0.2, 0.5); leaf.position.set(-0.05, 0.14, 0); leaf.rotation.z = 0.7; g.add(leaf);
  return g;
}

// A soft painted mound of ground with a flat walkable top.
export function mound(p, x, y, z, rTop, h, top = 0x7ccf78, side = 0x3f9a6a, base = 0xe9dcb4) {
  const pr = [[0.001, h], [rTop * 0.6, h], [rTop, h], [rTop + 0.35, h - 0.06], [rTop + 0.8, h - 0.25], [rTop + 1.3, h * 0.2], [rTop + 2.0, -0.12], [rTop + 2.6, -0.3]];
  const geo = new THREE.LatheGeometry(pr.reverse().map(([r, yy]) => new THREE.Vector2(r, yy)), 56), pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) { const px = pos.getX(i), pz = pos.getZ(i), r = Math.hypot(px, pz); if (r > rTop) { const k = 1 + (noise(px * 0.5, 0, pz * 0.5) - 0.5) * 0.14; pos.setX(i, px * k); pos.setZ(i, pz * k); } }
  geo.computeVertexNormals();
  const ct = C(top), cs = C(side), cb = C(base), dk = C(top).multiplyScalar(0.8);
  colorize(geo, (c, px, py, pz) => {
    if (py >= h - 0.001) c.lerpColors(dk, ct, THREE.MathUtils.clamp(noise(px * 0.45 + 9, 0, pz * 0.45) * 1.5 - 0.2, 0, 1));
    else if (py > h * 0.25) c.lerpColors(cs, ct, (py - h * 0.25) / (h * 0.75));
    else c.lerpColors(cb, cs, THREE.MathUtils.clamp(py / (h * 0.25), 0, 1) * 0.5);
  });
  const m = new THREE.Mesh(geo, paint()); m.position.set(x, y, z); p.add(m);
  return m;
}
