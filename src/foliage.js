// Painted foliage. A canopy from Blender is a few lumpy blobs; here each one is covered in "leaf cards": small images of
// painted leaf clusters, turned outward and lit as if the whole canopy were one soft round shape. That gives the
// Ghibli look: big masses of light and shade with leafy, broken edges. The cards flutter a little in the wind.
import * as THREE from 'three';
import { uTime } from './kit.js';
import { rimPatch } from './models.js';

function rng(seed) { return () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }; }

// A cluster of pointed leaves on a transparent background, painted in light greys so each card's own colour shows through.
function leafTexture(kind) {
  const S = 256, c = document.createElement('canvas'); c.width = c.height = S;
  const g = c.getContext('2d'), r = rng(kind === 'pine' ? 77 : 31);
  const leaf = (x, y, len, wid, a, shade) => {
    const dx = Math.cos(a), dy = Math.sin(a), nx = -dy, ny = dx, tx = x + dx * len, ty = y + dy * len, mx = x + dx * len * 0.45, my = y + dy * len * 0.45;
    const v = Math.round(185 + shade * 70);
    g.fillStyle = `rgb(${v},${v},${v})`; g.beginPath(); g.moveTo(x, y);
    g.quadraticCurveTo(mx + nx * wid, my + ny * wid, tx, ty); g.quadraticCurveTo(mx - nx * wid, my - ny * wid, x, y); g.fill();
    g.strokeStyle = `rgba(90,90,90,0.35)`; g.lineWidth = 1; g.beginPath(); g.moveTo(x, y); g.lineTo(x + dx * len * 0.8, y + dy * len * 0.8); g.stroke();
  };
  const n = kind === 'pine' ? 70 : 34;
  for (let i = 0; i < n; i++) {                                   // back to front: darker leaves inside, lighter on top
    const k = i / n, a = r() * 6.283, d = (1 - k * 0.6) * 74 * Math.sqrt(r());
    const x = S / 2 + Math.cos(a) * d * 0.9, y = S / 2 + Math.sin(a) * d * 0.9 + 6;
    if (kind === 'pine') leaf(x, y, 34 + r() * 30, 3.5 + r() * 2, a + (r() - 0.5) * 0.5, k * 0.8 + r() * 0.2);
    else leaf(x, y, 30 + r() * 26, 10 + r() * 8, a + (r() - 0.5) * 0.8, k * 0.8 + r() * 0.2);
  }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4;
  return t;
}
const textures = {};
const tex = (kind) => textures[kind] || (textures[kind] = leafTexture(kind));

// Colours from cool shade at the bottom of a canopy to warm sunlit yellow-green at the top.
const TONES = ['#2a5e45', '#33704a', '#3f864c', '#559c4e', '#74b452', '#9bcb5c', '#c8e27a'].map((h) => new THREE.Color(h));
const PINE_TONES = ['#1f5242', '#286247', '#33754b', '#44894e', '#5c9e52', '#7fb65a'].map((h) => new THREE.Color(h));

const mats = {};
function cardMaterial(kind, ramp) {
  if (mats[kind]) return mats[kind];
  const m = new THREE.MeshToonMaterial({ map: tex(kind), alphaTest: 0.5, side: THREE.DoubleSide, vertexColors: true, gradientMap: ramp });
  m.onBeforeCompile = (sh) => {
    sh.uniforms.uTime = uTime;
    sh.vertexShader = 'uniform float uTime;\nattribute float sway;\n' + sh.vertexShader.replace('#include <begin_vertex>', `#include <begin_vertex>
      vec4 wp0 = modelMatrix * vec4(position, 1.0);
      float ph = wp0.x * 0.7 + wp0.z * 0.5 + sway * 6.28;
      transformed += vec3(sin(uTime * 1.6 + ph), sin(uTime * 2.1 + ph * 1.3) * 0.5, cos(uTime * 1.3 + ph)) * 0.05 * sway;`);
    rimPatch(sh);
  };
  m.customProgramCacheKey = () => 'leaves-' + kind;
  return (mats[kind] = m);
}

// Split points into separate clumps (bushes on an islet, shrubs in a row of planters): points closer than `gap` join up.
function clusters(pts, gap) {
  const cell = new Map(), key = (p) => `${Math.floor(p.x / gap)},${Math.floor(p.y / gap)},${Math.floor(p.z / gap)}`;
  for (const p of pts) { const k = key(p); if (!cell.has(k)) cell.set(k, []); cell.get(k).push(p); }
  const seen = new Set(), out = [];
  for (const start of cell.keys()) {
    if (seen.has(start)) continue;
    const group = [], stack = [start]; seen.add(start);
    while (stack.length) {
      const k = stack.pop(); group.push(...cell.get(k));
      const [x, y, z] = k.split(',').map(Number);
      for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) {
        const n = `${x + dx},${y + dy},${z + dz}`; if (cell.has(n) && !seen.has(n)) { seen.add(n); stack.push(n); }
      }
    }
    out.push(group);
  }
  return out;
}

const SETTINGS = {
  broad: { size: 1.25, density: 10, max: 900, shell: 0.72, offset: 0.32 },
  pine: { size: 0.9, density: 12, max: 900, shell: 0, offset: 0.32 },
  bush: { size: 0.62, density: 22, max: 220, shell: 0.6, offset: 0.25 },
};

