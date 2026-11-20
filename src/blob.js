// The traveller: a soft blob with headphones (blender/assets/blob.py). No legs: it hops, squashing as it lands and
// stretching as it rises, and the squash wobbles like jelly (a spring). At rest it breathes and now and then does a
// little bounce on the spot; it blinks. Same interface as before: position, rotation, animate(t, dt, speed, sitting).
import * as THREE from 'three';
import { M } from './kit.js';
import { loadModel } from './models.js';

export function makeBlob() {
  const root = new THREE.Group();
  const hop = new THREE.Group(); root.add(hop);                 // up and down
  const squash = new THREE.Group(); hop.add(squash);            // squash and stretch, round its base
  loadModel('models/character/blob.glb').then(({ scene }) => {
    scene.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
    squash.add(scene);
  });
  const eyeMat = M(0x1e1e24);
  const eyes = [-1, 1].map((s) => {                             // the dot eyes (drawn here so they can blink)
    const e = new THREE.Mesh(new THREE.SphereGeometry(0.032, 16, 12), eyeMat);
    e.position.set(s * 0.085, 0.66, 0.426); e.scale.set(1, 1.15, 0.55); squash.add(e); return e;
  });

  const L = THREE.MathUtils.lerp;
  let walk = 0, runK = 0, sit = 0, phase = 0, blink = 2, turn = 0, lastYaw = 0, idleHop = 3, idleT = -1;
  const sp = { y: 1, v: 0 };                                     // the jelly spring on the vertical scale
  root.animate = (t, dt, speed, sitting) => {
    dt = Math.min(dt, 0.05);
    walk = L(walk, Math.min(1, speed), 1 - Math.exp(-dt * 8));
    runK = L(runK, THREE.MathUtils.clamp((speed - 1) / 0.8, 0, 1), 1 - Math.exp(-dt * 6));
    sit = L(sit, sitting ? 1 : 0, 1 - Math.exp(-dt * 6));
    let dy = root.rotation.y - lastYaw; dy = Math.atan2(Math.sin(dy), Math.cos(dy)); lastYaw = root.rotation.y;
    turn = L(turn, THREE.MathUtils.clamp(dy / Math.max(dt, 0.001), -4, 4), 1 - Math.exp(-dt * 6));

    // hopping: one hop per half turn of the phase; higher and quicker when running
    const moving = Math.min(1, walk * 3);
    phase += dt * (7 + 4 * runK) * moving;
    const arc = Math.abs(Math.sin(phase));                        // 0 on the ground, 1 at the top of a hop
    let height = arc * (0.14 * walk + 0.12 * runK) * moving;
    // at rest, now and then a little bounce on the spot
    idleHop -= dt * (1 - moving) * (1 - sit);
    if (idleHop < 0) { idleT = 0; idleHop = 4 + Math.random() * 5; }
    if (idleT >= 0) { idleT += dt; const k = idleT / 0.42; if (k >= 1) { idleT = -1; sp.v -= 2.2; } else height += Math.sin(k * Math.PI) * 0.09; }
    hop.position.y = height;

    // the target squash: flattened on landing, stretched in the air, breathing at rest, squat when sitting
    const ground = 1 - THREE.MathUtils.smoothstep(arc, 0, 0.3);
    let target = 1 + (arc - 0.35) * 0.16 * moving - ground * 0.12 * moving + Math.sin(t * 2.1) * 0.022 * (1 - moving) - 0.12 * sit;
    if (idleT >= 0) target += Math.sin(idleT / 0.42 * Math.PI) * 0.06;
    // the jelly: a spring towards the target, so every landing wobbles a little
    sp.v += ((target - sp.y) * 220 - sp.v * 11) * dt; sp.y += sp.v * dt;
    const sy = THREE.MathUtils.clamp(sp.y, 0.7, 1.3), sxz = 1 / Math.sqrt(sy);
    squash.scale.set(sxz, sy, sxz);

    // lean into the direction of travel, tilt into turns
    root.children[0].rotation.x = (0.1 * walk + 0.08 * runK) * (1 - sit);
    root.children[0].rotation.z = -turn * 0.05 * walk;

    blink -= dt; if (blink < -0.12) blink = 2 + Math.random() * 3.5;
    const ey = blink < 0 ? 0.12 : 1.15; eyes.forEach((e) => { e.scale.y = ey; });
  };
  return root;
}
