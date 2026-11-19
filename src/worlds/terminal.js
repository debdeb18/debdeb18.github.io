// The terminal: a little country station on a railway that runs just under the sea.
// The station itself is built in Blender (models/terminal); this file adds what moves: water, sky, clouds, the train, the cutscene.
import * as THREE from 'three';
import { makeWorld, sky, stars, softDot, makeCrack, sign, uPlayer } from '../kit.js';
import { blob } from '../nature.js';
import { loadLayout, loadModel, gradient } from '../models.js';
import { leafify } from '../foliage.js';
import { cumulus, cumulusMaterial } from '../clouds.js';
import { grassField } from '../grass.js';
import { painted } from '../paint.js';

export const DEST = {
  home: { color: 0x8fb4ff, name: 'Home among the stars' },
  office: { color: 0xffd27a, name: 'The Office' },
  market: { color: 0xff7aa8, name: 'The Night Market' },
};

const B = (x, y, z = 0) => new THREE.Vector3(x, z, -y);       // Blender (x right, y away, z up) -> three
const PZ = 0.95, TRACK = -3.2;                                   // porch floor height; the line (Blender y)
// The v1 scenery, left out while the world is rebuilt from zero (the layout still lists it).
const V1_SCENERY = ['islet_00', 'islet_01', 'islet_02', 'islet_03', 'islet_04', 'islet_05', 'islet_06', 'islet_07', 'islet_08', 'islet_09', 'islet_10', 'islet_11',
  'islet_12', 'islet_13', 'islet_14', 'islet_15', 'tree_a', 'tree_b', 'tree_c', 'pine', 'footbridge', 'buoy_red', 'buoy_yellow', 'lily_pads', 'wires', 'backdrop', 'far_islands', 'gulls'];
const LOW = 0.325, SIGN_K = 0.6, RAIL_Z = -0.322;              // the porch's lower front level; the sign's size; the rail (its top at -0.05)

// ---------- time of day: the sky follows the visitor's clock (or ?time=HH) ----------
const NUMBERS = new Set(['sunI', 'hemiI', 'lamps', 'stars', 'glow', 'bloom']);                // everything else in a palette is a colour
const pal = (o) => Object.fromEntries(Object.entries(o).map(([k, v]) => [k, NUMBERS.has(k) ? v : new THREE.Color(v)]));
const NIGHT = pal({ top: 0x070b24, mid: 0x1b2552, bot: 0x0e1638, sun: 0x8fa8ff, sunI: 0.45, sky: 0x3a4a80, ground: 0x182030, hemiI: 0.55, fog: 0x18214a, shallow: 0x1d5a6e, deep: 0x07142e, lamps: 1, cLit: 0x5d68a0, cShade: 0x20264a, cEdge: 0x8c96cc, stars: 1, glow: 0.45, bloom: 0.75 });
const DAWN = pal({ top: 0x4a6fb0, mid: 0xffc2a0, bot: 0x8aa0c8, sun: 0xffb38a, sunI: 1.3, sky: 0xd8c8e8, ground: 0x8a9a78, hemiI: 1.0, fog: 0xf0c8b8, shallow: 0x6ab4c4, deep: 0x24508c, lamps: 0.5, cLit: 0xffe2d2, cShade: 0x9890c4, cEdge: 0xffd0b4, stars: 0.15, glow: 0.3, bloom: 0.45 });
const DAY = pal({ top: 0x2f86e0, mid: 0xbfe4f3, bot: 0xbfe4ea, sun: 0xfff2d6, sunI: 3.0, sky: 0xb4d4f4, ground: 0x8a9c8c, hemiI: 1.2, fog: 0xd2ecf2, shallow: 0x45b8c8, deep: 0x1a4f96, lamps: 0, cLit: 0xfbf8ee, cShade: 0xa3b0cf, cEdge: 0xffffff, stars: 0, glow: 0.2, bloom: 0.3 });
const DUSK = pal({ top: 0x232a5c, mid: 0xf6b3a0, bot: 0x7a86b4, sun: 0xffa070, sunI: 1.5, sky: 0xc8a8c8, ground: 0x6a6a7a, hemiI: 0.95, fog: 0xe8b9b0, shallow: 0x5a8fb4, deep: 0x1d3270, lamps: 1, cLit: 0xffd9c4, cShade: 0x8a7bb0, cEdge: 0xffc4a0, stars: 0.1, glow: 0.6, bloom: 0.55 });
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
// ---------- weather: mostly fair, with stretches of heavy cloud that come and go over a few hours ----------
// Everyone visiting at the same time sees the same weather. ?weather=clear | cloudy | 0..1 pins it.
const wParam = new URLSearchParams(location.search).get('weather');
const weatherNow = () => {
  if (wParam === 'clear') return 0; if (wParam === 'cloudy') return 1; if (wParam && !isNaN(+wParam)) return Math.min(1, Math.max(0, +wParam));
  const h = Date.now() / 3.6e6, n = 0.5 + 0.28 * Math.sin(h * 6.283 / 7.3) + 0.22 * Math.sin(h * 6.283 / 3.1 + 1.7);
  return THREE.MathUtils.smoothstep(n, 0.58, 0.8);                               // cloudy roughly a third of the time
};
const hourNow = () => { if (!isNaN(forced)) return ((forced % 24) + 24) % 24; const d = new Date(); return d.getHours() + d.getMinutes() / 60; };

// ---------- the sea floor: shallow banks under the line, the station and the islets, deep water beyond ----------
function seaDepth(bx, by, islets) {
  const dt = Math.abs(by - TRACK) - 3.0;                                           // off the track bank the sea drops away fast
  let d = Math.max(-11 - bx, bx - 35, -2.5 - by, by - 11.5, 0) - 1.0;
  for (const [ix, iy, ir] of islets) d = Math.min(d, Math.hypot(bx - ix, by - iy) - ir * 1.15);
  let k = Math.min(Math.min(1, Math.max(0, dt / 3.5)), Math.min(1, Math.max(0, d / 8))); k = k * k * (3 - 2 * k);
  return 0.42 + 3.4 * k - Math.sin(bx * 0.7) * Math.cos(by * 0.9) * 0.05;
}
const DEPTH_GLSL = `
uniform vec3 uIslets[16];
float seaDepth(vec2 b) {
  float dt = abs(b.y - (${TRACK.toFixed(1)})) - 3.0;
  float d = max(max(max(-11.0 - b.x, b.x - 35.0), max(-2.5 - b.y, b.y - 11.5)), 0.0) - 1.0;
  for (int i = 0; i < 16; i++) d = min(d, length(b - uIslets[i].xy) - uIslets[i].z * 1.15);
  float k = min(clamp(dt / 3.5, 0.0, 1.0), clamp(d / 8.0, 0.0, 1.0)); k = k * k * (3.0 - 2.0 * k);
  return 0.42 + 3.4 * k - sin(b.x * 0.7) * cos(b.y * 0.9) * 0.05;
}`;

