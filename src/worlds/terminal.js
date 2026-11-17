// The terminal: a little country station on a railway that runs just under the sea.
// The station itself is built in Blender (models/terminal); this file adds what moves: water, sky, clouds, the train, the cutscene.
import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { makeWorld, sky, stars, cloud, cloudMat, softDot, makeCrack, sign } from '../kit.js';
import { blob } from '../nature.js';
import { loadLayout, gradient } from '../models.js';
import { leafify } from '../foliage.js';
import { painted } from '../paint.js';

export const DEST = {
  home: { color: 0x8fb4ff, name: 'Home among the stars' },
  office: { color: 0xffd27a, name: 'The Office' },
  market: { color: 0xff7aa8, name: 'The Night Market' },
};

const B = (x, y, z = 0) => new THREE.Vector3(x, z, -y);       // Blender (x right, y away, z up) -> three
const PZ = 0.95, TRACK = -3.2;                                   // platform height; the line (Blender y)

// ---------- time of day: the sky follows the visitor's clock (or ?time=HH) ----------
const NUMBERS = new Set(['sunI', 'hemiI', 'lamps', 'stars', 'glow', 'bloom']);                // everything else in a palette is a colour
const pal = (o) => Object.fromEntries(Object.entries(o).map(([k, v]) => [k, NUMBERS.has(k) ? v : new THREE.Color(v)]));
const NIGHT = pal({ top: 0x070b24, mid: 0x1b2552, bot: 0x0e1638, sun: 0x8fa8ff, sunI: 0.45, sky: 0x3a4a80, ground: 0x182030, hemiI: 0.55, fog: 0x18214a, shallow: 0x1d5a6e, deep: 0x07142e, lamps: 1, cLit: 0x5d68a0, cShade: 0x20264a, cEdge: 0x8c96cc, stars: 1, glow: 0.45, bloom: 0.75 });
const DAWN = pal({ top: 0x4a6fb0, mid: 0xffc2a0, bot: 0x8aa0c8, sun: 0xffb38a, sunI: 1.3, sky: 0xd8c8e8, ground: 0x8a9a78, hemiI: 1.0, fog: 0xf0c8b8, shallow: 0x7cc4c4, deep: 0x245a80, lamps: 0.5, cLit: 0xffe2d2, cShade: 0x9890c4, cEdge: 0xffd0b4, stars: 0.15, glow: 0.3, bloom: 0.45 });
const DAY = pal({ top: 0x2f86e0, mid: 0xbfe4f3, bot: 0xbfe4ea, sun: 0xfff2d6, sunI: 3.0, sky: 0xb4d4f4, ground: 0x8a9c8c, hemiI: 1.2, fog: 0xd2ecf2, shallow: 0x5fd0c8, deep: 0x17639a, lamps: 0, cLit: 0xffffff, cShade: 0xb4cbe6, cEdge: 0xffffff, stars: 0, glow: 0.2, bloom: 0.3 });
const DUSK = pal({ top: 0x232a5c, mid: 0xf6b3a0, bot: 0x7a86b4, sun: 0xffa070, sunI: 1.5, sky: 0xc8a8c8, ground: 0x6a6a7a, hemiI: 0.95, fog: 0xe8b9b0, shallow: 0x6aa8b4, deep: 0x1a3c6a, lamps: 1, cLit: 0xffd9c4, cShade: 0x8a7bb0, cEdge: 0xffc4a0, stars: 0.1, glow: 0.6, bloom: 0.55 });
const KEYS = [[0, NIGHT], [5.2, NIGHT], [6.5, DAWN], [8.5, DAY], [16.4, DAY], [18.2, DUSK], [19.7, NIGHT], [24, NIGHT]];
function mixPal(out, a, b, k) {
  for (const key in a) out[key] = a[key].isColor ? (out[key] || new THREE.Color()).lerpColors(a[key], b[key], k) : a[key] + (b[key] - a[key]) * k;
  return out;
}
function paletteAt(h, out) {
  let i = 0; while (h > KEYS[i + 1][0]) i++;
  const [h0, a] = KEYS[i], [h1, b] = KEYS[i + 1];
  return mixPal(out, a, b, (h - h0) / (h1 - h0));
}
function sunDir(h, out) {                                        // the sun by day, the moon by night, both over the sea (south)
  const day = h >= 6 && h < 18.4, t = day ? (h - 6) / 12.4 : ((h + 24 - 18.4) % 24) / 11.6;
  const az = -1.25 + 2.5 * t, el = 0.16 + Math.sin(Math.PI * t) * (day ? 0.95 : 0.7);
  return out.set(Math.sin(az) * Math.cos(el), Math.sin(el), Math.cos(az) * Math.cos(el)).normalize();
}
const forced = parseFloat(new URLSearchParams(location.search).get('time'));
const hourNow = () => { if (!isNaN(forced)) return ((forced % 24) + 24) % 24; const d = new Date(); return d.getHours() + d.getMinutes() / 60; };

