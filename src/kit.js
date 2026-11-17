// Small building-block helpers shared by every world.
import * as THREE from 'three';

import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

export const uTime = { value: 0 };   // shared clock for shader animation (grass, etc.)

// Soft clay-like material: smooth shading plus a gentle rim of light around every silhouette.
function soften(m) {
  m.onBeforeCompile = (sh) => {
    sh.fragmentShader = sh.fragmentShader.replace('#include <opaque_fragment>',
      'float rimK = pow(1.0 - saturate(dot(normalize(vViewPosition), normal)), 2.6);\noutgoingLight += rimK * 0.26 * (diffuseColor.rgb * 0.55 + 0.45);\n#include <opaque_fragment>');
  };
  m.customProgramCacheKey = () => 'soft';
  return m;
}
const cache = new Map();
export function M(color, o) {
  if (color && color.isMaterial) return color;
  if (!o) {
    if (!cache.has(color)) cache.set(color, soften(new THREE.MeshStandardMaterial({ color, roughness: 0.95 })));
    return cache.get(color);
  }
  return soften(new THREE.MeshStandardMaterial({ color, roughness: 0.95, ...o }));
}
const flat = new Map();
const MF = (color) => { if (color && color.isMaterial) return color; if (!flat.has(color)) flat.set(color, soften(new THREE.MeshStandardMaterial({ color, roughness: 0.95, flatShading: true }))); return flat.get(color); };
// Unlit material brighter than 1.0 so the bloom pass picks it up.
export function glowM(color, k = 2) {
  const m = new THREE.MeshBasicMaterial({ color });
  m.color.multiplyScalar(k);
  return m;
}

function put(p, geo, mat, x, y, z) {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(x, y, z);
  p.add(m);
  return m;
}
// y is always the BOTTOM of the shape, so things stack naturally. Boxes get rounded edges.
export const box = (p, w, h, d, color, x, y, z, o) => put(p, new RoundedBoxGeometry(w, h, d, 2, Math.min(0.08, Math.min(w, h, d) * 0.32)), M(color, o), x, y + h / 2, z);
export const cyl = (p, rt, rb, h, color, x, y, z, seg = 12, o) => put(p, new THREE.CylinderGeometry(rt, rb, h, seg > 6 ? Math.max(seg, 20) : seg), seg > 6 || o ? M(color, o) : MF(color), x, y + h / 2, z);
export const cone = (p, r, h, color, x, y, z, seg = 8, o) => put(p, new THREE.ConeGeometry(r, h, seg > 6 ? Math.max(seg, 20) : seg), seg > 6 || o ? M(color, o) : MF(color), x, y + h / 2, z);
export const sph = (p, r, color, x, y, z, detail = 1, o) => put(p, new THREE.SphereGeometry(r, 22, 16), M(color, o), x, y, z);

// A soft round dot for particles (instead of square points).
let dot;
export function softDot() {
  if (dot) return dot;
  const c = document.createElement('canvas'); c.width = c.height = 64;
  const g = c.getContext('2d'), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.35, 'rgba(255,255,255,.75)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 64, 64);
  return (dot = new THREE.CanvasTexture(c));
}

// Fluffy, backlit cloud stuff. Also used for blossom and foliage.
export function cloudMat(lit, shade, edge, sun = [-0.5, 0.8, 0.4]) {
  return new THREE.ShaderMaterial({
    uniforms: { lit: { value: new THREE.Color(lit) }, shade: { value: new THREE.Color(shade) }, edge: { value: new THREE.Color(edge) }, sun: { value: new THREE.Vector3(...sun).normalize() } },
    vertexShader: 'varying vec3 vN, vW; void main(){ vN = normalize(mat3(modelMatrix)*normal); vec4 w = modelMatrix*vec4(position,1.); vW = w.xyz; gl_Position = projectionMatrix*viewMatrix*w; }',
    fragmentShader: `uniform vec3 lit, shade, edge, sun; varying vec3 vN, vW;
      void main(){ vec3 n = normalize(vN), v = normalize(cameraPosition - vW);
        float d = smoothstep(.2, .9, dot(n, sun)*.5+.5);
        float f = pow(1. - max(dot(n, v), 0.), 2.2);
        gl_FragColor = vec4(mix(mix(shade, lit, d), edge, f*.7), 1.); }`,
  });
}
export function cloud(p, mat, x, y, z, s = 1, n = 9) {
  const g = group(p, x, y, z);
  for (let i = 0; i < n; i++) {
    const k = i / (n - 1) - 0.5, r = (1 - Math.abs(k) * 1.3) * (2.2 + Math.random() * 1.4) * s;
    const m = new THREE.Mesh(new THREE.SphereGeometry(r, 20, 14), mat);
    m.position.set(k * 11 * s, r * 0.45 + Math.random() * s, (Math.random() - 0.5) * 3 * s); m.scale.y = 0.72;
    m.userData.noShadow = true; g.add(m);
  }
  return g;
}