// The porch's footprint and its tower (Blender x, y): the water draws a thin foam line round them, as round the islets.
const PX = 0, PY = 1.4;                                            // where the porch stands (blender/assets/halt.py, centred)
const PORCH = [PX, PY, 5.5, 2.3], TOWER = [PX - 7.0, PY - 0.55, 2.45];

// Ghibli-style water (docs/ghibli-water.md): flat painted colour in hard bands (lightest in a rim along every shore,
// then by depth), see-through in the shallows, wobbly cell-like highlight lines, a thin white foam line round every
// shore with a second ring that pulses, blinking sparkles; plus the train's bow wave and wake, and rings round a wader.
const WATER_GLSL = `
vec2 wHash(vec2 p) { p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3))); return fract(sin(p) * 43758.5453); }
float wNoise(vec2 p) { vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
  return mix(mix(wHash(i).x, wHash(i + vec2(1, 0)).x, f.x), mix(wHash(i + vec2(0, 1)).x, wHash(i + vec2(1, 1)).x, f.x), f.y); }
// distance to the nearest cell edge of a slowly moving Voronoi pattern (the 'distance to edge' feature)
float cellEdge(vec2 x, float t) {
  vec2 n = floor(x), f = fract(x), mg, mr; float md = 8.0;
  for (int j = -1; j <= 1; j++) for (int i = -1; i <= 1; i++) {
    vec2 g = vec2(float(i), float(j)), o = 0.5 + 0.5 * sin(t + 6.2831 * wHash(n + g)), r = g + o - f; float d = dot(r, r);
    if (d < md) { md = d; mr = r; mg = g; } }
  md = 8.0;
  for (int j = -2; j <= 2; j++) for (int i = -2; i <= 2; i++) {
    vec2 g = mg + vec2(float(i), float(j)), o = 0.5 + 0.5 * sin(t + 6.2831 * wHash(n + g)), r = g + o - f;
    if (dot(mr - r, mr - r) > 0.00001) md = min(md, dot(0.5 * (mr + r), normalize(r - mr))); }
  return md;
}
// distance to the nearest point of a slowly moving Voronoi pattern (for sparkles)
float cellDot(vec2 x, float t) {
  vec2 n = floor(x), f = fract(x); float md = 8.0;
  for (int j = -1; j <= 1; j++) for (int i = -1; i <= 1; i++) {
    vec2 g = vec2(float(i), float(j)), o = 0.5 + 0.5 * sin(t + 6.2831 * wHash(n + g)); md = min(md, length(g + o - f)); }
  return md;
}
uniform vec4 uPorch; uniform vec3 uTower;
float shoreDist(vec2 b) {                                          // metres from the nearest shore: islets, the porch, its tower
  vec2 q = abs(b - uPorch.xy) - uPorch.zw; float s = length(max(q, 0.0)) + min(max(q.x, q.y), 0.0);
  s = min(s, length(b - uTower.xy) - uTower.z);
  for (int i = 0; i < 16; i++) s = min(s, length(b - uIslets[i].xy) - uIslets[i].z * 0.99);
  return s;
}`;

