// 3D grass: thousands of individual blades on the GPU. Each blade sways in rolling gusts of wind and bends away from
// whoever walks through it. Blades are lit like the ground beneath them (their normals point up), which keeps a field
// reading as one soft painted mass rather than thousands of flickering slivers.
import * as THREE from 'three';
import { uTime, uPlayer } from './kit.js';

// Greens from cool shade to warm light; patches of tone come from a slow noise over the ground.
const TONES = ['#2c6a3d', '#3a7f41', '#4e9644', '#6aad48', '#8cc352', '#b3d862'].map((h) => new THREE.Color(h));

function bladeGeometry() {
  const g = new THREE.PlaneGeometry(1, 1, 1, 4).translate(0, 0.5, 0), p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const y = p.getY(i);
    p.setX(i, p.getX(i) * 0.075 * Math.pow(1 - y, 0.9));              // tapers to a point
    p.setZ(i, y * y * 0.18);                                           // a little natural curve
  }
  const n = g.attributes.normal; for (let i = 0; i < n.count; i++) n.setXYZ(i, 0, 1, 0);
  return g;
}

/**
 * Plant grass. `spots(add)` calls add(x, y, z) for every place a blade should grow (world coordinates);
 * `density` scales how many are kept (lower on phones).
 */
export function grassField(scene, ramp, spots, { max = 60000 } = {}) {
  const pts = [];
  spots((x, y, z) => { if (pts.length < max) pts.push(x, y, z); });
  const count = pts.length / 3;
  const mat = new THREE.MeshToonMaterial({ color: 0xffffff, gradientMap: ramp, side: THREE.DoubleSide });
  mat.onBeforeCompile = (sh) => {
    sh.uniforms.uTime = uTime; sh.uniforms.uPlayer = uPlayer;
    sh.vertexShader = 'uniform float uTime;\nuniform vec3 uPlayer;\nvarying float vBlade;\n' + sh.vertexShader.replace('#include <begin_vertex>', `#include <begin_vertex>
      float h = position.y; vBlade = h;
      vec3 root = (modelMatrix * instanceMatrix * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
      float tall = length(instanceMatrix[1].xyz);
      // wind: big slow gusts rolling across the field, plus a quick flutter
      float gust = sin(root.x * 0.22 + uTime * 1.25) * cos(root.z * 0.17 - uTime * 0.8) * 0.5 + 0.5;
      vec2 wind = vec2(1.0, 0.35) * (0.12 + 0.42 * gust) + vec2(sin(uTime * 3.1 + root.x * 2.3), cos(uTime * 2.7 + root.z * 2.1)) * 0.06;
      // bend away from the traveller's legs
      vec2 away = root.xz - uPlayer.xz; float d = length(away);
      float push = (1.0 - smoothstep(0.2, 0.85, d)) * (1.0 - smoothstep(0.6, 1.4, abs(uPlayer.y - root.y)));
      vec2 bend = wind + (away / max(d, 0.001)) * push * 1.6;
      vec3 disp = vec3(bend.x, -length(bend) * 0.45, bend.y) * h * h * tall;
      transformed += inverse(mat3(instanceMatrix)) * disp;`);
    sh.fragmentShader = 'varying float vBlade;\n' + sh.fragmentShader.replace('#include <color_fragment>', `#include <color_fragment>
      diffuseColor.rgb *= mix(0.5, 1.18, vBlade);                     // dark at the roots, sunlit at the tips`);
  };
  mat.customProgramCacheKey = () => 'grass-blades';

  const mesh = new THREE.InstancedMesh(bladeGeometry(), mat, count);
  const m = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), s = new THREE.Vector3(), p = new THREE.Vector3(), c = new THREE.Color();
  let seed = 9;
  const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
  for (let i = 0; i < count; i++) {
    const x = pts[i * 3], y = pts[i * 3 + 1], z = pts[i * 3 + 2];
    const patch = Math.sin(x * 0.45 + Math.cos(z * 0.31) * 2) * Math.cos(z * 0.38 - x * 0.12) * 0.5 + 0.5;
    q.setFromEuler(e.set((rnd() - 0.5) * 0.35, rnd() * 6.283, (rnd() - 0.5) * 0.35));
    const tall = 0.28 + rnd() * 0.32 + patch * 0.18;
    m.compose(p.set(x, y - 0.02, z), q, s.set(0.8 + rnd() * 0.8, tall, 1));
    mesh.setMatrixAt(i, m);
    mesh.setColorAt(i, c.copy(TONES[Math.min(TONES.length - 1, Math.floor((patch * 0.75 + rnd() * 0.35) * TONES.length))]));
  }
  mesh.instanceMatrix.needsUpdate = true; mesh.instanceColor.needsUpdate = true;
  mesh.receiveShadow = true; mesh.castShadow = false; mesh.frustumCulled = false; mesh.userData.noShadow = true;
  scene.add(mesh);
  return mesh;
}