// Grass that sways: an instanced blade whose tip bends with the wind.
export function windMat(color) {
  const m = new THREE.MeshStandardMaterial({ color, roughness: 1 });
  m.onBeforeCompile = (sh) => {
    sh.uniforms.uTime = uTime;
    sh.vertexShader = 'uniform float uTime;\n' + sh.vertexShader.replace('#include <begin_vertex>',
      '#include <begin_vertex>\nfloat bend = max(0., position.y + .25);\ntransformed.x += sin(uTime*1.7 + instanceMatrix[3].x*.6 + instanceMatrix[3].z*.4) * bend * bend * 1.1;\ntransformed.z += cos(uTime*1.3 + instanceMatrix[3].x*.3) * bend * bend * .5;');
  };
  return m;
}

export function group(p, x = 0, y = 0, z = 0, ry = 0) {
  const g = new THREE.Group();
  g.position.set(x, y, z);
  g.rotation.y = ry;
  p.add(g);
  return g;
}

// A flat sign with text drawn on a canvas. Faces +z by default.
export function sign(p, lines, w, h, x, y, z, o = {}) {
  const res = o.res || 128;
  const c = document.createElement('canvas');
  c.width = Math.round(w * res); c.height = Math.round(h * res);
  const g = c.getContext('2d');
  if (o.bg !== null) {
    g.fillStyle = o.bg || '#fbf6e9';
    g.fillRect(0, 0, c.width, c.height);
  }
  if (o.border) {
    g.strokeStyle = o.border; g.lineWidth = res * 0.06;
    g.strokeRect(res * 0.06, res * 0.06, c.width - res * 0.12, c.height - res * 0.12);
  }
  lines = [].concat(lines);
  const sizes = lines.map((l, i) => (Array.isArray(o.size) ? o.size[i] : o.size) || 0.3);
  const total = sizes.reduce((a, b) => a + b * 1.25, 0);
  let cy = (h - total) / 2;
  g.textAlign = 'center'; g.textBaseline = 'middle';
  lines.forEach((l, i) => {
    const px = sizes[i] * res;
    g.font = `${o.weight || 700} ${px}px ${o.font || '"Trebuchet MS", "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif'}`;
    g.fillStyle = (Array.isArray(o.fg) ? o.fg[i] : o.fg) || '#3b3a4a';
    g.fillText(l, c.width / 2, (cy + sizes[i] * 0.625) * res, c.width * 0.94);
    cy += sizes[i] * 1.25;
  });
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 4;
  const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: o.bg === null, side: o.double ? THREE.DoubleSide : THREE.FrontSide });
  if (o.glow) mat.color.multiplyScalar(o.glow);
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat);
  m.position.set(x, y, z);
  m.rotation.y = o.ry || 0;
  m.userData.noShadow = true;
  p.add(m);
  return m;
}

// A framed photo. Swap `src` for any picture in /photos.
export function photo(p, src, w, h, x, y, z, ry = 0) {
  const g = group(p, x, y, z, ry);
  box(g, w + 0.16, h + 0.16, 0.06, 0xf4ecd8, 0, -h / 2 - 0.08, -0.04);
  const tex = new THREE.TextureLoader().load(src);
  tex.colorSpace = THREE.SRGBColorSpace;
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tex }));
  m.userData.noShadow = true;
  g.add(m);
  return g;
}

export function sky(scene, top, mid, bottom, sun = null, sunCol = 0xfff2d0) {
  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { a: { value: new THREE.Color(top) }, b: { value: new THREE.Color(mid) }, c: { value: new THREE.Color(bottom) },
      sun: { value: new THREE.Vector3(...(sun || [0, -1, 0])).normalize() }, sc: { value: new THREE.Color(sunCol) }, sk: { value: sun ? 1 : 0 } },
    vertexShader: 'varying vec3 d; void main(){ d = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }',
    fragmentShader: `uniform vec3 a,b,c,sun,sc; uniform float sk; varying vec3 d;
      void main(){ vec3 n = normalize(d); float h = n.y;
        vec3 col = h>0. ? mix(b,a,pow(h,.55)) : mix(b,c,pow(-h,.4));
        float s = max(dot(n, sun), 0.);
        col += sc * sk * (pow(s, 6.)*.22 + pow(s, 60.)*.5 + smoothstep(.9985, .9993, s)*1.4);
        gl_FragColor = vec4(col,1.); }`,
  });
  const m = new THREE.Mesh(new THREE.SphereGeometry(450, 32, 20), mat);
  m.userData.noShadow = true;
  scene.add(m);
  return m;
}