// ---------- the sea floor: shallow banks under the line, the station and the islets, deep water beyond ----------
function seaDepth(bx, by, islets) {
  let d = Math.abs(by - TRACK) - 2.2;
  d = Math.min(d, Math.max(-11 - bx, bx - 35, -2.5 - by, by - 11.5, 0) - 1.0);
  for (const [ix, iy, ir] of islets) d = Math.min(d, Math.hypot(bx - ix, by - iy) - ir * 1.15);
  let k = Math.min(1, Math.max(0, d / 8)); k = k * k * (3 - 2 * k);
  return 0.42 + 3.4 * k - Math.sin(bx * 0.7) * Math.cos(by * 0.9) * 0.05;
}
const DEPTH_GLSL = `
uniform vec3 uIslets[16];
float seaDepth(vec2 b) {
  float d = abs(b.y - (${TRACK.toFixed(1)})) - 2.2;
  d = min(d, max(max(max(-11.0 - b.x, b.x - 35.0), max(-2.5 - b.y, b.y - 11.5)), 0.0) - 1.0);
  for (int i = 0; i < 16; i++) d = min(d, length(b - uIslets[i].xy) - uIslets[i].z * 1.15);
  float k = clamp(d / 8.0, 0.0, 1.0); k = k * k * (3.0 - 2.0 * k);
  return 0.42 + 3.4 * k - sin(b.x * 0.7) * cos(b.y * 0.9) * 0.05;
}`;

function makeWater(U) {
  const m = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.14, metalness: 0, transparent: true, depthWrite: false });
  m.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, U);
    sh.vertexShader = 'varying vec3 vW;\n' + sh.vertexShader.replace('#include <project_vertex>', '#include <project_vertex>\nvW = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    sh.fragmentShader = 'varying vec3 vW;\nuniform float uTime;\nuniform vec3 uShallow, uDeep, uSky, uTrain;\n' + DEPTH_GLSL + '\n' + sh.fragmentShader
      .replace('#include <color_fragment>', `#include <color_fragment>
        vec2 bp = vec2(vW.x, -vW.z);
        float dep = seaDepth(bp);
        float murk = 1.0 - exp(-dep * 0.85);                     // the deeper, the darker and less see-through
        diffuseColor.rgb = mix(uShallow, uDeep, murk);
        diffuseColor.a = mix(0.36, 1.0, smoothstep(0.0, 0.95, murk));
        // the train pushes a bow wave and leaves a wake; both grow with its speed (uTrain = front x, speed 0..1, length)
        float along = bp.x - uTrain.x, side = abs(bp.y - (${TRACK.toFixed(1)}));
        float bow = smoothstep(-1.6, -0.2, along) * (1.0 - smoothstep(-0.2, 0.6, along)) * (1.0 - smoothstep(1.4, 2.6 + uTrain.y * 2.0, side));
        float body = step(0.0, along) * (1.0 - smoothstep(uTrain.z, uTrain.z + 4.0 + uTrain.y * 40.0, along));
        float spread = 1.45 + 0.35 + max(along, 0.0) * 0.05 * uTrain.y;
        float wake = body * smoothstep(1.3, 1.45, side) * (1.0 - smoothstep(spread - 0.3, spread + 0.4, side));
        float ripple = 0.55 + 0.45 * sin(bp.x * 6.0 + uTime * 9.0) * sin(bp.y * 9.0 - uTime * 6.0);
        float foam = uTrain.y * clamp(bow * 1.4 + wake * ripple, 0.0, 1.0);
        foam += smoothstep(0.6, 0.44, dep) * (0.35 + 0.25 * sin(uTime * 1.4 + bp.x * 2.7 + bp.y * 1.9));   // lace around the shores
        foam = clamp(foam, 0.0, 1.0);
        diffuseColor.rgb = mix(diffuseColor.rgb, vec3(1.0), foam * 0.85);
        diffuseColor.a = max(diffuseColor.a, foam * 0.9);`)
      .replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
        vec2 q = vec2(vW.x, -vW.z) * 0.9;
        float h1 = sin(q.x * 1.7 + uTime * 1.1 + sin(q.y * 1.3 + uTime * 0.4) * 2.0), h2 = sin(q.y * 2.3 - uTime * 0.9 + q.x * 0.5);
        vec3 tilt = vec3(h1 * 0.07 + h2 * 0.04, 0.0, h2 * 0.07 - h1 * 0.03);
        normal = normalize(normal + (viewMatrix * vec4(tilt, 0.0)).xyz);`)
      .replace('#include <opaque_fragment>', `float fres = pow(1.0 - saturate(dot(normalize(vViewPosition), normal)), 4.0);
        outgoingLight = mix(outgoingLight, uSky, fres * 0.35);
        #include <opaque_fragment>`);
  };
  return m;
}

