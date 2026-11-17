// The traveller: a small, smooth figure with jointed limbs, flowing hair and a long red cardigan.
import * as THREE from 'three';
import { M } from './kit.js';

const SKIN = 0xf6d2b3, HAIR = 0x241d24, RED = 0xd8364a, CREAM = 0xfff0dc, NAVY = 0x34406e, SHOE = 0x5a3a36;

function part(parent, geo, color, x = 0, y = 0, z = 0, o) {
  const m = new THREE.Mesh(geo, M(color, o));
  m.position.set(x, y, z); parent.add(m); return m;
}
function joint(parent, x = 0, y = 0, z = 0) { const g = new THREE.Group(); g.position.set(x, y, z); parent.add(g); return g; }
const capsule = (r, len) => new THREE.CapsuleGeometry(r, len, 6, 14);

// A strip of cloth that hangs from its top edge and trails behind when moving.
function cloth(parent, w, h, color, wrap, flare, y, z) {
  const geo = new THREE.PlaneGeometry(w, h, 8, 10);
  const base = geo.attributes.position.array.slice();
  const mesh = new THREE.Mesh(geo, M(color, { side: THREE.DoubleSide }));
  mesh.position.set(0, y, z); parent.add(mesh);
  mesh.sway = (t, trail, gust) => {
    const p = geo.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const bx = base[i * 3], by = base[i * 3 + 1], k = (h / 2 - by) / h;      // k: 0 at the top edge, 1 at the hem
      const a = (bx / w) * wrap, r = w / wrap * (1 + k * flare);                 // wrap the strip around the back
      const ripple = Math.sin(t * 5 - k * 5 + bx * 6) * 0.035 * k * (0.4 + trail) + Math.sin(t * 1.6 + k * 2) * 0.02 * k;
      const back = k * k * (0.1 + trail * 0.55 + gust * 0.2) + ripple;
      p.setXYZ(i, Math.sin(a) * r, by + k * k * trail * 0.16, -Math.cos(a) * r + w / wrap - back);
    }
    p.needsUpdate = true; geo.computeVertexNormals();
  };
  return mesh;
}