export function stars(scene, n, rMin, rMax, size = 1.4, upperOnly = false) {
  const pos = new Float32Array(n * 3), col = new Float32Array(n * 3);
  const v = new THREE.Vector3(), c = new THREE.Color();
  for (let i = 0; i < n; i++) {
    v.randomDirection();
    if (upperOnly) v.y = Math.abs(v.y) * 0.9 + 0.05;
    v.normalize().multiplyScalar(rMin + Math.random() * (rMax - rMin));
    pos.set([v.x, v.y, v.z], i * 3);
    c.setHSL(0.55 + Math.random() * 0.2, 0.5, 0.75 + Math.random() * 0.25).multiplyScalar(0.8 + Math.random() * 1.6);
    col.set([c.r, c.g, c.b], i * 3);
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const pts = new THREE.Points(geo, new THREE.PointsMaterial({ size: size * 2.6, map: softDot(), vertexColors: true, sizeAttenuation: false, fog: false, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }));
  scene.add(pts);
  return pts;
}

export function plant(p, x, y, z, s = 1) {
  const g = group(p, x, y, z);
  cyl(g, 0.22 * s, 0.16 * s, 0.35 * s, 0xc97b5a, 0, 0, 0, 8);
  for (let i = 0; i < 5; i++) {
    const l = cone(g, 0.12 * s, 0.9 * s, 0x5fa46b, 0, 0.3 * s, 0, 5);
    l.rotation.set(0.35 + Math.random() * 0.3, 0, 0);
    l.rotation.y = (i / 5) * Math.PI * 2;
    l.rotateOnWorldAxis(new THREE.Vector3(0, 1, 0), (i / 5) * Math.PI * 2);
  }
  return g;
}

// The dimension crack: a jagged glowing tear. setOpen(0..1) animates it.
export function makeCrack(color = 0xffffff) {
  const g = new THREE.Group();
  const H = 5, N = 14, L = [], R = [];
  for (let i = 0; i <= N; i++) {
    const k = i / N, wdt = Math.pow(Math.sin(Math.PI * k), 0.7) * (0.75 + Math.random() * 0.6);
    const cx = (i % 2 ? 0.28 : -0.28) * Math.sin(Math.PI * k) + (Math.random() - 0.5) * 0.2;
    L.push(new THREE.Vector2(cx - wdt, k * H)); R.push(new THREE.Vector2(cx + wdt, k * H));
  }
  const shape = new THREE.Shape([...L, ...R.reverse()]);
  const edge = new THREE.Mesh(new THREE.ShapeGeometry(shape), new THREE.MeshBasicMaterial({ side: THREE.DoubleSide }));
  const innerGeo = new THREE.ShapeGeometry(shape);
  const uv = innerGeo.attributes.uv;
  for (let i = 0; i < uv.count; i++) uv.setXY(i, (uv.getX(i) + 1.6) / 3.2, uv.getY(i) / H);
  const cv = document.createElement('canvas'); cv.width = 64; cv.height = 128;
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
  const inner = new THREE.Mesh(innerGeo, new THREE.MeshBasicMaterial({ map: tex, side: THREE.DoubleSide }));
  inner.scale.set(0.82, 0.94, 1); inner.position.set(0, H * 0.03, 0.02);
  const inner2 = inner.clone(); inner2.position.z = -0.02;
  g.add(edge, inner, inner2);
  const shards = [];
  for (let i = 0; i < 16; i++) {
    const s = 0.1 + Math.random() * 0.25;
    const geo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(-s, 0, 0), new THREE.Vector3(s, s * 0.4, 0), new THREE.Vector3(0, s * 1.6, 0)]);
    const m = new THREE.Mesh(geo, edge.material);
    m.userData = { a: Math.random() * 6.28, r: 1.2 + Math.random() * 1.8, y: 0.4 + Math.random() * 4.4, sp: 0.3 + Math.random() };
    g.add(m); shards.push(m);
  }
  g.traverse((o) => { o.userData.noShadow = true; });
  let open = 1;
  g.setColor = (hex) => {
    const c = new THREE.Color(hex);
    edge.material.color.copy(c).multiplyScalar(1.5);
    const x = cv.getContext('2d'), gr = x.createLinearGradient(0, 0, 0, 128);
    gr.addColorStop(0, '#0a0b1e'); gr.addColorStop(0.55, '#' + c.clone().multiplyScalar(0.55).getHexString()); gr.addColorStop(1, '#ffffff');
    x.fillStyle = gr; x.fillRect(0, 0, 64, 128);
    x.fillStyle = '#fff';
    for (let i = 0; i < 40; i++) x.fillRect(Math.random() * 64, Math.random() * 90, 1.2, 1.2);
    tex.needsUpdate = true;
  };
  g.setOpen = (k) => { open = k; g.visible = k > 0.001; };
  // show a live view of the destination inside the crack (or null for the plain gradient)
  g.setPortal = (tx) => { inner.material.map = tx || tex; inner.material.needsUpdate = true; };
  g.tick = (t) => {
    // first 30%: a hairline climbs upward. the rest: it bursts open with a little overshoot.
    const line = Math.min(1, open / 0.3), wide = Math.max(0, (open - 0.3) / 0.7);
    const eb = wide <= 0 ? 0 : 1 + 2.70158 * Math.pow(wide - 1, 3) + 1.70158 * Math.pow(wide - 1, 2);
    g.scale.set(0.03 + eb * (0.97 + Math.sin(t * 3) * 0.04), 0.04 + 0.96 * (1 - Math.pow(1 - line, 3)), 1);
    for (const m of shards) {
      const u = m.userData, a = u.a + t * u.sp * 0.4;
      m.visible = wide > 0;
      m.position.set(Math.cos(a) * u.r * (0.2 + 0.8 * eb), u.y + Math.sin(t * u.sp + u.a) * 0.3, Math.sin(a) * 0.5);
      m.rotation.set(t * u.sp, t * u.sp * 0.7, u.a);
    }
  };
  g.setColor(color); g.setOpen(1);
  return g;
}