/**
 * Cover the leafy parts of a loaded model with leaf cards.
 * `isCanopy(material)` says which parts are leaves. The original blobs stay inside, darkened, so gaps between cards show
 * deep shade rather than sky. With `clumps`, each separate clump (a bush) gets its own round lighting.
 */
export function leafify(model, kind, isCanopy, ramp, { clumps = false } = {}) {
  model.updateMatrixWorld(true);
  const all = [], v = new THREE.Vector3(), blobs = [];
  model.traverse((o) => {
    if (!o.isMesh || !isCanopy(o.material)) return;
    blobs.push(o);
    const p = o.geometry.attributes.position, step = Math.max(1, Math.floor(p.count / (clumps ? 4000 : 900)));
    for (let i = 0; i < p.count; i += step) all.push(v.fromBufferAttribute(p, i).applyMatrix4(o.matrixWorld).clone());
  });
  if (!all.length) return null;
  for (const o of blobs) { o.material = o.material.clone(); o.material.color.multiplyScalar(0.62); o.castShadow = true; }   // the dark heart

  const cfg = SETTINGS[kind], tones = kind === 'pine' ? PINE_TONES : TONES;
  const pos = [], nor = [], uv = [], col = [], sway = [], idx = [];
  const groups = clumps ? clusters(all, 0.45) : [all];
  for (const pts of groups) {
    if (pts.length < 12) continue;
    const box = new THREE.Box3().setFromPoints(pts);
    addCards(pts, box, kind, cfg, tones, { pos, nor, uv, col, sway, idx });
  }
  if (!pos.length) return null;
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
  g.setAttribute('sway', new THREE.Float32BufferAttribute(sway, 1)); g.setIndex(idx);
  const cards = new THREE.Mesh(g, cardMaterial(kind === 'bush' ? 'broad' : kind, ramp));
  cards.castShadow = false; cards.receiveShadow = true; cards.name = 'leaf_cards';
  model.add(cards);
  return cards;
}

function addCards(pts0, box, kind, cfg, tones, out) {
  let pts = pts0;
  const center = box.getCenter(new THREE.Vector3()), size = box.getSize(new THREE.Vector3()).max(new THREE.Vector3(0.05, 0.05, 0.05));
  // keep only points on the outer shell, so the cards sit on the outside, not inside other blobs (and not under a bush)
  const half = size.clone().multiplyScalar(0.5), shell = pts.filter((q) => {
    const d = q.clone().sub(center).divide(half);
    if (kind === 'bush' && d.y < -0.55) return false;
    return kind === 'pine' ? Math.hypot(d.x, d.z) > 0.55 - 0.35 * d.y : d.length() > cfg.shell;
  });
  if (shell.length > 12) pts = shell;
  const r = rng(Math.round(Math.abs(center.x) * 100 + Math.abs(center.z) * 37 + size.y * 1000) + 7);
  const count = Math.min(cfg.max, Math.max(12, Math.round((size.x * size.z + size.y * size.x) * cfg.density)));
  const n = new THREE.Vector3(), t1 = new THREE.Vector3(), t2 = new THREE.Vector3(), up = new THREE.Vector3(0, 1, 0), corner = new THREE.Vector3();
  const scale = kind === 'bush' ? THREE.MathUtils.clamp(size.y * 1.1, 0.45, 1.1) : Math.max(0.6, size.y / 6);
  for (let c = 0; c < count; c++) {
    const p = pts[Math.floor(r() * pts.length)];
    if (kind === 'pine') n.set(p.x - center.x, 0.45 * size.x / size.y, p.z - center.z).normalize();
    else n.copy(p).sub(center).multiply(new THREE.Vector3(1 / size.x, 1 / size.y, 1 / size.z)).normalize();
    const s = cfg.size * (0.75 + r() * 0.5) * scale;
    const at = p.clone().addScaledVector(n, s * cfg.offset);
    t1.crossVectors(Math.abs(n.y) > 0.9 ? new THREE.Vector3(1, 0, 0) : up, n).normalize(); t2.crossVectors(n, t1);
    const spin = r() * 6.283, cs = Math.cos(spin), sn = Math.sin(spin);
    const a = t1.clone().multiplyScalar(cs).addScaledVector(t2, sn), b = t1.clone().multiplyScalar(-sn).addScaledVector(t2, cs);
    a.addScaledVector(n, (r() - 0.5) * 0.6).normalize();                     // tilt a little off the surface for depth
    const h = THREE.MathUtils.clamp((p.y - box.min.y) / size.y + (n.y * 0.25) + (r() - 0.5) * 0.3, 0, 0.999);
    const tone = tones[Math.floor(h * tones.length)];
    const base = out.pos.length / 3;
    for (const [u, w] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) {
      corner.copy(at).addScaledVector(a, u * s / 2).addScaledVector(b, w * s / 2);
      out.pos.push(corner.x, corner.y, corner.z);
      const cn = corner.clone().sub(center).normalize().lerp(n, 0.5).normalize();   // soft, round lighting across the clump
      out.nor.push(cn.x, cn.y, cn.z); out.uv.push((u + 1) / 2, (w + 1) / 2); out.col.push(tone.r, tone.g, tone.b);
      out.sway.push(0.3 + r() * 0.7);
    }
    out.idx.push(base, base + 1, base + 2, base, base + 2, base + 3);
  }
}
