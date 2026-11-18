// Loading the Blender models (models/<world>/*.glb) and giving them the painted look.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { painted, surfaceOf } from './paint.js';

const loader = new GLTFLoader();
loader.setMeshoptDecoder(MeshoptDecoder);

// Three flat tones with a soft step between them: the "cel" part of the painted look.
let ramp;
export function gradient() {
  if (ramp) return ramp;
  const tones = new Uint8Array([92, 92, 92, 255, 168, 168, 168, 255, 222, 222, 222, 255, 255, 255, 255, 255]);
  ramp = new THREE.DataTexture(tones, 4, 1, THREE.RGBAFormat);
  ramp.minFilter = ramp.magFilter = THREE.LinearFilter; ramp.needsUpdate = true;
  return ramp;
}

// A rim of light around every silhouette, like the bright outline painters give backlit shapes.
export function rimPatch(sh) {
  sh.fragmentShader = sh.fragmentShader.replace('#include <opaque_fragment>',
    'float rimK = pow(1.0 - saturate(dot(normalize(vViewPosition), normal)), 3.0);\noutgoingLight += rimK * 0.22 * (diffuseColor.rgb * 0.6 + 0.4);\n#include <opaque_fragment>');
}
function rim(m) { m.onBeforeCompile = rimPatch; m.customProgramCacheKey = () => 'rim'; return m; }

const crisp = (t) => { if (t) { t.minFilter = THREE.NearestFilter; t.magFilter = THREE.NearestFilter; t.generateMipmaps = false; t.needsUpdate = true; } return t; };

/** Swap every material for a toon one. Returns the glowing materials (lamps, windows) so they can follow the time of day. */
export function toon(object, opts = {}) {      // opts.smoothMaps: keep painted textures smooth (models made outside our pipeline)
  const done = new Map(), glow = [];
  object.traverse((o) => {
    if (!o.isMesh) return;
    const swap = (m) => {
      if (done.has(m)) return done.get(m);
      const t = new THREE.MeshToonMaterial({
        color: m.color, map: m.map && opts.smoothMaps ? m.map : crisp(m.map), gradientMap: gradient(), vertexColors: m.vertexColors,
        emissive: m.emissive, emissiveMap: crisp(m.emissiveMap), emissiveIntensity: m.emissiveIntensity ?? 1, side: m.side,
        transparent: m.transparent, opacity: m.opacity, depthWrite: !m.transparent,
      });
      t.name = m.name;
      const kind = surfaceOf(m);                                        // grass, sand, concrete, wood... get a hand-painted texture
      if (kind) painted(t, kind, rimPatch); else rim(t);
      if (m.emissiveMap || (m.emissive && m.emissive.getHex() !== 0)) { t.userData.glow = t.emissiveIntensity; glow.push(t); }
      done.set(m, t);
      return t;
    };
    o.material = Array.isArray(o.material) ? o.material.map(swap) : swap(o.material);
    o.castShadow = o.receiveShadow = true;
  });
  return glow;
}

/** Load every model a world's layout needs, then place each piece. Blender is z-up, so (x, y, z) becomes (x, z, -y). */
/** Load one model outside the layout, with the same painted look. */
export async function loadModel(url, opts = {}) {
  const gltf = await loader.loadAsync(url);
  return { scene: gltf.scene, glow: toon(gltf.scene, opts) };
}

export async function loadLayout(dir, parent, onProgress = () => {}, prepare = () => {}, skip = []) {
  const layout = await (await fetch(`${dir}/layout.json`)).json();
  layout.pieces = layout.pieces.filter((p) => !skip.includes(p.name));
  const names = [...new Set(layout.pieces.filter((p) => p.model).map((p) => p.name))];
  const models = {}, glow = [];
  let done = 0;
  await Promise.all(names.map(async (n) => {
    const gltf = await loader.loadAsync(`${dir}/${n}.glb`);
    glow.push(...toon(gltf.scene));
    prepare(n, gltf.scene);                                           // e.g. leaves on the trees, before the copies are made
    models[n] = gltf.scene;
    onProgress(++done, names.length);
  }));
  const placed = {};
  for (const p of layout.pieces) {
    if (!p.model) continue;
    const o = placed[p.name] ? models[p.name].clone() : models[p.name];
    o.position.set(p.pos[0], p.pos[2], -p.pos[1]);
    o.rotation.y = p.rot_z;
    o.scale.setScalar(p.scale);
    parent.add(o);
    (placed[p.name] ||= []).push(o);
  }
  return { layout, placed, glow };
}
