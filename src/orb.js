// The traveller: a small glowing orb of warm light that floats about a metre up. It bobs gently, breathes (its glow
// swells and settles), leans and stretches a little into the way it moves, and leaves a short trail of fading motes.
// It lights what is near it, more so in the dark. Same interface as before: position, rotation, animate(t, dt, speed, sitting).
import * as THREE from 'three';
import { softDot } from './kit.js';

export function makeOrb() {
  const root = new THREE.Group();
  const float = new THREE.Group(); root.add(float);
  const COLOR = new THREE.Color(0xfff1d6);                         // warm sandstone-cream light
  const core = new THREE.Mesh(new THREE.SphereGeometry(0.13, 32, 20), new THREE.MeshBasicMaterial({ color: COLOR.clone().multiplyScalar(1.6) }));
  core.userData.noShadow = true; float.add(core);
  const glowMat = (o) => new THREE.SpriteMaterial({ map: softDot(), color: COLOR, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, opacity: o });
  const halo = new THREE.Sprite(glowMat(0.9)); halo.scale.setScalar(0.75); float.add(halo);          // the glow round it
  const haze = new THREE.Sprite(glowMat(0.35)); haze.scale.setScalar(1.9); float.add(haze);         // and a wider haze
  const light = new THREE.PointLight(0xffe2b0, 1.6, 5, 1.6); float.add(light);
  // a short trail of motes left behind as it moves (in the world, not following the orb)
  const trail = Array.from({ length: 10 }, () => { const s = new THREE.Sprite(glowMat(0)); s.scale.setScalar(0.18); return s; });
  let trailOn = false, trailI = 0, trailT = 0;
  const wp = new THREE.Vector3();

  const L = THREE.MathUtils.lerp;
  let walk = 0, sit = 0, turn = 0, lastYaw = 0;
  root.animate = (t, dt, speed, sitting) => {
    dt = Math.min(dt, 0.05);
    if (!trailOn && root.parent) { for (const s of trail) root.parent.add(s); trailOn = true; }
    walk = L(walk, Math.min(1.8, speed), 1 - Math.exp(-dt * 6));
    sit = L(sit, sitting ? 1 : 0, 1 - Math.exp(-dt * 5));
    let dy = root.rotation.y - lastYaw; dy = Math.atan2(Math.sin(dy), Math.cos(dy)); lastYaw = root.rotation.y;
    turn = L(turn, THREE.MathUtils.clamp(dy / Math.max(dt, 0.001), -4, 4), 1 - Math.exp(-dt * 6));

    // float: about a metre up (lower when resting on the bench), bobbing slowly
    float.position.y = L(1.0, 0.75, sit) + Math.sin(t * 1.6) * 0.06 + Math.sin(t * 0.7 + 1) * 0.025;
    // lean and stretch into the way it moves; drift a little into turns
    float.rotation.x = 0.25 * Math.min(1, walk);
    float.position.x = -turn * 0.03 * Math.min(1, walk);
    const st = 1 + 0.18 * Math.min(1, walk);
    core.scale.set(1 / Math.sqrt(st), 1 / Math.sqrt(st), st);
    // breathe: the glow swells and settles
    const breath = 1 + Math.sin(t * 2.1) * 0.08 + Math.sin(t * 5.3) * 0.02;
    halo.scale.setScalar(0.75 * breath); haze.scale.setScalar(1.9 * (1 + Math.sin(t * 1.3) * 0.06));
    light.intensity = 1.6 * breath;

    // the trail: a mote dropped every so often while moving, each fading and sinking a little
    trailT -= dt;
    if (walk > 0.15 && trailT <= 0) {
      trailT = 0.07; const s = trail[trailI++ % trail.length];
      core.getWorldPosition(wp); s.position.copy(wp).add(new THREE.Vector3((Math.random() - 0.5) * 0.06, (Math.random() - 0.5) * 0.06, (Math.random() - 0.5) * 0.06));
      s.userData.life = 1;
    }
    for (const s of trail) {
      const l = (s.userData.life || 0) - dt * 1.6; s.userData.life = Math.max(0, l);
      s.material.opacity = 0.8 * s.userData.life; s.scale.setScalar(0.06 + 0.14 * s.userData.life); s.position.y -= dt * 0.05;
    }
  };
  return root;
}