export function makeCharacter() {
  const root = new THREE.Group(), lean = joint(root);
  const hips = joint(lean, 0, 0.62, 0);

  // legs: hip -> knee -> foot
  const legs = [-1, 1].map((s) => {
    const hip = joint(hips, s * 0.095, 0, 0);
    part(hip, capsule(0.075, 0.2), NAVY, 0, -0.16, 0);
    const knee = joint(hip, 0, -0.32, 0);
    part(knee, capsule(0.064, 0.18), NAVY, 0, -0.14, 0);
    part(knee, new THREE.SphereGeometry(0.085, 16, 12), SHOE, 0, -0.275, 0.035).scale.set(0.9, 0.62, 1.5);
    return { hip, knee };
  });

  // torso: a cream top under an open red cardigan
  const torso = joint(hips, 0, -0.06, 0);
  const prof = (pts) => pts.map(([r, y]) => new THREE.Vector2(r, y));
  part(torso, new THREE.LatheGeometry(prof([[0.001, 0], [0.17, 0.0], [0.185, 0.08], [0.165, 0.3], [0.125, 0.48], [0.07, 0.56], [0.001, 0.57]]), 28), CREAM);
  const cardi = part(torso, new THREE.LatheGeometry(prof([[0.215, -0.04], [0.205, 0.1], [0.18, 0.32], [0.14, 0.5], [0.085, 0.575]]), 28, 0.42, Math.PI * 2 - 0.84), RED, 0, 0, 0, { side: THREE.DoubleSide });
  cardi.rotation.y = Math.PI / 2;
  const tails = cloth(torso, 0.5, 0.62, RED, 2.5, 0.35, 0.02, -0.19);

  // arms: shoulder -> elbow -> hand
  const arms = [-1, 1].map((s) => {
    const sh = joint(torso, s * 0.165, 0.49, 0);
    part(sh, new THREE.SphereGeometry(0.068, 14, 10), RED);
    part(sh, capsule(0.052, 0.15), RED, 0, -0.12, 0);
    const el = joint(sh, 0, -0.24, 0);
    part(el, capsule(0.047, 0.14), RED, 0, -0.1, 0);
    part(el, new THREE.SphereGeometry(0.05, 12, 10), SKIN, 0, -0.215, 0);
    sh.rotation.z = s * 0.14;
    return { sh, el, s };
  });

  // head
  const head = joint(torso, 0, 0.6, 0);
  part(head, capsule(0.05, 0.05), SKIN, 0, 0.0, 0);
  const face = part(head, new THREE.SphereGeometry(0.2, 28, 20), SKIN, 0, 0.2, 0); face.scale.set(1, 0.96, 0.95);
  const dark = new THREE.MeshBasicMaterial({ color: 0x2a2228 });
  const eyes = [-1, 1].map((s) => { const e = new THREE.Mesh(new THREE.SphereGeometry(0.022, 10, 8), dark); e.position.set(s * 0.072, 0.2, 0.178); e.scale.set(1, 1.45, 0.5); head.add(e); return e; });
  for (const s of [-1, 1]) {
    const ring = new THREE.Mesh(new THREE.TorusGeometry(0.052, 0.007, 6, 22), dark); ring.position.set(s * 0.072, 0.2, 0.19); head.add(ring);
    const blush = new THREE.Mesh(new THREE.CircleGeometry(0.03, 14), new THREE.MeshBasicMaterial({ color: 0xff9a9a, transparent: true, opacity: 0.45 })); blush.position.set(s * 0.115, 0.135, 0.158); blush.rotation.y = s * 0.6; head.add(blush);
  }
  const bridge = new THREE.Mesh(new THREE.CylinderGeometry(0.005, 0.005, 0.045, 6), dark); bridge.rotation.z = Math.PI / 2; bridge.position.set(0, 0.205, 0.195); head.add(bridge);
  // hair: a cap tilted back off the forehead, a fringe, and a long curtain that flows
  const cap = part(head, new THREE.SphereGeometry(0.215, 28, 18, 0, Math.PI * 2, 0, Math.PI * 0.56), HAIR, 0, 0.21, -0.012); cap.rotation.x = -0.42;
  for (const s of [-1, 1]) { const f = part(head, new THREE.SphereGeometry(0.1, 14, 10), HAIR, s * 0.105, 0.325, 0.105); f.scale.set(1.15, 0.5, 0.75); f.rotation.z = -s * 0.5; }
  const hair = cloth(head, 0.5, 0.56, HAIR, 2.9, -0.12, 0.0, -0.13);

  root.traverse((o) => { if (o.isMesh) o.castShadow = true; });

  let runK = 0, phase = 0, walk = 0, sit = 0, blink = 0, turn = 0, lastYaw = 0;
  const L = THREE.MathUtils.lerp;
  // speed: 0..1 how fast we're moving. sitting: true while on the chair.
  root.animate = (t, dt, speed, sitting) => {
    // speed: 0..1 walks, above 1 blends into a run (1.8 = full run)
    walk = L(walk, Math.min(1, speed), 1 - Math.exp(-dt * 9));
    runK = L(runK, THREE.MathUtils.clamp((speed - 1) / 0.8, 0, 1), 1 - Math.exp(-dt * 7));
    sit = L(sit, sitting ? 1 : 0, 1 - Math.exp(-dt * 6));
    phase += dt * (5 + 6.5 * walk + 4.5 * runK) * Math.min(1, walk * 3);
    let dy = root.rotation.y - lastYaw; dy = Math.atan2(Math.sin(dy), Math.cos(dy)); lastYaw = root.rotation.y;
    turn = L(turn, THREE.MathUtils.clamp(dy / Math.max(dt, 0.001), -4, 4), 1 - Math.exp(-dt * 6));
    const up = 1 - sit, breathe = Math.sin(t * 1.9);

    legs.forEach(({ hip, knee }, i) => {
      const ph = phase + i * Math.PI;
      hip.rotation.x = L(-Math.sin(ph) * (0.72 * walk + 0.28 * runK), -1.5, sit);
      knee.rotation.x = L((0.12 + Math.max(0, Math.sin(ph - 1.1)) * (1.25 + 0.7 * runK)) * walk, 1.45, sit);
    });
    arms.forEach(({ sh, el, s }, i) => {
      const ph = phase + (i + 1) * Math.PI;
      sh.rotation.x = L(-Math.sin(ph) * (0.62 * walk + 0.4 * runK) + breathe * 0.02, -0.55, sit);
      el.rotation.x = L(-(0.18 + 0.5 * walk + 0.75 * runK + Math.max(0, -Math.sin(ph)) * 0.35 * walk), -0.75, sit);
      sh.rotation.z = s * (0.14 + 0.05 * walk + 0.1 * sit);
    });
    hips.position.y = 0.62 + Math.abs(Math.sin(phase)) * (0.045 * walk + 0.06 * runK) * up - 0.03 * sit + breathe * 0.004;
    hips.position.z = -0.05 * sit;
    hips.rotation.y = Math.sin(phase) * 0.1 * walk;
    torso.rotation.y = -Math.sin(phase) * 0.16 * walk;
    torso.scale.y = 1 + breathe * 0.012;
    lean.rotation.x = (0.17 * walk + 0.2 * runK) * up;
    lean.rotation.z = -turn * 0.05 * walk;
    head.rotation.x = -0.1 * walk + Math.sin(t * 0.7) * 0.04 * (1 - walk) - 0.08 * sit;
    head.rotation.y = Math.sin(t * 0.45) * 0.14 * (1 - walk) + turn * 0.06;
    head.rotation.z = Math.sin(t * 0.6 + 1) * 0.03;

    blink -= dt; if (blink < -0.13) blink = 2 + Math.random() * 3.5;
    const ey = blink < 0 ? 0.15 : 1.45; eyes.forEach((e) => { e.scale.y = ey; });

    const gust = 0.5 + Math.sin(t * 0.8) * 0.5;
    tails.sway(t, (walk + runK * 0.6) * up, gust * 0.5); hair.sway(t + 1.3, walk * 0.8 + runK * 0.5, gust * 0.4);
  };
  return root;
}