// World container: scene + collision + interactive hotspots.
export function makeWorld(name, title) {
  const scene = new THREE.Scene();
  const w = {
    name, title, scene, solids: [], hots: [], ticks: [],
    spawn: new THREE.Vector3(), spawnYaw: Math.PI, groundY: 0,
    cam: { dist: 11, pitch: 0.7, yaw: 0.5 }, bloom: 0.5, sun: null,
    inside: () => true,
    solid(x, z, sx, sz) { w.solids.push({ x0: x - sx / 2, x1: x + sx / 2, z0: z - sz / 2, z1: z + sz / 2 }); },
    canWalk(x, z) {
      if (!w.inside(x, z)) return false;
      const r = 0.32;
      for (const s of w.solids) if (x > s.x0 - r && x < s.x1 + r && z > s.z0 - r && z < s.z1 + r) return false;
      return true;
    },
    // A hotspot: walk near it and press E. `action` is a content key or a function.
    hot(x, z, label, action, o = {}) {
      // a soft floating light marks things you can interact with
      const mark = new THREE.Sprite(new THREE.SpriteMaterial({ map: softDot(), color: new THREE.Color(o.color || 0xffe08a).multiplyScalar(1.15), blending: THREE.AdditiveBlending, depthWrite: false }));
      mark.scale.setScalar(0.5);
      mark.position.set(x, (o.y || 2.2) + w.groundY, z);
      mark.userData.noShadow = true;
      scene.add(mark);
      const h = { x, z, label, action, r: o.r || 1.9, mark, baseY: mark.position.y };
      w.hots.push(h);
      return h;
    },
    sunlight(color, intensity, x, y, z) {
      const d = new THREE.DirectionalLight(color, intensity);
      d.userData.offset = new THREE.Vector3(x, y, z);
      d.castShadow = true;
      d.shadow.mapSize.set(2048, 2048);
      const c = d.shadow.camera; c.left = c.bottom = -22; c.right = c.top = 22; c.near = 1; c.far = 80;
      d.shadow.bias = -0.0004; d.shadow.normalBias = 0.03;
      scene.add(d, d.target);
      w.sun = d;
      return d;
    },
    finish() {
      scene.traverse((o) => {
        if (o.isMesh && !o.userData.noShadow && !o.material.isMeshBasicMaterial && !o.material.isShaderMaterial && !o.material.transparent) {
          o.castShadow = true; o.receiveShadow = true;
        }
      });
      return w;
    },
    update(t, dt) {
      for (const h of w.hots) { h.mark.position.y = h.baseY + Math.sin(t * 2 + h.x) * 0.12; h.mark.scale.setScalar(0.45 + Math.sin(t * 3 + h.z) * 0.08); }
      for (const f of w.ticks) f(t, dt);
    },
  };
  return w;
}
