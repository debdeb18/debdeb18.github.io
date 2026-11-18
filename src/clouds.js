// Painted cumulus: towers of lumpy puffs with a flat base, shaded in flat bands (cream tops, lavender-blue shade),
// like the clouds in anime backgrounds. One merged mesh per cloud, so a whole sky is only a handful of draw calls.
import * as THREE from 'three';
import { mergeGeometries, mergeVertices } from 'three/addons/utils/BufferGeometryUtils.js';

function rng(seed) { return () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }; }
const hash = (x, y, z) => { const s = Math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453; return s - Math.floor(s); };

/** The shared material. Uniform names match what the time-of-day code already updates: lit, shade, edge, sun. */
export function cumulusMaterial() {
  return new THREE.ShaderMaterial({
    uniforms: { lit: { value: new THREE.Color(0xfbf8ee) }, shade: { value: new THREE.Color(0xa3b0cf) }, edge: { value: new THREE.Color(0xffffff) },
      sun: { value: new THREE.Vector3(0, 1, 1).normalize() }, haze: { value: new THREE.Color(0xbfe4f3) } },
    vertexShader: `attribute float hgt; varying vec3 vN, vW; varying float vH;
      void main() { vN = normalize(mat3(modelMatrix) * normal); vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz; vH = hgt; gl_Position = projectionMatrix * viewMatrix * w; }`,
    fragmentShader: `uniform vec3 lit, shade, edge, sun, haze; varying vec3 vN, vW; varying float vH;
      void main() {
        vec3 n = normalize(vN), v = normalize(cameraPosition - vW);
        float l = (dot(n, sun) * 0.5 + 0.5) * 0.72 + vH * 0.38;          // higher puffs catch more light
        vec3 mid = mix(shade, lit, 0.55);
        vec3 c = mix(shade, mid, smoothstep(0.43, 0.46, l));               // three flat bands with crisp edges
        c = mix(c, lit, smoothstep(0.6, 0.63, l));
        float rim = pow(1.0 - max(dot(n, v), 0.0), 3.0);
        c = mix(c, edge, rim * 0.35 * smoothstep(0.35, 0.6, l));          // bright rims where the light wraps round
        c = mix(c, haze, 0.06 + (1.0 - vH) * 0.06);                        // a little sky in it, more near the base
        c *= mix(0.86, 1.0, smoothstep(0.0, 0.25, vH));                   // darker undersides give the puffs weight
        gl_FragColor = vec4(c, 1.0);
      }`,
  });
}

/** Build one cumulus `w` metres wide at (x, y, z) (y = its flat base). */
export function cumulus(scene, mat, x, y, z, w, seed) {
  const r = rng(seed * 7919 + 13), puffs = [];
  const layers = 5, H = w * (0.55 + r() * 0.35);                       // height of the tower
  for (let L = 0; L < layers; L++) {
    const k = L / (layers - 1), ring = w * 0.5 * (1 - k * 0.62) * (0.85 + r() * 0.3);
    const n = Math.round(10 - k * 6), py = k * H * 0.8;
    for (let i = 0; i < n; i++) {
      const a = (i / n) * 6.283 + r() * 0.6, d = ring * (0.35 + r() * 0.65);
      const rad = w * (0.13 + r() * 0.07) * (1 - k * 0.25);
      puffs.push([Math.cos(a) * d, py + rad * 0.3, Math.sin(a) * d * 0.55, rad]);
    }
  }
  for (let i = 0; i < 3; i++) puffs.push([(r() - 0.5) * w * 0.3, H * (0.8 + r() * 0.15), (r() - 0.5) * w * 0.15, w * (0.15 + r() * 0.05)]);   // the heads
  const geos = puffs.map(([px, py, pz, rad], i) => {
    const ico = new THREE.IcosahedronGeometry(1, 3); ico.deleteAttribute('normal'); ico.deleteAttribute('uv');
    const g = mergeVertices(ico), p = g.attributes.position, v = new THREE.Vector3();   // shared vertices, so the puffs shade smoothly
    for (let j = 0; j < p.count; j++) {
      v.fromBufferAttribute(p, j);
      const bump = 1 + (hash(v.x * 2.1 + i, v.y * 2.1, v.z * 2.1) - 0.5) * 0.28;   // lumpy, cauliflower-like puffs
      v.multiplyScalar(rad * bump).add(new THREE.Vector3(px, py, pz));
      v.y = Math.max(v.y, 0);                                                       // flat bottom
      p.setXYZ(j, v.x, v.y, v.z);
    }
    g.computeVertexNormals();
    const h = new Float32Array(p.count); for (let j = 0; j < p.count; j++) h[j] = Math.min(1, p.getY(j) / H);
    g.setAttribute('hgt', new THREE.BufferAttribute(h, 1));
    return g;
  });
  const mesh = new THREE.Mesh(mergeGeometries(geos), mat);
  mesh.position.set(x, y, z); mesh.rotation.y = r() * 6.283;
  mesh.userData.noShadow = true; mesh.frustumCulled = true;
  scene.add(mesh);
  return mesh;
}