function makeWater(U) {
  const m = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1, metalness: 0, transparent: true, depthWrite: false });
  m.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, U);
    sh.vertexShader = 'varying vec3 vW;\n' + sh.vertexShader.replace('#include <project_vertex>', '#include <project_vertex>\nvW = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    sh.fragmentShader = 'varying vec3 vW;\nuniform float uTime, uSun;\nuniform vec3 uShallow, uDeep, uSky, uTrain, uPlayer;\nuniform float uStir;\n' + DEPTH_GLSL + WATER_GLSL + '\n' + sh.fragmentShader
      .replace('#include <color_fragment>', `#include <color_fragment>
        vec2 bp = vec2(vW.x, -vW.z);
        float dep = seaDepth(bp), shore = shoreDist(bp);
        float wob = (wNoise(bp * 3.0 + uTime * 0.2) - 0.5) * 0.12;                // edges that wobble, as if drawn by hand
        // the colour bands: a light rim along every shore, then by depth; hard steps, like paint
        vec3 rim = mix(uShallow, vec3(1.0), 0.28), mid = mix(uShallow, uDeep, 0.55);
        vec3 col = uDeep; float alpha = 1.0;
        if (dep < 2.2 + wob * 4.0) { col = mid; alpha = 0.9; }
        if (dep < 0.9 + wob * 2.0) { col = uShallow; alpha = 0.55; }                // over the line and the banks: see-through
        if (shore < 0.75 + wob) { col = rim; alpha = 0.38; }                         // the shallows at the shore: clearest
        diffuseColor.rgb = col; diffuseColor.a = alpha;
        // the train pushes a bow wave and leaves a wake; both grow with its speed (uTrain = front x, speed 0..1, length)
        float along = bp.x - uTrain.x, side = abs(bp.y - (${TRACK.toFixed(1)}));
        float bow = smoothstep(-1.6, -0.2, along) * (1.0 - smoothstep(-0.2, 0.6, along)) * (1.0 - smoothstep(1.4, 2.6 + uTrain.y * 2.0, side));
        float body = step(0.0, along) * (1.0 - smoothstep(uTrain.z, uTrain.z + 4.0 + uTrain.y * 40.0, along));
        float spread = 1.45 + 0.35 + max(along, 0.0) * 0.05 * uTrain.y;
        float wake = body * smoothstep(1.3, 1.45, side) * (1.0 - smoothstep(spread - 0.3, spread + 0.4, side));
        float ripple = 0.55 + 0.45 * sin(bp.x * 6.0 + uTime * 9.0) * sin(bp.y * 9.0 - uTime * 6.0);
        float foam = uTrain.y * clamp(bow * 1.4 + wake * ripple, 0.0, 1.0);
        float pd = length(bp - vec2(uPlayer.x, -uPlayer.z));                     // rings spreading from legs in the water
        float wet = 1.0 - smoothstep(0.05, 0.25, uPlayer.y);
        for (int k = 0; k < 2; k++) { float rr = 0.35 + fract(uTime * 0.7 + float(k) * 0.5) * 1.3; foam += wet * (1.0 - smoothstep(0.0, 0.07, abs(pd - rr))) * (1.0 - (rr - 0.35) / 1.3) * 0.8; }
        // how stirred-up the water is: along the train and its wake, and round a wader who is moving
        float trainStir = min(1.0, uTrain.y * 3.0) * clamp(bow * 1.5 + body * (1.0 - smoothstep(1.4, 7.0 + uTrain.y * 6.0, side)) * (1.0 - smoothstep(0.0, uTrain.z + 30.0 * uTrain.y, along) * 0.7), 0.0, 1.0);
        float stir = clamp(trainStir + wet * uStir * (1.0 - smoothstep(0.3, 4.0, pd)), 0.0, 1.0);
        // wobbly cell-like highlight lines, here and there (more where the water is stirred)
        vec2 cp = bp * 1.1 + (vec2(wNoise(bp * 1.6 + 3.1), wNoise(bp * 1.6 + 7.7)) - 0.5) * 0.35;
        float lines = 1.0 - step(0.018 + 0.03 * stir, cellEdge(cp, uTime * 0.25));        // thin lines, small cells,
        lines *= step(0.66 - 0.3 * stir, wNoise(bp * 0.09 + uTime * 0.012));             // only in patches here and there
        // the thin shore foam, a dark inked line just outside it, and a second ring that pulses in and out
        float fl = 1.0 - step(0.09, shore + wob * 0.5);
        float ink = (1.0 - step(0.15, shore + wob * 0.5)) * (1.0 - fl);
        float ring = 1.0 - step(0.035, abs(shore - (0.32 + 0.06 * sin(uTime * 0.9)) + wob * 0.4));
        // sparkles that blink, in the sun
        float spark = (1.0 - step(0.035, cellDot(bp * 2.2, uTime * 0.6))) * step(0.62, wNoise(bp * 0.5 + uTime * 0.35)) * uSun;
        float white = clamp(max(max(lines * 0.85, max(fl, ring * 0.8)), max(spark, foam)), 0.0, 1.0) * step(0.0, shore);
        diffuseColor.rgb = mix(diffuseColor.rgb, uDeep * 0.6, ink * 0.6 * step(0.0, shore));
        diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.91, 0.98, 1.0), white);
        diffuseColor.a = max(diffuseColor.a, white * 0.95);`)
      .replace('#include <opaque_fragment>', `float fres = pow(1.0 - saturate(dot(normalize(vViewPosition), normal)), 4.0);
        outgoingLight = mix(diffuseColor.rgb, outgoingLight, 0.3);                    // flat painted colour, with a hint of shadow
        outgoingLight = mix(outgoingLight, uSky, fres * 0.35);                          // and the sky toward the horizon
        #include <opaque_fragment>`);
  };
  return m;
}