export function buildTerminal() {
  const w = makeWorld('terminal', 'The Terminal');
  const s = w.scene;
  w.groundY = PZ;
  w.spawn.copy(B(-3.9, 0.9, PZ)); w.spawnYaw = Math.PI / 2;
  w.cam = { dist: 11, pitch: 0.34, yaw: 0.12 };
  w.bloom = 0.35;
  w.glowMats = [];

  // ---------- sky, light ----------
  const skyMesh = sky(s, 0x3f8fe0, 0xbfe4f3, 0xbfe4ea, [0, 1, 1], 0xfff2d0);
  const SU = skyMesh.material.uniforms;
  const starField = stars(s, 1600, 300, 420, 1.3, true); starField.material.transparent = true;
  s.fog = new THREE.Fog(0xd2ecf2, 70, 300);
  const hemi = new THREE.HemisphereLight(0xe6f6ff, 0x9fc7a8, 1.5); s.add(hemi);
  w.sunlight(0xfff0d0, 2.2, 10, 20, 12);
  const sc = w.sun.shadow.camera; sc.left = sc.bottom = -26; sc.right = sc.top = 26; sc.far = 110; sc.updateProjectionMatrix();

  // ---------- water and sea floor ----------
  const U = { uTime: { value: 0 }, uIslets: { value: Array.from({ length: 16 }, () => new THREE.Vector3(1e4, 1e4, 0)) },
    uShallow: { value: new THREE.Color() }, uDeep: { value: new THREE.Color() }, uSky: { value: new THREE.Color() }, uTrain: { value: new THREE.Vector3(1e4, 0, 25) } };
  const water = new THREE.Mesh(new THREE.PlaneGeometry(900, 900).rotateX(-Math.PI / 2), makeWater(U));
  water.position.set(55, 0, 0); water.receiveShadow = true; water.renderOrder = 1; water.userData.noShadow = true;
  s.add(water);
  const floorMat = painted(new THREE.MeshToonMaterial({ color: 0xe6d6a8 }), 'sand');
  const deepFloor = new THREE.Mesh(new THREE.PlaneGeometry(900, 900).rotateX(-Math.PI / 2), new THREE.MeshBasicMaterial({ color: 0x14304a }));
  deepFloor.position.set(55, -4.3, 0); deepFloor.userData.noShadow = true; s.add(deepFloor);
  function buildSeabed(islets) {
    const g = new THREE.PlaneGeometry(220, 124, 160, 90).rotateX(-Math.PI / 2), p = g.attributes.position;
    for (let i = 0; i < p.count; i++) { const bx = p.getX(i) + 55, by = -p.getZ(i); p.setY(i, -seaDepth(bx, by, islets)); }
    g.computeVertexNormals();
    const bed = new THREE.Mesh(g, floorMat); bed.position.x = 55; bed.receiveShadow = true; s.add(bed);
    islets.forEach(([x, y, r], i) => U.uIslets.value[i].set(x, y, r));
  }

  // ---------- the Blender station ----------
  let placed = {};
  w.progress = () => {};
  const CANOPY = /^c_(256b45|3c8c4c|7cbc58|c2e272)/;                            // the leafy parts of the Blender trees
  const isCanopy = (m) => CANOPY.test(m.name || '');
  w.ready = loadLayout('models/terminal', s, (n, of) => w.progress(n, of), (name, model) => {
    if (/^tree_|^pine$/.test(name)) leafify(model, name === 'pine' ? 'pine' : 'broad', isCanopy, gradient());
  }).then((r) => {
    placed = r.placed; w.glowMats = r.glow; w.loaded = true;
    buildSeabed(r.layout.islets || []);
    trees = [...(placed.tree_a || []), ...(placed.tree_b || []), ...(placed.tree_c || []), ...(placed.pine || [])].map((o) => ({ o, ph: Math.random() * 6.28 }));
    train = placed.train[0]; train.userData.home = train.position.clone();
    train.position.x = 1e4; nextTrain = 6;
  });
  let trees = [], train = null, nextTrain = 1e9;

  // The station name, drawn here so the Korean stays crisp (covers the board on the Blender sign).
  const name = sign(s, ['어딘가', 'SOMEWHERE  ·  ENTAH DI MANA', '←  Semarang                    Seoul  →'], 2.1, 0.82, -6.2, PZ + 1.51, -(1.9 - 0.045 * 0.8),
    { size: [0.34, 0.12, 0.11], fg: ['#2f3b52', '#5a6478', '#b0563f'], bg: '#f6eedb', res: 200 });
  name.material = new THREE.MeshToonMaterial({ map: name.material.map });

  // ---------- overhead wires between the utility poles ----------
  const POLES = [-7, 11, 29, 47, 65, 83], wires = [];
  for (let i = 0; i < POLES.length - 1; i++) for (const [z, wd] of [[8.66, 2.3], [7.86, 1.8]]) for (const k of [-1, 0, 1]) {
    const y = -5.9 + k * wd * 0.42, sag = 0.35 + ((i * 7 + k * 3 + z) % 1) * 0.25;
    wires.push(new THREE.TubeGeometry(new THREE.QuadraticBezierCurve3(B(POLES[i], y, z), B((POLES[i] + POLES[i + 1]) / 2, y, z - sag * 2), B(POLES[i + 1], y, z)), 24, 0.014, 4));
  }
  wires.push(new THREE.TubeGeometry(new THREE.QuadraticBezierCurve3(B(11, -5.9, 7.2), B(11.5, -1, 5.0), B(12, 3.2, PZ + 3.2)), 24, 0.014, 4));
  wires.push(new THREE.TubeGeometry(new THREE.QuadraticBezierCurve3(B(-7, -5.9, 7.2), B(-7.6, -1.5, 5.4), B(-8.2, 2.4, PZ + 4.2)), 24, 0.014, 4));
  s.add(new THREE.Mesh(mergeGeometries(wires), new THREE.MeshBasicMaterial({ color: 0x3b332d })));

  // ---------- far islands with little villages ----------
  for (const [x, y, r, z] of [[190, 100, 80, 0.2], [230, -80, 95, 0.22], [140, 190, 70, 0.18], [150, -180, 70, 0.16]]) {
    blob(s, x, -2, -y, r, 0x3f8a6a, 0x9ad88a, { squash: [1.0, z, 1.0], lump: 0.25 });
    for (let k = 0; k < 4; k++) {
      const hx = x - r * 0.45 + k * 9, hy = y + (k % 2) * 8 - r * 0.2, hz = r * z * 0.72 - 2;
      const hm = new THREE.Mesh(new THREE.BoxGeometry(5, 4, 5), new THREE.MeshToonMaterial({ color: 0xf3ead6 })); hm.position.copy(B(hx, hy, hz + 2)); s.add(hm);
      const rf = new THREE.Mesh(new THREE.ConeGeometry(4.2, 2.4, 4), new THREE.MeshToonMaterial({ color: 0xc9604a })); rf.position.copy(B(hx, hy, hz + 5.2)); rf.rotation.y = Math.PI / 4; s.add(rf);
    }
  }

  // ---------- clouds drifting with the wind ----------
  const cm = cloudMat(0xffffff, 0xb4cbe6, 0xffffff, [-0.4, 0.6, 0.7]);
  const WIND = new THREE.Vector3(1.4, 0, 0.35);
  const clouds = [];
  for (let i = 0; i < 16; i++) {
    const a = (i / 16) * 6.283 + Math.random() * 0.3, r = 130 + Math.random() * 140;
    const c = cloud(s, cm, 55 + Math.cos(a) * r, 28 + Math.random() * 45, Math.sin(a) * r, 3.2 + Math.random() * 2.8, 11);
    c.rotation.y = Math.random() * 6.28; c.userData.bob = Math.random() * 6.28; clouds.push(c);
  }

  // ---------- gulls ----------
  const gulls = [];
  const gullMat = new THREE.MeshToonMaterial({ color: 0xffffff, side: THREE.DoubleSide });
  for (let i = 0; i < 6; i++) {
    const g = new THREE.Group(), wings = [-1, 1].map((sd) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 0.22).translate(0.45 * sd, 0, 0), gullMat); m.rotation.x = -Math.PI / 2; g.add(m); return m; });
    g.userData = { wings, cx: 30 + Math.random() * 50, cz: -10 - Math.random() * 25, r: 8 + Math.random() * 10, h: 13 + Math.random() * 9, sp: 0.15 + Math.random() * 0.12, ph: Math.random() * 6.28 };
    s.add(g); gulls.push(g);
  }

  // ---------- spray thrown up by the train ----------
  const SN = 420, sp = new Float32Array(SN * 3), sv = new Float32Array(SN * 3), life = new Float32Array(SN);
  const sgeo = new THREE.BufferGeometry(); sgeo.setAttribute('position', new THREE.BufferAttribute(sp, 3));
  const spray = new THREE.Points(sgeo, new THREE.PointsMaterial({ size: 0.28, map: softDot(), transparent: true, depthWrite: false, color: 0xffffff, opacity: 0.85 }));
  spray.frustumCulled = false; spray.renderOrder = 2; s.add(spray);
  for (let i = 0; i < SN; i++) sp[i * 3 + 1] = -50;
  let emitAcc = 0, spawnI = 0;

  // ---------- night lights on the platform ----------
  const lamps = [B(3, 0.6, PZ + 1.95), B(8.3, 0.6, PZ + 1.95), B(13.7, 0.6, PZ + 1.95), B(19.2, 0.6, PZ + 1.95), B(-8.2, 1.2, PZ + 4.0), B(27.5, 1.2, PZ + 4.0)].map((p) => {
    const l = new THREE.PointLight(0xffb870, 0, 13, 1.6); l.position.copy(p); s.add(l); return l;
  });

  // ---------- walking, collisions, things to look at ----------
  w.inside = (x, z) => {
    const bx = x, by = -z;
    if (by > 2.8 && by < 3.2 && (bx < 0.5 || bx > 23.5)) return false;            // the white fences
    return (bx > -10.8 && bx < 34.8 && by > -1.25 && by < 3.05) || (bx > -4.8 && bx < 28.8 && by > 2.9 && by < 10.2);
  };
  const S = (bx, by, sx, sy) => w.solid(bx, -by, sx, sy);
  S(11, 5.6, 12.3, 5.3);                                                           // the station building
  for (const x of [1.5, 5, 8.5, 12, 15.5, 19, 22.5]) S(x, -0.45, 0.36, 0.36);   // canopy posts
  for (const x of [1.5, 19, 22.5]) S(x, 2.95, 0.3, 0.3);
  S(14.9, 2.65, 2.3, 0.8); S(8.95, 2.72, 1.05, 0.7); S(12.72, 2.78, 0.55, 0.55); S(9.75, 2.8, 0.45, 0.45); S(19.5, 2.65, 1.6, 0.85);
  for (const [x, y] of [[5.5, 2.65], [6.2, 2.75], [16.6, 2.7], [1.6, -0.1], [22.4, -0.1], [17.4, 2.75]]) S(x, y, 0.5, 0.5);
  S(-2.6, -0.2, 0.62, 0.62); S(-1.75, -0.25, 0.6, 0.35);                         // chair, suitcase
  S(-7.36, 1.9, 0.3, 0.3); S(-5.04, 1.9, 0.3, 0.3);                               // sign posts
  S(-8.2, 2.4, 0.3, 0.3); S(27.5, 2.4, 0.3, 0.3);                                 // lamps
  for (const x of [-9, -6.3, -3.4, 25, 28, 31]) S(x, 2.55, 1.55, 0.6);           // planters

  w.hot(-2.6, 0.2, 'Sit down and wait for the train', 'sit', { y: 1.7, r: 1.6 });
  w.hot(7.9, -2.35, 'Read the timetable', 'welcome', { y: 2.1, r: 1.3 });
  w.hot(8.95, -1.95, 'Check the vending machine', 'contact', { y: 2.3, r: 1.2 });
  w.hot(-6.2, -1.2, 'Read the station sign', 'station', { y: 2.7, r: 1.6 });
  w.hot(14.35, -1.95, 'Say hello to the cat', 'cat', { y: 1.4, r: 1.3 });

  w.seat = { pos: B(-2.6, -0.2, PZ), yaw: 0.15 };
  w.standSpot = B(-2.6, 0.55, PZ);

  // ---------- the dimension crack ----------
  const CX = -2.6, CZ = -TRACK;                                                    // where it opens: over the line, in front of the chair
  const crack = makeCrack();
  crack.position.set(CX, -0.1, CZ); crack.setOpen(0); s.add(crack);
  w.crack = crack;
  const C = new THREE.Vector3(CX, 2.6, CZ);
  const crackLight = new THREE.PointLight(0xffffff, 0, 16);
  crackLight.position.set(CX, 2.4, CZ - 0.8); s.add(crackLight);
  const fx = { transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, opacity: 0 };
  const rays = new THREE.Group(), rayMat = new THREE.MeshBasicMaterial(fx);
  rays.position.set(C.x, C.y, C.z + 0.06); rays.renderOrder = 2; s.add(rays);
  for (let i = 0; i < 12; i++) {
    const len = 5 + Math.random() * 6;
    const m = new THREE.Mesh(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(-0.1, 0, 0), new THREE.Vector3(0.1, 0, 0), new THREE.Vector3(0, len, 0)]), rayMat);
    m.rotation.z = (i / 12) * 6.283 + Math.random() * 0.4; rays.add(m);
  }
  const ring = new THREE.Mesh(new THREE.RingGeometry(0.9, 1, 64), new THREE.MeshBasicMaterial(fx));
  ring.position.copy(C); ring.renderOrder = 2; s.add(ring);
  const MN = 240, mp = new Float32Array(MN * 3), ms = [];
  for (let i = 0; i < MN; i++) ms.push({ a: Math.random() * 6.283, r: 1 + Math.random() * 9, y: (Math.random() - 0.5) * 6, v: 1.5 + Math.random() * 2.5 });
  const mgeo = new THREE.BufferGeometry(); mgeo.setAttribute('position', new THREE.BufferAttribute(mp, 3));
  const motes = new THREE.Points(mgeo, new THREE.PointsMaterial({ size: 0.12, map: softDot(), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
  motes.frustumCulled = false; motes.visible = false; motes.renderOrder = 2; s.add(motes);

  // ---------- applying the time of day (plus the cutscene's push toward dusk) ----------
  const P = {}, Q = {}, sd = new THREE.Vector3();
  let moodK = 0;
  function applySky(h) {
    paletteAt(h, P);
    const k = h > 6 && h < 19.5 ? moodK : 0;                                       // the cutscene drifts into dusk (by day)
    const p = k > 0 ? mixPal(Q, P, DUSK, k) : P;
    SU.a.value.copy(p.top); SU.b.value.copy(p.mid); SU.c.value.copy(p.bot);
    sunDir(h, sd); SU.sun.value.copy(sd); SU.sc.value.copy(p.sun); SU.sk.value = 1;
    w.sun.color.copy(p.sun); w.sun.intensity = p.sunI; w.sun.userData.offset.copy(sd).multiplyScalar(40);
    hemi.color.copy(p.sky); hemi.groundColor.copy(p.ground); hemi.intensity = p.hemiI;
    s.fog.color.copy(p.fog);
    U.uShallow.value.copy(p.shallow); U.uDeep.value.copy(p.deep); U.uSky.value.copy(p.mid);
    cm.uniforms.lit.value.copy(p.cLit); cm.uniforms.shade.value.copy(p.cShade); cm.uniforms.edge.value.copy(p.cEdge); cm.uniforms.sun.value.copy(sd);
    starField.material.opacity = p.stars;
    for (const l of lamps) l.intensity = p.lamps * 9;
    for (const m of w.glowMats) m.emissiveIntensity = m.userData.glow * (0.25 + 0.75 * Math.max(p.lamps, 0.2));
    w.bloom = p.bloom;
  }

  // ---------- the train ----------
  const TRAIN_LEN = 25.4;
  let run = null;                                                                  // { x, v } while a train is on the line
  const startRun = (x, v) => { run = { x, v }; };
  Object.defineProperty(w, 'trainX', { get: () => (run ? run.x : null) });
  function trainTick(t, dt) {
    if (!train) return;
    if (!run) { U.uTrain.value.set(1e4, 0, TRAIN_LEN); train.position.x = 1e4; return; }
    run.x -= run.v * dt; train.position.x = run.x;
    const speedK = Math.min(1, run.v / 40);
    U.uTrain.value.set(run.x, speedK, TRAIN_LEN);
    // throw spray from the bow and along the wheels, more the faster it goes
    emitAcc += dt * run.v * 6;
    while (emitAcc > 1) {
      emitAcc -= 1; const i = spawnI++ % SN, side = Math.random() < 0.5 ? -1 : 1, front = Math.random() < 0.45;
      sp[i * 3] = run.x + (front ? Math.random() * 0.8 : Math.random() * TRAIN_LEN); sp[i * 3 + 1] = 0.05; sp[i * 3 + 2] = CZ + side * (1.3 + Math.random() * 0.3);
      sv[i * 3] = -run.v * (front ? 0.35 : 0.08) * Math.random(); sv[i * 3 + 1] = (1 + Math.random() * 2.5) * (0.4 + speedK); sv[i * 3 + 2] = side * (0.6 + Math.random() * 2) * (0.3 + speedK);
      life[i] = 0.6 + Math.random() * 0.6;
    }
    if (run.x < -40 - TRAIN_LEN) run = null;
  }
  function sprayTick(dt) {
    for (let i = 0; i < SN; i++) {
      if (life[i] <= 0) { sp[i * 3 + 1] = -50; continue; }
      life[i] -= dt; sv[i * 3 + 1] -= 9 * dt;
      sp[i * 3] += sv[i * 3] * dt; sp[i * 3 + 1] += sv[i * 3 + 1] * dt; sp[i * 3 + 2] += sv[i * 3 + 2] * dt;
      if (sp[i * 3 + 1] < 0) life[i] = 0;
    }
    sgeo.attributes.position.needsUpdate = true;
  }

  // ---------- the cutscene: four shots ----------
  const END = 7.6, V = (a) => new THREE.Vector3(...a);
  const shots = [
    { t: 0, from: V([-0.9, 2.6, -2.5]), to: V([-1.3, 2.35, -1.9]), look: V([CX, 1.8, CZ]) },          // waiting, behind the chair
    { t: 1.5, from: V([-9.5, 1.15, 1.9]), to: V([-9.5, 1.3, 2.05]), look: V([40, 1.6, CZ]) },         // at the platform edge, the train bearing down
    { t: 3.05, from: V([0.6, 2.4, -3.4]), to: V([-0.8, 2.45, -2.0]), look: V([CX, 2.4, CZ]) },        // it passes, the air tears
    { t: 5.7, from: V([-1.4, 2.1, -1.4]), to: V([-2.4, 1.9, 1.7]), look: V([CX, 2.6, CZ + 1]) },     // walking in
    { t: END },
  ];
  w.cine = { pos: shots[0].from.clone(), look: shots[0].look.clone(), snap: false, shake: 0, glow: 0 };
  w.seqT = 0;
  let seq = null;
  const cl = (x) => THREE.MathUtils.clamp(x, 0, 1), ease = (x) => x * x * (3 - 2 * x);
  w.depart = (dest, onArrive) => {
    seq = { t: 0, onArrive, done: false, shot: 0 };
    crack.setColor(DEST[dest].color); crackLight.color.set(DEST[dest].color);
    rayMat.color.set(DEST[dest].color).multiplyScalar(1.4); ring.material.color.set(DEST[dest].color).multiplyScalar(2); motes.material.color.set(DEST[dest].color).lerp(new THREE.Color(0xffffff), 0.5);
    startRun(95 + 1.2 * 40, 40);                                                   // reaches the crack about 3 s in
  };
  w.walkIn = (k, p) => p.set(CX, PZ - (PZ - 0.02) * THREE.MathUtils.smoothstep(k, 0.36, 0.5), 0.2 + k * 3.2);
  w.reset = () => {
    seq = null; w.seqT = 0; moodK = 0; crack.setOpen(0); crack.setPortal(null); crackLight.intensity = 0; motes.visible = false;
    rayMat.opacity = ring.material.opacity = 0; run = null; nextTrain = 20;
    Object.assign(w.cine, { snap: false, shake: 0, glow: 0 }); w.cine.pos.copy(shots[0].from); w.cine.look.copy(shots[0].look);
  };

  const water0 = new THREE.Vector3();
  w.ticks.push((t, dt) => {
    U.uTime.value = t;
    applySky(hourNow());
    for (const c of clouds) {                                                      // drift; wrap around the far side
      c.position.addScaledVector(WIND, dt); c.position.y += Math.sin(t * 0.1 + c.userData.bob) * dt * 0.15;
      water0.set(c.position.x - 55, 0, c.position.z);
      if (water0.length() > 300) c.position.set(55 - WIND.x * 280 / WIND.length() + (Math.random() - 0.5) * 160, c.position.y, -WIND.z * 280 / WIND.length() + (Math.random() - 0.5) * 160);
    }
    for (const { o, ph } of trees) { o.rotation.z = Math.sin(t * 0.9 + ph) * 0.012; o.rotation.x = Math.sin(t * 0.7 + ph * 1.3) * 0.01; }
    for (const g of gulls) {
      const u = g.userData, a = t * u.sp + u.ph;
      g.position.set(u.cx + Math.cos(a) * u.r, u.h + Math.sin(t * 0.5 + u.ph) * 0.8, u.cz + Math.sin(a) * u.r); g.rotation.y = -a;
      const flap = Math.sin(t * 7 + u.ph) * 0.45; u.wings[0].rotation.y = flap; u.wings[1].rotation.y = -flap;
    }
    // a train passes every so often, even when nobody is leaving
    if (!seq && !run && (nextTrain -= dt) < 0) { startRun(150, 14 + Math.random() * 6); nextTrain = 35 + Math.random() * 20; }
    trainTick(t, dt); sprayTick(dt);
    crack.tick(t);
    if (!seq) return;

    const q = (seq.t += dt); w.seqT = q;
    moodK = ease(cl(q / 3.6));
    let i = seq.shot; while (q >= shots[i + 1].t && i < shots.length - 2) i++;
    if (i !== seq.shot) { seq.shot = i; w.cine.snap = true; }
    const sh = shots[i];
    w.cine.pos.lerpVectors(sh.from, sh.to, ease(cl((q - sh.t) / (shots[i + 1].t - sh.t)))); w.cine.look.copy(sh.look);
    const near = run ? Math.min(Math.abs(run.x - w.cine.pos.x), Math.abs(run.x + TRAIN_LEN - w.cine.pos.x), run.x < w.cine.pos.x && run.x + TRAIN_LEN > w.cine.pos.x ? 0 : 99) : 99;
    w.cine.shake = 0.09 * Math.exp(-((near / 9) ** 2));
    w.cine.glow = ease(cl((q - 6.8) / 0.8)) * 1.0;
    const open = cl((q - 3.85) / 1.5), wide = cl((open - 0.3) / 0.7), qs = q - 4.3;
    crack.setOpen(open); crackLight.intensity = wide * 90;
    rayMat.opacity = wide * (0.22 + Math.sin(t * 5) * 0.05); rays.rotation.z = t * 0.15;
    ring.scale.setScalar(1 + Math.max(0, qs) * 15); ring.material.opacity = qs > 0 ? cl(1 - qs / 0.9) * 0.9 : 0;
    motes.visible = wide > 0;
    for (let n = 0; n < MN; n++) {
      const m = ms[n]; m.r -= dt * m.v * (0.6 + wide); m.a += dt * (1.2 + 3 / (m.r + 0.5));
      if (m.r < 0.15) { m.r = 6 + Math.random() * 4; m.y = (Math.random() - 0.5) * 6; }
      mp[n * 3] = C.x + Math.cos(m.a) * m.r; mp[n * 3 + 1] = C.y + m.y * Math.min(1, m.r / 5) + Math.sin(m.a) * m.r * 0.25; mp[n * 3 + 2] = C.z - 0.4 - Math.abs(Math.sin(m.a)) * m.r * 0.5;
    }
    mgeo.attributes.position.needsUpdate = true;
    if (q > END && !seq.done) { seq.done = true; seq.onArrive(); }
  });

  return w.finish();
}