export function buildTerminal() {
  const w = makeWorld('terminal', 'The Terminal');
  const s = w.scene;
  w.groundY = PZ;
  w.spawn.copy(B(PX - 3.5, PY - 1.2, PZ)); w.spawnYaw = Math.PI / 2;
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
    uShallow: { value: new THREE.Color() }, uDeep: { value: new THREE.Color() }, uSky: { value: new THREE.Color() }, uTrain: { value: new THREE.Vector3(1e4, 0, 25) }, uPlayer, uStir: { value: 0 }, uSun: { value: 1 },
    uPorch: { value: new THREE.Vector4(...PORCH) }, uTower: { value: new THREE.Vector3(...TOWER) } };
  const water = new THREE.Mesh(new THREE.PlaneGeometry(900, 900).rotateX(-Math.PI / 2), makeWater(U));
  water.position.set(55, 0, 0); water.receiveShadow = true; water.renderOrder = 1; water.userData.noShadow = true;
  s.add(water);
  const hideInMirror = [];                                                          // (the old mirror water's list; kept for the grass and spray)
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
  const BUSH = /^c_(3a8547|6fb04f|2a6643)/;                                       // bushes, planter shrubs, potted plants
  const isBush = (m) => BUSH.test(m.name || '');
  w.glowMats = [];
  w.ready = loadLayout('models/terminal', s, (n, of) => w.progress(n, of), (name, model) => {
    if (/^tree_|^pine$/.test(name)) leafify(model, name === 'pine' ? 'pine' : 'broad', isCanopy, gradient(), { clumps: true });   // each puff gets its own round light
    if (/^islet_|^fences_planters$|^station_props$/.test(name)) leafify(model, 'bush', isBush, gradient(), { clumps: true });
  }, ['train', 'utility_pole', 'utility_pole_lamp', 'utility_pole_transformer', 'platform', 'station_building', 'canopy', 'bench', 'vending_machine', 'bin',
      'canopy_signs', 'fences_planters', 'platform_lamp', 'station_props', 'lantern_string', 'roof_extras', 'mooring', 'chair', 'suitcase', 'cat', 'boat', 'causeway',
      'halt', 'fish', 'heron', 'heron_flying', 'rail', ...V1_SCENERY]).then((r) => {   // the v1 station and scenery are gone: the porch (below)
    placed = r.placed; w.glowMats.push(...r.glow); w.loaded = true;
    const sg = (placed.station_sign || [])[0];                                  // the station sign stands on the porch's lower level
    if (sg) { sg.position.copy(B(PX + 4.3, PY - 1.85, LOW)); sg.scale.setScalar(SIGN_K); }
    buildSeabed([]);                                                               // (no islets for now: built from zero)
  });
  // The train: "Spirited Away Train" by judpro (CC BY 4.0), prepared by blender/scenes/import_train.py. Its cab is at y = 0,
  // it runs along +y, so turned to run along +x it leads with the cab toward -x, the way it travels here.
  const trainReady = loadModel('models/terminal/seatrain.glb', { smoothMaps: true }).then(({ scene, glow }) => {
    train = scene;
    train.rotation.y = -Math.PI / 2; train.position.set(1e4, -0.05, -TRACK);
    // its textures are dark and weathered: give it a soft light ramp, and brighten it by day (see applySky)
    const soft = new THREE.DataTexture(new Uint8Array([170, 170, 170, 255, 215, 215, 215, 255, 245, 245, 245, 255, 255, 255, 255, 255]), 4, 1, THREE.RGBAFormat);
    soft.minFilter = soft.magFilter = THREE.LinearFilter; soft.needsUpdate = true;
    train.traverse((o) => { if (o.isMesh) for (const m of [].concat(o.material)) if (!trainMats.includes(m)) { m.userData.base = m.color.clone(); recolor(m); trainMats.push(m); } });   // the usual crisp toon ramp
    s.add(train); nextTrain = 6;
    return glow;
  });
  // ---------- the porch on the ruin (blender/assets/halt.py), the rail, the boat, the heron and the fish ----------
  let heronSpot = null;
  const porchReady = loadModel('models/terminal/halt.glb').then(({ scene, glow }) => {
    scene.position.copy(B(PX, PY, 0)); s.add(scene);
    leafify(scene, 'bush', isBush, gradient(), { clumps: true });                 // its bushes, ivy and grass: v1's leaf cards
    w.camBlockers = [scene];                                                       // the camera pulls in rather than pass through
    const hs = scene.getObjectByName('heron_spot'); if (hs) { scene.updateMatrixWorld(true); heronSpot = hs.getWorldPosition(new THREE.Vector3()); }
    return glow;
  });
  const railReady = loadModel('models/terminal/rail.glb').then(({ scene }) => {   // a 12 m stretch, repeated along the line
    for (let i = 0; i < 20; i++) { const o = i ? scene.clone() : scene; o.position.copy(B(-64 + 12 * i, TRACK, RAIL_Z)); s.add(o); }
    return [];
  });
  let boat = null;
  const boatReady = loadModel('models/terminal/boat.glb').then(({ scene }) => {
    boat = scene; boat.position.copy(B(PX + 1.3, PY + 6.3, -0.12)); boat.rotation.y = 0.3; s.add(boat);
    return [];
  });
  const heron = { stand: null, fly: null, wings: [], state: 'gone', t: 0, wait: 0 };
  const heronReady = Promise.all([loadModel('models/terminal/heron.glb'), loadModel('models/terminal/heron_flying.glb')]).then(([a, b]) => {
    heron.stand = a.scene; heron.fly = b.scene; a.scene.visible = b.scene.visible = false; s.add(a.scene, b.scene);
    heron.wings = ['heron_wing_l', 'heron_wing_r'].map((n) => b.scene.getObjectByName(n));
    return [];
  });
  const fishes = [];
  const fishReady = loadModel('models/terminal/fish.glb').then(({ scene }) => {
    for (let i = 0; i < 5; i++) {
      const o = i ? scene.clone() : scene; o.scale.setScalar(0.9 + Math.random() * 0.4); s.add(o);
      fishes.push({ o, r: 0.8 + Math.random() * 1.6, sp: (0.25 + Math.random() * 0.25) * (Math.random() < 0.5 ? -1 : 1), ph: Math.random() * 6.28, dz: 0.18 + Math.random() * 0.1 });
    }
    return [];
  });
  w.ready = Promise.all([w.ready, trainReady, porchReady, railReady, boatReady, heronReady, fishReady]).then((all) => { for (const g of all.slice(1)) w.glowMats.push(...(g || [])); });
  let trees = [], train = null, nextTrain = 1e9;

  // ---------- light shafts: soft beams of sun slanting down through the tree crowns ----------
  // Each beam is a long quad hung from under a canopy along the sun's direction, turned every frame to face the camera
  // around that axis. Brightest with a low sun, gone at night and under cloud, flickering as the leaves move.
  const shafts = [];
  const shaftTex = (() => {
    const c = document.createElement('canvas'); c.width = 64; c.height = 256; const g = c.getContext('2d');
    const img = g.createImageData(64, 256);
    for (let y = 0; y < 256; y++) for (let x = 0; x < 64; x++) {
      const v = y / 255, u = (x / 63) * 2 - 1;
      const along = Math.min(1, v / 0.12) * Math.pow(1 - v, 1.6);             // fades in under the leaves, out toward the ground
      const across = Math.exp(-u * u * 3.2);
      const a = along * across;
      img.data.set([255, 255, 255, Math.round(a * 255)], (y * 64 + x) * 4);
    }
    g.putImageData(img, 0, 0);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
  })();
  const shaftMat = new THREE.MeshBasicMaterial({ map: shaftTex, color: 0xfff0c8, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false });
  const shaftGeo = new THREE.PlaneGeometry(1, 1).translate(0, -0.5, 0);      // top edge at the origin, hanging down
  function makeShafts(objs) {
    let seed = 17; const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
    for (const o of objs) {
      const box = new THREE.Box3().setFromObject(o), size = box.getSize(new THREE.Vector3()), c = box.getCenter(new THREE.Vector3());
      const under = box.min.y + size.y * 0.55;                                 // just under the leaves
      const n = 3 + Math.floor(rnd() * 3);
      for (let i = 0; i < n; i++) {
        const a = rnd() * 6.283, d = Math.sqrt(rnd()) * Math.min(size.x, size.z) * 0.32;
        const m = new THREE.Mesh(shaftGeo, shaftMat.clone());
        m.userData = { top: new THREE.Vector3(c.x + Math.cos(a) * d, under + rnd() * size.y * 0.15, c.z + Math.sin(a) * d), width: 0.5 + rnd() * 1.1, ph: rnd() * 6.28, sp: 0.4 + rnd() * 0.6, k: 0.6 + rnd() * 0.4 };
        m.renderOrder = 3; m.frustumCulled = false; m.userData.noShadow = true; m.matrixAutoUpdate = false;
        s.add(m); shafts.push(m); hideInMirror.push(m);
      }
    }
  }
  const camP = new THREE.Vector3(), ax = new THREE.Vector3(), side = new THREE.Vector3(), nrm = new THREE.Vector3(), toCam = new THREE.Vector3();
  function updateShafts(t, camera) {
    // strength: the sun has to be up and not behind cloud; a lower sun makes longer, more visible beams
    const up = THREE.MathUtils.clamp((P.sunI - 0.6) / 1.6, 0, 1), low = 1 - Math.max(0, sd.y) * 0.55;
    const k = up * (1 - 0.85 * cloudy) * low;
    for (const m of shafts) m.visible = k > 0.02;
    if (k <= 0.02) return;
    ax.copy(sd).negate();                                                      // the way the light travels
    if (ax.y > -0.25) ax.y = -0.25; ax.normalize();
    camera.getWorldPosition(camP);
    for (const m of shafts) {
      const u = m.userData, L = Math.max(1, (u.top.y + 0.1) / -ax.y);          // reach the ground (or the water)
      toCam.subVectors(camP, u.top);
      side.crossVectors(ax, toCam).normalize(); nrm.crossVectors(side, ax).normalize();
      m.matrix.makeBasis(side.clone().multiplyScalar(u.width), ax.clone().negate().multiplyScalar(L), nrm).setPosition(u.top);
      m.matrixWorldNeedsUpdate = true;
      m.material.opacity = k * u.k * 0.5 * (0.7 + 0.3 * Math.sin(t * u.sp + u.ph));
    }
  }
  w.camera = null;                                                            // main.js hands over the camera
  const trainMats = [];
  // Repaint the train in design A's clean livery: flat maroon body, cream window band, slate roof, dark skirt. The
  // texture only says which part is which (rose/red paint vs gold paint, and how high up it is); its grime is dropped.
  // Grey parts (glass, metal, frames) keep their texture.
  const L = (hex) => { const c = new THREE.Color(hex); return `vec3(${c.r.toFixed(4)}, ${c.g.toFixed(4)}, ${c.b.toFixed(4)})`; };
  function recolor(m) {
    if (!m.map) return;
    const prev = m.onBeforeCompile;
    m.onBeforeCompile = (sh, r) => {
      if (prev) prev(sh, r);
      sh.vertexShader = 'varying float vTH;\n' + sh.vertexShader.replace('#include <begin_vertex>', '#include <begin_vertex>\nvTH = (modelMatrix * vec4(transformed, 1.0)).y + 0.05;');
      sh.fragmentShader = 'varying float vTH;\n' + sh.fragmentShader;
      sh.fragmentShader = sh.fragmentShader.replace('#include <map_fragment>', `#include <map_fragment>
        {
          vec3 c = diffuseColor.rgb;
          float mx = max(c.r, max(c.g, c.b)), mn = min(c.r, min(c.g, c.b)), d = mx - mn, sat = mx > 0.0 ? d / mx : 0.0;
          float h = 0.0;
          if (d > 1e-4) { if (mx == c.r) h = mod((c.g - c.b) / d, 6.0); else if (mx == c.g) h = (c.b - c.r) / d + 2.0; else h = (c.r - c.g) / d + 4.0; h /= 6.0; }
          float lum = dot(c, vec3(0.3, 0.59, 0.11));
          float red  = smoothstep(0.12, 0.3, sat) * (1.0 - smoothstep(0.03, 0.07, min(h, 1.0 - h)));
          float gold = smoothstep(0.1, 0.25, sat) * smoothstep(0.04, 0.07, h) * (1.0 - smoothstep(0.17, 0.22, h));
          float roof = smoothstep(2.72, 2.8, vTH), skirt = 1.0 - smoothstep(0.85, 1.0, vTH);
          float tex = 0.9 + 0.1 * clamp(lum / 0.35, 0.0, 1.6);                   // only a whisper of the old texture: clean paint
          vec3 MAROON = ${L(0x8A2A36)}, CREAM = ${L(0xE6C47C)}, SLATE = ${L(0x4D5655)}, IRON = ${L(0x2E2D33)};
          vec3 body = mix(MAROON, SLATE, roof), band = mix(CREAM, IRON, skirt);
          c = mix(c, body * tex, red);
          c = mix(c, mix(band, SLATE, roof) * tex, gold);
          diffuseColor.rgb = c;
        }`);
    };
    m.customProgramCacheKey = () => 'train-recolor';
    m.needsUpdate = true;
  }
  const TINT = new THREE.Color();

  // ---------- 3D grass on the islets ----------
  function plantGrass(islets) {
    const perM2 = matchMedia('(pointer: coarse)').matches ? 22 : 55;
    let seed = 3; const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
    hideInMirror.push(grassField(s, gradient(), (add) => {
      for (const [x, y, r] of islets) {
        const R = r * 0.86 * 0.96, n = Math.round(Math.PI * R * R * perM2);
        for (let i = 0; i < n; i++) {
          const a = rnd() * 6.283, d = Math.sqrt(rnd()) * R;
          if (d < 0.45) continue;                                                  // not inside the trunk
          const bx = x + Math.cos(a) * d, by = y + Math.sin(a) * d;
          add(bx, 0.08 + 0.2 * r * 0.86 * Math.sqrt(Math.max(0, 1 - (d / (r * 0.86)) ** 2)), -by);
        }
      }
    }, { max: perM2 > 30 ? 60000 : 24000 }));
  }

  // The station name, drawn here so the Korean stays crisp (covers the board on the Blender sign).
  const sk = SIGN_K / 0.8;                                                         // (the Blender sign is drawn at 0.8)
  const name = sign(s, ['어딘가', 'SOMEWHERE  ·  ENTAH DI MANA', '←  Semarang                    Seoul  →'], 2.1 * sk, 0.82 * sk, PX + 4.3, LOW + 1.51 * sk, -(PY - 1.85 - 0.045 * SIGN_K),
    { size: [0.34 * sk, 0.12 * sk, 0.11 * sk], fg: ['#2f3b52', '#5a6478', '#b0563f'], bg: '#f6eedb', res: 200 });
  name.material = new THREE.MeshToonMaterial({ map: name.material.map });


  // ---------- painted cumulus, drifting with the wind ----------
  const cm = cumulusMaterial();
  const WIND = new THREE.Vector3(1.4, 0, 0.35);
  const clouds = [];
  // a busy summer sky: a ring of big towers far out, and plenty of smaller puffs at every distance and height
  const CLOUDS = [];
  for (let i = 0; i < 12; i++) CLOUDS.push([(i / 12) * 6.283 + Math.random() * 0.4, 210 + Math.random() * 90, 6 + Math.random() * 20, 55 + Math.random() * 45]);
  for (let i = 0; i < 26; i++) CLOUDS.push([Math.random() * 6.283, 110 + Math.random() * 190, 25 + Math.random() * 55, 14 + Math.random() * 26]);
  CLOUDS.forEach(([a, r, y, wd], i) => {
    const c = cumulus(s, cm, 55 + Math.cos(a) * r, y, Math.sin(a) * r, wd, i + 1);
    c.userData.bob = Math.random() * 6.28; clouds.push(c);
  });
  // the heavy layer: big low clouds right overhead, which only gather when the weather turns cloudy
  const heavy = [];
  for (let i = 0; i < 14; i++) {                                                  // about as many as the smooth Blender dusk render
    const a = (i / 14) * 6.283 + Math.random() * 0.35, r = 130 + Math.random() * 130;
    const c = cumulus(s, cm, 30 + Math.cos(a) * r, -4 + Math.random() * 14, Math.sin(a) * r, 80 + Math.random() * 70, 100 + i);
    c.userData.bob = Math.random() * 6.28; c.userData.k = Math.random(); c.visible = false; clouds.push(c); heavy.push(c);
  }
  let cloudy = weatherNow();

  // ---------- gulls ----------
  const gulls = [];
  const gullMat = new THREE.MeshToonMaterial({ color: 0xffffff, side: THREE.DoubleSide });

  // ---------- spray thrown up by the train ----------
  const SN = 420, sp = new Float32Array(SN * 3), sv = new Float32Array(SN * 3), life = new Float32Array(SN);
  const sgeo = new THREE.BufferGeometry(); sgeo.setAttribute('position', new THREE.BufferAttribute(sp, 3));
  const spray = new THREE.Points(sgeo, new THREE.PointsMaterial({ size: 0.28, map: softDot(), transparent: true, depthWrite: false, color: 0xffffff, opacity: 0.85 }));
  spray.frustumCulled = false; spray.renderOrder = 2; s.add(spray); hideInMirror.push(spray);
  for (let i = 0; i < SN; i++) sp[i * 3 + 1] = -50;
  let emitAcc = 0, spawnI = 0;

  // ---------- night lights on the platform ----------
  const lamps = [B(PX - 0.4, PY - 0.31, PZ + 2.09), B(PX + 3.6, PY - 0.31, PZ + 2.09)].map((p) => {           // the lanterns on the wall
    const l = new THREE.PointLight(0xffb870, 0, 13, 1.6); l.position.copy(p); s.add(l); return l;
  });

  // ---------- walking, collisions, things to look at ----------
  // Where you can walk: the porch (upper front, back, the stairs down to the lower front level), its back stairs down
  // into the water, the wooden deck, the islets behind it, and the shallow water all round them (you wade). The porch
  // sits at (PX, PY); everything below is in its own coordinates (lx, ly), Blender-style. Islet data arrives with the models.
  let ISL = [];
  const NORTH = () => ISL.filter(([, y]) => y > 9);
  const L_ = (bx, by) => [bx - PX, by - PY];
  const onPier = (lx, ly) => Math.abs(lx) < 5.45 && Math.abs(ly) < 2.25 && Math.hypot(lx + 7.0, ly + 0.55) > 2.6;
  const onDeck = (lx, ly) => lx > 3.15 && lx < 4.55 && ly >= 2.25 && ly < 4.85;
  const stairOut = (lx, ly) => Math.max(ly - 2.3, -5.5 - lx);                     // how far out from the porch on the back stairs
  const onBackStairs = (lx, ly) => lx > -6.45 && lx < -3.35 && ly > 1.1 && ly < 3.2 && stairOut(lx, ly) > -0.05 && Math.hypot(lx + 7.0, ly + 0.55) > 2.6;
  const isletTop = (bx, by) => {                                                   // height of the sand and grass mounds (Blender z)
    let h = -1;
    for (const [x, y, r] of ISL) {
      const d = Math.hypot(bx - x, by - y), R = r * 0.86;
      if (d < r) h = Math.max(h, -0.05 + 0.16 * r * Math.sqrt(1 - (d / r) ** 2));
      if (d < R) h = Math.max(h, 0.08 + 0.2 * R * Math.sqrt(1 - (d / R) ** 2));
    }
    return h;
  };
  const wading = (bx, by) => {
    const [lx, ly] = L_(bx, by);
    if (by < PY - 0.6 || Math.abs(lx) < 5.5 && Math.abs(ly) < 2.3 || Math.hypot(lx + 7.0, ly + 0.55) < 2.6) return false;
    return bx > -22 && bx < 46 && by < 19 && seaDepth(bx, by, ISL) < 0.62;
  };
  w.inside = (x, z) => {
    const bx = x, by = -z, [lx, ly] = L_(bx, by);
    if (onPier(lx, ly) || onDeck(lx, ly) || onBackStairs(lx, ly)) return true;
    return NORTH().some(([ix, iy, ir]) => Math.hypot(bx - ix, by - iy) < ir * 0.93) || wading(bx, by);
  };
  w.heightAt = (x, z) => {
    const bx = x, by = -z, [lx, ly] = L_(bx, by);
    if (onPier(lx, ly)) return ly < 0.04 ? PZ - (PZ - LOW) * THREE.MathUtils.clamp((lx - 1.05) / 0.9, 0, 1) : PZ;   // the front stairs down
    if (onDeck(lx, ly)) return PZ + 0.06;
    if (onBackStairs(lx, ly)) return PZ - PZ * THREE.MathUtils.clamp(stairOut(lx, ly) / 1.0, 0, 1);
    return Math.max(isletTop(bx, by), -0.3);                                       // on an islet, or wading
  };
  const S = (bx, by, sx, sy) => w.solid(bx, -by, sx, sy);
  S(PX + 1.2, PY + 0.39, 8.3, 0.75);                                               // the tall wall
  S(PX - 0.9, PY - 0.41, 2.6, 0.55);                                               // the seats
  S(PX + 3.55, PY + 4.6, 0.6, 0.3);                                                // the mooring post
  for (const sx of [-1, 1]) S(PX + 4.3 + sx * 0.87 * SIGN_K / 0.6, PY - 1.85, 0.3, 0.3);   // the sign's posts

  const SEAT = { x: PX - 1.21, y: PY - 0.41 };                                      // the second of the four seats
  w.hot(SEAT.x, -SEAT.y, 'Sit down and wait for the train', 'sit', { y: 1.7, r: 1.6 });
  w.hot(PX + 2.43, -(PY + 0.01), 'Read the timetable', 'welcome', { y: 1.9, r: 1.3 });
  w.hot(PX + 3.77, -(PY + 0.01), 'Read the notices', 'contact', { y: 1.8, r: 1.2 });
  w.hot(PX + 4.3, -(PY - 1.85), 'Read the station sign', 'station', { y: 2.0, r: 1.5 });

  w.seat = { pos: B(SEAT.x, SEAT.y, PZ), yaw: 0 };
  w.standSpot = B(SEAT.x, SEAT.y - 0.7, PZ);

  // ---------- the dimension crack ----------
  const CX = SEAT.x, CZ = -TRACK;                                                  // where it opens: over the line, in front of the seat
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
  const GREY = { top: new THREE.Color(0x6f7f9c), mid: new THREE.Color(0xc7c9d4), shade: new THREE.Color(0x7d8299), water: new THREE.Color(0x7aa6a8), lit: new THREE.Color(0xf2efe6) };
  let moodK = 0;
  function applySky(h) {
    paletteAt(h, P);
    const k = h > 6 && h < 19.5 ? moodK : 0;                                       // the cutscene drifts into dusk (by day)
    const p = k > 0 ? mixPal(Q, P, DUSK, k) : P;
    // overcast: the sun dims and the shadows fade, the sky goes greyer, clouds darken underneath
    const c = cloudy;
    if (c > 0.001) {
      p.sunI *= 1 - 0.6 * c; p.hemiI *= 1 + 0.15 * c;
      p.top.lerp(GREY.top, c * 0.55); p.mid.lerp(GREY.mid, c * 0.45); p.fog.lerp(GREY.mid, c * 0.4);
      p.cShade.lerp(GREY.shade, c * 0.75); p.cLit.lerp(GREY.lit, c * 0.25); p.shallow.lerp(GREY.water, c * 0.3);
    }
    SU.a.value.copy(p.top); SU.b.value.copy(p.mid); SU.c.value.copy(p.bot);
    sunDir(h, sd); SU.sun.value.copy(sd); SU.sc.value.copy(p.sun); SU.sk.value = 1 - 0.85 * cloudy;      // the sun disc hides behind overcast
    w.sun.color.copy(p.sun); w.sun.intensity = p.sunI; w.sun.userData.offset.copy(sd).multiplyScalar(40);
    hemi.color.copy(p.sky); hemi.groundColor.copy(p.ground); hemi.intensity = p.hemiI;
    s.fog.color.copy(p.fog);
    U.uShallow.value.copy(p.shallow); U.uDeep.value.copy(p.deep); U.uSky.value.copy(p.mid);
    U.uSun.value = THREE.MathUtils.clamp((p.sunI - 0.8) / 1.6, 0, 1) * (1 - 0.8 * cloudy);   // sparkles need the sun
    cm.uniforms.lit.value.copy(p.cLit); cm.uniforms.shade.value.copy(p.cShade); cm.uniforms.edge.value.copy(p.cEdge); cm.uniforms.sun.value.copy(sd); cm.uniforms.haze.value.copy(p.mid);
    starField.material.opacity = p.stars;
    for (const l of lamps) l.intensity = p.lamps * 9;
    for (const m of w.glowMats) m.emissiveIntensity = m.userData.glow * (0.25 + 0.75 * Math.max(p.lamps, 0.2));
    w.bloom = p.bloom;
    const day = THREE.MathUtils.clamp((p.sunI - 0.45) / 2.55, 0, 1);              // 0 at night .. 1 at noon
    const kT = 0.95 + 0.15 * day;
    for (const m of trainMats) m.color.copy(m.userData.base).multiplyScalar(kT);
  }

  // ---------- the train ----------
  const TRAIN_LEN = 23.64;
  let run = null;                                                                  // { x, v } while a train is on the line
  const startRun = (x, v) => { run = { x, v }; };
  Object.defineProperty(w, 'trainX', { get: () => (run ? run.x : null) });
  w.holdTrain = (x, v = 0) => startRun(x, v);                                      // debug: put the train at x (moving at v)
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
    { t: 0, from: V([CX + 1.7, PZ + 1.6, -SEAT.y - 0.3]), to: V([CX + 1.25, PZ + 1.45, -SEAT.y - 0.15]), look: V([CX, 1.8, CZ]) },   // waiting, beside the seat
    { t: 1.5, from: V([PX - 3.6, PZ + 0.25, -(PY - 2.3) - 0.1]), to: V([PX - 3.6, PZ + 0.4, -(PY - 2.3)]), look: V([40, 1.6, CZ]) },  // the edge, the train bearing down
    { t: 3.05, from: V([CX + 2.4, PZ + 1.5, -SEAT.y + 0.5]), to: V([CX + 1.0, PZ + 1.55, -SEAT.y + 0.8]), look: V([CX, 2.4, CZ]) },  // it passes, the air tears
    { t: 5.7, from: V([CX + 0.6, PZ + 1.15, -SEAT.y - 0.1]), to: V([CX - 0.2, PZ + 0.95, -SEAT.y + 2.6]), look: V([CX, 2.6, CZ + 1]) },   // walking in
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
  const z0 = -SEAT.y, z1 = CZ + 0.2, kEdge = (-(PY - 2.3) - z0) / (z1 - z0);           // off the porch's front edge, into the crack
  w.walkIn = (k, p) => p.set(CX, PZ - (PZ - 0.02) * THREE.MathUtils.smoothstep(k, kEdge, kEdge + 0.12), z0 + k * (z1 - z0));
  w.reset = () => {
    seq = null; w.seqT = 0; moodK = 0; crack.setOpen(0); crack.setPortal(null); crackLight.intensity = 0; motes.visible = false;
    rayMat.opacity = ring.material.opacity = 0; run = null; nextTrain = 20;
    Object.assign(w.cine, { snap: false, shake: 0, glow: 0 }); w.cine.pos.copy(shots[0].from); w.cine.look.copy(shots[0].look);
  };

  // ---------- the heron, the fish, the boat ----------
  // The heron stands on its rock only in sunshine; when a train comes (or the weather turns) it takes off and flies away
  // north, and comes back a while after, if the sun is still out. The fish circle in the shallows by the back stairs; in
  // rain only two stay, under the deck.
  const FLY = new THREE.Vector3(14, 9, -24), fpos = new THREE.Vector3(), fprev = new THREE.Vector3();
  const FISH_AT = B(PX - 4.0, PY + 4.2, 0), FISH_RAIN = B(PX + 3.85, PY + 3.6, 0);
  function animals(t, dt) {
    if (boat) { boat.position.y = -0.12 + Math.sin(t * 0.8) * 0.025; boat.rotation.z = Math.sin(t * 0.6) * 0.02; boat.rotation.x = Math.sin(t * 0.7 + 1) * 0.015; }
    const rain = cloudy > 0.6;
    fishes.forEach((f, i) => {
      const here = rain ? FISH_RAIN : FISH_AT, r = rain ? 0.35 + i * 0.1 : f.r;
      f.o.visible = !rain || i < 2;
      const a = t * f.sp + f.ph;
      f.o.position.set(here.x + Math.cos(a) * r, -f.dz, here.z + Math.sin(a) * r * 0.7);
      const dx = -Math.sin(a) * Math.sign(f.sp), dz = Math.cos(a) * 0.7 * Math.sign(f.sp);
      f.o.rotation.y = Math.atan2(dz, -dx) + Math.sin(t * 6 + f.ph) * 0.12;       // facing the way it swims, tail wagging
    });
    if (!heron.stand || !heronSpot) return;
    const sunny = cloudy < 0.35 && P.sunI > 1.2;
    const trainNear = run && run.x < heronSpot.x + 45 && run.x + TRAIN_LEN > heronSpot.x - 12;
    const away = fpos.copy(heronSpot).add(FLY);
    const h = heron;
    if (h.state === 'stand' && (trainNear || !sunny)) { h.state = 'off'; h.t = 0; }
    if (h.state === 'gone') { h.wait = sunny && !trainNear ? h.wait + dt : 0; if (h.wait > 12) { h.state = 'in'; h.t = 0; } }
    if (h.state === 'off' || h.state === 'in') {
      h.t += dt / 5; const k = Math.min(1, h.t), e = h.state === 'off' ? k : 1 - k;
      fprev.copy(h.fly.position);
      h.fly.position.lerpVectors(heronSpot, away, e * e * (3 - 2 * e)); h.fly.position.y += Math.sin(Math.PI * e) * 2.5 + 0.6 * Math.min(1, e * 6);
      const d = fprev.sub(h.fly.position).negate();
      if (d.lengthSq() > 1e-6) h.fly.rotation.y = Math.atan2(d.z, -d.x);
      const flap = Math.sin(t * 8) * 0.55; if (h.wings[0]) h.wings[0].rotation.x = -flap; if (h.wings[1]) h.wings[1].rotation.x = flap;
      if (k >= 1) { h.state = h.state === 'off' ? 'gone' : 'stand'; h.wait = 0; }
    }
    if (h.state === 'stand' || (h.state === 'gone' && h.wait === 0 && sunny && !trainNear && t < 2)) h.state = 'stand';
    h.stand.visible = h.state === 'stand'; h.fly.visible = h.state === 'off' || h.state === 'in';
    if (h.stand.visible) { h.stand.position.copy(heronSpot); h.stand.rotation.y = 2.6; }
  }
  const water0 = new THREE.Vector3();
  const lastP = new THREE.Vector3(); let stir = 0;
  w.ticks.push((t, dt) => {
    U.uTime.value = t;
    const v = dt > 0 ? lastP.distanceTo(uPlayer.value) / dt : 0; lastP.copy(uPlayer.value);
    const want = v > 0.3 && v < 20 ? Math.min(1, v / 3) : 0;                       // walking through water stirs it up...
    stir += (want - stir) * Math.min(1, dt * (want > stir ? 4 : 0.6));              // ...and it settles over a few seconds
    U.uStir.value = stir;
    cloudy += (weatherNow() - cloudy) * Math.min(1, dt * 0.2);                     // weather changes ease in over a few seconds
    applySky(hourNow());
    if (w.camera && shafts.length) updateShafts(t, w.camera);
    for (const c of heavy) {                                                       // the heavy layer gathers one cloud at a time
      const g = THREE.MathUtils.clamp((cloudy - c.userData.k * 0.8) / 0.2, 0, 1);
      c.visible = g > 0.01; c.scale.setScalar(0.35 + 0.65 * g);
    }
    const gust = 1 + cloudy * 1.2;                                                 // windier when it is cloudy
    for (const c of clouds) {                                                      // drift; wrap around the far side
      c.position.addScaledVector(WIND, dt * gust); c.position.y += Math.sin(t * 0.1 + c.userData.bob) * dt * 0.15;
      water0.set(c.position.x - 55, 0, c.position.z);
      if (water0.length() > 300) c.position.set(55 - WIND.x * 280 / WIND.length() + (Math.random() - 0.5) * 160, c.position.y, -WIND.z * 280 / WIND.length() + (Math.random() - 0.5) * 160);
    }
    for (const { o, ph } of trees) { o.rotation.z = Math.sin(t * 0.9 + ph) * 0.012; o.rotation.x = Math.sin(t * 0.7 + ph * 1.3) * 0.01; }
    for (const g of gulls) {
      const u = g.userData, a = t * u.sp + u.ph;
      g.position.set(u.cx + Math.cos(a) * u.r, u.h + Math.sin(t * 0.5 + u.ph) * 0.8, u.cz + Math.sin(a) * u.r); g.rotation.y = -a;
      const flap = Math.sin(t * 7 + u.ph) * 0.45; u.wings[0].rotation.y = flap; u.wings[1].rotation.y = -flap;
    }
    animals(t, dt);
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
