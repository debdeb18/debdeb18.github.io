// The terminal: a quiet platform on a railway that runs across the sea.
import * as THREE from 'three';
import { makeWorld, box, cyl, cone, sph, group, sign, sky, glowM, makeCrack, M } from '../kit.js';

export const DEST = {
  home: { color: 0x8fb4ff, name: 'Home among the stars' },
  office: { color: 0xffd27a, name: 'The Office' },
  market: { color: 0xff7aa8, name: 'The Night Market' },
};

export function buildTerminal() {
  const w = makeWorld('terminal', 'The Terminal');
  const s = w.scene;
  w.groundY = 0.6;
  w.spawn.set(2.5, 0.6, 3.4);
  w.cam = { dist: 10, pitch: 0.36, yaw: 0.55 };
  w.bloom = 0.35;
  const TZ = -2.2; // centre line of the track

  const skyMesh = sky(s, 0x4f9fe6, 0xcdeaf3, 0xbfe4ea);
  s.fog = new THREE.Fog(0xd7ecef, 45, 190);
  const hemi = new THREE.HemisphereLight(0xe6f6ff, 0x9fc7a8, 1.5); s.add(hemi);
  w.sunlight(0xfff0d0, 2.1, -9, 15, 7);

  // --- the sea ---
  const water = new THREE.Mesh(new THREE.PlaneGeometry(900, 900), new THREE.ShaderMaterial({
    uniforms: { t: { value: 0 }, a: { value: new THREE.Color(0x58b7c4) }, b: { value: new THREE.Color(0xcdeaf3) } },
    vertexShader: 'varying vec3 p; void main(){ p=(modelMatrix*vec4(position,1.)).xyz; gl_Position=projectionMatrix*viewMatrix*vec4(p,1.); }',
    fragmentShader: `uniform float t; uniform vec3 a,b; varying vec3 p;
      void main(){ float d=length(p.xz-cameraPosition.xz); float f=smoothstep(4.,150.,d);
        float sp=smoothstep(.9,1.,sin(p.x*1.9+t*1.1+sin(p.z*1.3+t*.4)*2.)*sin(p.z*2.7-t*.8));
        float sw=sin(p.x*.35+t*.5)*sin(p.z*.5-t*.3)*.035;
        gl_FragColor=vec4(mix(a,b,f)+sw+sp*.3*(1.-f),1.); }`,
  }));
  water.rotation.x = -Math.PI / 2;
  s.add(water);
  w.ticks.push((t) => { water.material.uniforms.t.value = t; });

  // --- the railway ---
  box(s, 500, 0.12, 2.6, 0xb9ad94, 0, -0.06, TZ);
  box(s, 500, 0.1, 0.1, 0x6f6a72, 0, 0.12, TZ - 0.7, { metalness: 0.6, roughness: 0.35 });
  box(s, 500, 0.1, 0.1, 0x6f6a72, 0, 0.12, TZ + 0.7, { metalness: 0.6, roughness: 0.35 });
  const sl = new THREE.InstancedMesh(new THREE.BoxGeometry(0.3, 0.08, 2), M(0x7b5b45), 200);
  const mt = new THREE.Matrix4();
  for (let i = 0; i < 200; i++) sl.setMatrixAt(i, mt.makeTranslation((i - 100) * 1.4, 0.09, TZ));
  s.add(sl);
  for (let i = -8; i <= 8; i++) { // telegraph poles marching to the horizon
    if (i === 0) continue;
    const g = group(s, i * 16, 0, TZ - 2.6);
    cyl(g, 0.07, 0.09, 5.5, 0x6b5a4c, 0, 0, 0, 6);
    box(g, 0.08, 0.08, 1.3, 0x6b5a4c, 0, 4.7, 0);
  }

  // --- platform + little island ---
  const IX = -13, IZ = 8.5;
  box(s, 15, 0.6, 5, 0xddd5c4, 0, 0, 2.5);
  box(s, 15, 0.02, 0.22, 0xf2c94c, 0, 0.6, 0.55);
  box(s, 15.3, 0.12, 5.3, 0xc4bba8, 0, -0.1, 2.5);
  cyl(s, 8.2, 9.6, 0.6, 0x86c06c, IX, 0, IZ, 20);
  cyl(s, 9.8, 10.6, 0.14, 0xe9dcb4, IX, -0.08, IZ, 20);
  w.inside = (x, z) => (Math.abs(x) < 7.2 && z > 0.45 && z < 5.2) || ((x - IX) ** 2 + (z - IZ) ** 2 < 7.6 ** 2 && (x < -7.2 || z >= 5));

  // the chair
  const chair = group(s, 0, 0.6, 1.9);
  box(chair, 0.62, 0.07, 0.6, 0xb98556, 0, 0.45, 0);
  for (const [x, z] of [[-0.26, -0.25], [0.26, -0.25], [-0.26, 0.25], [0.26, 0.25]]) box(chair, 0.06, 0.45, 0.06, 0x8f6440, x, 0, z);
  box(chair, 0.06, 0.6, 0.06, 0x8f6440, -0.26, 0.5, 0.27); box(chair, 0.06, 0.6, 0.06, 0x8f6440, 0.26, 0.5, 0.27);
  box(chair, 0.62, 0.3, 0.05, 0xb98556, 0, 0.78, 0.27);
  w.solid(0, 1.9, 0.6, 0.6);
  w.chair = new THREE.Vector3(0, 0.6, 1.9);
  w.hot(0, 1.9, 'Sit down and wait for the train', 'sit', { y: 1.7, r: 1.7 });

  // station sign
  const sg = group(s, -4.2, 0.6, 1.0);
  cyl(sg, 0.06, 0.06, 2.6, 0x5b5560, -1.5, 0, 0, 6); cyl(sg, 0.06, 0.06, 2.6, 0x5b5560, 1.5, 0, 0, 6);
  box(sg, 3.3, 1.3, 0.08, 0x5b5560, 0, 1.4, 0);
  const txt = ['어딘가', 'SOMEWHERE  ·  ENTAH DI MANA', '←  Semarang                    Seoul  →'];
  const so = { size: [0.42, 0.15, 0.14], fg: ['#2f3b52', '#5a6478', '#b0563f'], border: '#2f3b52' };
  sign(sg, txt, 3.1, 1.1, 0, 2.05, 0.05, so);
  sign(sg, txt, 3.1, 1.1, 0, 2.05, -0.05, { ...so, ry: Math.PI });
  w.solid(-4.2, 1.0, 3.3, 0.3);

  // crossing signal
  const cg = group(s, 4.6, 0.6, 0.9);
  cyl(cg, 0.06, 0.08, 3.2, 0x44424c, 0, 0, 0, 6);
  const x1 = box(cg, 1.3, 0.14, 0.05, 0xf4f0e6, 0, 2.9, 0); x1.rotation.z = 0.6;
  const x2 = box(cg, 1.3, 0.14, 0.05, 0xf4f0e6, 0, 2.9, 0); x2.rotation.z = -0.6;
  box(cg, 0.9, 0.3, 0.1, 0x2c2b33, 0, 2.2, 0);
  const lampOff = M(0x5a1f1f), lampOn = glowM(0xff3b30, 3);
  const la = sph(cg, 0.11, lampOff, -0.27, 2.35, 0.07), lb = sph(cg, 0.11, lampOff, 0.27, 2.35, 0.07);
  w.solid(4.6, 0.9, 0.3, 0.3);

  // lamp post
  const lg = group(s, 6.6, 0.6, 4.5);
  cyl(lg, 0.05, 0.08, 3, 0x4c4a55, 0, 0, 0, 6);
  box(lg, 0.34, 0.4, 0.34, glowM(0xffd9a0, 1.7), 0, 3, 0);
  cone(lg, 0.34, 0.2, 0x4c4a55, 0, 3.4, 0, 4);
  w.solid(6.6, 4.5, 0.3, 0.3);

  // vending machine (it only sells links)
  const vg = group(s, 6.6, 0.6, 2.6, -Math.PI / 2);
  box(vg, 1.1, 1.9, 0.8, 0xd9483b, 0, 0, 0);
  box(vg, 0.9, 0.9, 0.04, glowM(0xfff3d0, 1.5), 0, 0.85, 0.41);
  box(vg, 0.9, 0.25, 0.04, 0x2c2b33, 0, 0.25, 0.41);
  for (let i = 0; i < 8; i++) cyl(vg, 0.07, 0.07, 0.2, [0x3f8fd1, 0xf2c94c, 0x5fa46b, 0xffffff][i % 4], -0.33 + (i % 4) * 0.22, 1 + Math.floor(i / 4) * 0.36, 0.44, 8);
  w.solid(6.6, 2.6, 0.8, 1.1);
  w.hot(5.8, 2.6, 'Check the vending machine', 'contact');

  // notice board
  const ng = group(s, -9.5, 0.6, 5.2, 0.5);
  cyl(ng, 0.05, 0.05, 1.9, 0x7b5b45, -0.8, 0, 0, 6); cyl(ng, 0.05, 0.05, 1.9, 0x7b5b45, 0.8, 0, 0, 6);
  box(ng, 1.9, 1.2, 0.08, 0x9c7450, 0, 0.8, 0);
  sign(ng, ['NOTICE', 'three lines depart from here', 'sit on the chair · pick a ticket'], 1.7, 1, 0, 1.4, 0.05, { size: [0.2, 0.1, 0.1], fg: ['#b0563f', '#3b3a4a', '#3b3a4a'] });
  cone(ng, 1.15, 0.3, 0xb0563f, 0, 2, 0, 4).rotation.y = Math.PI / 4;
  w.solid(-9.5, 5.2, 1.7, 1);
  w.hot(-9, 6, 'Read the notice board', 'welcome');

  // cherry blossom tree
  const TX = -16.5, TZ2 = 7;
  const tg = group(s, TX, 0.6, TZ2);
  cyl(tg, 0.28, 0.45, 2.6, 0x5c4033, 0, 0, 0, 7).rotation.z = 0.08;
  const b1 = cyl(tg, 0.13, 0.2, 2.2, 0x5c4033, 0.8, 2.2, 0, 6); b1.rotation.z = -0.8;
  const b2 = cyl(tg, 0.12, 0.18, 2, 0x5c4033, -0.8, 2.3, 0.2, 6); b2.rotation.z = 0.8;
  const pinks = [0xffc4d6, 0xffd6e2, 0xfbb1c8];
  for (let i = 0; i < 16; i++) {
    const a = Math.random() * 6.28, r = Math.random() * 2.3;
    sph(tg, 0.9 + Math.random() * 0.8, pinks[i % 3], Math.cos(a) * r, 3.6 + Math.random() * 1.9, Math.sin(a) * r, 1);
  }
  w.solid(TX, TZ2, 0.9, 0.9);
  const PN = 140, pp = new Float32Array(PN * 3);
  for (let i = 0; i < PN; i++) pp.set([TX + (Math.random() - 0.5) * 9, 0.6 + Math.random() * 5, TZ2 + (Math.random() - 0.5) * 9], i * 3);
  const pgeo = new THREE.BufferGeometry(); pgeo.setAttribute('position', new THREE.BufferAttribute(pp, 3));
  s.add(new THREE.Points(pgeo, new THREE.PointsMaterial({ color: 0xffc9da, size: 0.09 })));
  w.ticks.push((t, dt) => {
    for (let i = 0; i < PN; i++) {
      pp[i * 3 + 1] -= dt * (0.35 + (i % 5) * 0.06);
      pp[i * 3] += Math.sin(t + i) * dt * 0.4 - dt * 0.25;
      if (pp[i * 3 + 1] < 0.6) { pp[i * 3 + 1] = 5.5; pp[i * 3] = TX + (Math.random() - 0.5) * 9; }
    }
    pgeo.attributes.position.needsUpdate = true;
  });

  // grass + flowers on the island
  const tuft = new THREE.InstancedMesh(new THREE.ConeGeometry(0.09, 0.45, 4), M(0x5fa85a), 260);
  const fl = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(0.07, 0), M(0xfff2a8), 60);
  for (let i = 0; i < 260; i++) {
    const a = Math.random() * 6.28, r = Math.sqrt(Math.random()) * 7.8, x = IX + Math.cos(a) * r, z = IZ + Math.sin(a) * r, off = x > -7.6 && z < 5.2;
    tuft.setMatrixAt(i, mt.makeTranslation(x, off ? -5 : 0.8, z));
    if (i < 60) fl.setMatrixAt(i, mt.makeTranslation(x + 0.2, off ? -5 : 0.72, z + 0.1));
  }
  s.add(tuft, fl);
  // a bench-side suitcase, because everyone here is going somewhere
  box(s, 0.5, 0.36, 0.2, 0x4f7f8f, 0.75, 0.6, 2.0); box(s, 0.2, 0.05, 0.05, 0x2c2b33, 0.75, 0.96, 2.0);

  // clouds
  const clouds = [];
  for (let i = 0; i < 12; i++) {
    const g = group(s, (Math.random() - 0.5) * 300, 22 + Math.random() * 24, -40 - Math.random() * 140);
    for (let j = 0; j < 5; j++) sph(g, 4 + Math.random() * 4, 0xffffff, (j - 2) * 5, Math.random() * 2, Math.random() * 3, 1, { emissive: 0xffffff, emissiveIntensity: 0.25 }).scale.y = 0.6;
    g.traverse((o) => { o.userData.noShadow = true; });
    clouds.push(g);
  }
  w.ticks.push((t, dt) => { for (const c of clouds) { c.position.x += dt * 0.8; if (c.position.x > 170) c.position.x = -170; } });
  // far islands
  for (const [x, z, r] of [[-70, -90, 16], [50, -120, 22], [110, -60, 12], [-120, -30, 14], [-40, 70, 12]]) {
    sph(s, r, 0x7fb873, x, -r * 0.55, z, 2).scale.y = 0.7;
    box(s, 2.4, 2, 2.4, 0xf6efe0, x + 2, r * 0.1, z + r * 0.35); cone(s, 2.2, 1.4, 0xc9604a, x + 2, r * 0.1 + 2, z + r * 0.35, 4).rotation.y = Math.PI / 4;
  }

  // --- the train ---
  const train = group(s, -120, 0.2, TZ);
  for (let c = 0; c < 2; c++) {
    const g = group(train, -c * 9.6, 0, 0);
    box(g, 9.2, 1.1, 2.3, 0x8c2f39, 0, 0.35, 0);
    box(g, 9.2, 1.3, 2.3, 0xf3e7cf, 0, 1.45, 0);
    box(g, 9.4, 0.18, 2.5, 0x5b5560, 0, 2.75, 0);
    for (let i = 0; i < 6; i++) for (const zz of [1.16, -1.16]) box(g, 1, 0.75, 0.04, glowM(0xffe2a6, 1.5), -3.6 + i * 1.45, 1.65, zz);
    for (const xx of [-3, 3]) box(g, 1.6, 0.4, 2, 0x2c2b33, xx, 0, 0);
  }
  box(train, 0.1, 0.8, 1.6, glowM(0xfff3d0, 1.3), 4.62, 1.6, 0);
  sph(train, 0.18, glowM(0xfff3d0, 4), 4.65, 0.9, 0.7); sph(train, 0.18, glowM(0xfff3d0, 4), 4.65, 0.9, -0.7);
  train.visible = false;

  // --- the dimension crack ---
  const crack = makeCrack();
  crack.position.set(0, 0.15, TZ); crack.setOpen(0); s.add(crack);
  w.crack = crack;
  const C = new THREE.Vector3(0, 2.7, TZ);
  const crackLight = new THREE.PointLight(0xffffff, 0, 16);
  crackLight.position.set(0, 2.5, TZ + 0.8); s.add(crackLight);
  const fx = { transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, opacity: 0 };
  // light rays fanning out of the tear
  const rays = group(s, C.x, C.y, C.z - 0.06), rayMat = new THREE.MeshBasicMaterial(fx);
  for (let i = 0; i < 12; i++) {
    const len = 5 + Math.random() * 6;
    const m = new THREE.Mesh(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(-0.1, 0, 0), new THREE.Vector3(0.1, 0, 0), new THREE.Vector3(0, len, 0)]), rayMat);
    m.rotation.z = (i / 12) * 6.283 + Math.random() * 0.4; rays.add(m);
  }
  // shockwave ring at the moment it shatters
  const ring = new THREE.Mesh(new THREE.RingGeometry(0.9, 1, 64), new THREE.MeshBasicMaterial(fx));
  ring.position.copy(C); s.add(ring);
  // motes of light pulled into the crack
  const MN = 240, mp = new Float32Array(MN * 3), ms = [];
  for (let i = 0; i < MN; i++) ms.push({ a: Math.random() * 6.283, r: 1 + Math.random() * 9, y: (Math.random() - 0.5) * 6, v: 1.5 + Math.random() * 2.5 });
  const mgeo = new THREE.BufferGeometry(); mgeo.setAttribute('position', new THREE.BufferAttribute(mp, 3));
  const motes = new THREE.Points(mgeo, new THREE.PointsMaterial({ size: 0.11, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
  motes.frustumCulled = false; motes.visible = false; s.add(motes);

  // the sky slides into dusk while the train comes
  const sU = skyMesh.material.uniforms, wU = water.material.uniforms, col = (h) => new THREE.Color(h);
  const day = { a: sU.a.value.clone(), b: sU.b.value.clone(), c: sU.c.value.clone(), wa: wU.a.value.clone(), wb: wU.b.value.clone(), fog: s.fog.color.clone(), sun: w.sun.color.clone() };
  const dusk = { a: col(0x232a5c), b: col(0xf6b3a0), c: col(0x7a86b4), wa: col(0x2c6890), wb: col(0xf0bcae), fog: col(0xe8b9b0), sun: col(0xffb38a) };
  const mood = (k) => {
    sU.a.value.lerpColors(day.a, dusk.a, k); sU.b.value.lerpColors(day.b, dusk.b, k); sU.c.value.lerpColors(day.c, dusk.c, k);
    wU.a.value.lerpColors(day.wa, dusk.wa, k); wU.b.value.lerpColors(day.wb, dusk.wb, k);
    s.fog.color.lerpColors(day.fog, dusk.fog, k); w.sun.color.lerpColors(day.sun, dusk.sun, k);
    hemi.intensity = 1.5 - 0.55 * k; w.sun.intensity = 2.1 - 0.5 * k;
  };

  // the cutscene: four shots, each a slow camera move
  const END = 7.6, V = (a) => new THREE.Vector3(...a);
  const shots = [
    { t: 0, from: V([2.3, 2.5, 5.6]), to: V([1.9, 2.2, 4.9]), look: V([0, 1.7, TZ]) },          // waiting
    { t: 1.5, from: V([7.6, 0.95, -0.35]), to: V([7.6, 1.15, -0.2]), look: V([-30, 2.4, TZ]) },  // rail-side, train bearing down
    { t: 3.05, from: V([3.0, 2.2, 6.8]), to: V([1.7, 2.3, 5.3]), look: V([0, 2.3, TZ]) },        // it passes, the air tears
    { t: 5.7, from: V([1.6, 2.0, 4.8]), to: V([0.3, 1.9, 0.7]), look: V([0, 2.6, TZ]) },         // walking in
    { t: END },
  ];
  w.cine = { pos: shots[0].from.clone(), look: shots[0].look.clone(), snap: false, shake: 0, glow: 0 };
  w.seqT = 0;
  let seq = null;
  const cl = (x) => THREE.MathUtils.clamp(x, 0, 1), ease = (x) => x * x * (3 - 2 * x);
  w.depart = (dest, onArrive) => {
    seq = { t: 0, onArrive, done: false, shot: 0 };
    crack.setColor(DEST[dest].color); crackLight.color.set(DEST[dest].color);
    rayMat.color.set(DEST[dest].color).multiplyScalar(1.4); ring.material.color.set(DEST[dest].color).multiplyScalar(2); motes.material.color.set(DEST[dest].color).lerp(col(0xffffff), 0.5);
    train.visible = true; train.position.x = -95;
  };
  w.reset = () => {
    seq = null; w.seqT = 0; crack.setOpen(0); crack.setPortal(null); crackLight.intensity = 0; train.visible = false; motes.visible = false;
    rayMat.opacity = ring.material.opacity = 0; la.material = lb.material = lampOff; mood(0);
    Object.assign(w.cine, { snap: false, shake: 0, glow: 0 }); w.cine.pos.copy(shots[0].from); w.cine.look.copy(shots[0].look);
  };
  w.ticks.push((t, dt) => {
    crack.tick(t);
    if (!seq) return;
    const q = (seq.t += dt); w.seqT = q;
    const blink = Math.floor(q * 3) % 2;
    la.material = blink ? lampOn : lampOff; lb.material = blink ? lampOff : lampOn;
    mood(ease(cl(q / 3.6)));
    train.position.x = -95 + Math.max(0, q - 1.2) * 52;
    // camera
    let i = seq.shot; while (q >= shots[i + 1].t && i < shots.length - 2) i++;
    if (i !== seq.shot) { seq.shot = i; w.cine.snap = true; }
    const sh = shots[i];
    w.cine.pos.lerpVectors(sh.from, sh.to, ease(cl((q - sh.t) / (shots[i + 1].t - sh.t)))); w.cine.look.copy(sh.look);
    w.cine.shake = 0.09 * Math.exp(-(((train.position.x - 5 - w.cine.pos.x) / 13) ** 2));
    w.cine.glow = ease(cl((q - 6.4) / 1.1)) * 1.8;
    // the tear: a hairline climbs, then it shatters open
    const open = cl((q - 3.75) / 1.5), wide = cl((open - 0.3) / 0.7), qs = q - 4.2;
    crack.setOpen(open); crackLight.intensity = wide * 90;
    rayMat.opacity = wide * (0.22 + Math.sin(t * 5) * 0.05); rays.rotation.z = t * 0.15;
    ring.scale.setScalar(1 + Math.max(0, qs) * 15); ring.material.opacity = qs > 0 ? cl(1 - qs / 0.9) * 0.9 : 0;
    motes.visible = wide > 0;
    for (let n = 0; n < MN; n++) {
      const m = ms[n]; m.r -= dt * m.v * (0.6 + wide); m.a += dt * (1.2 + 3 / (m.r + 0.5));
      if (m.r < 0.15) { m.r = 6 + Math.random() * 4; m.y = (Math.random() - 0.5) * 6; }
      mp[n * 3] = C.x + Math.cos(m.a) * m.r; mp[n * 3 + 1] = C.y + m.y * Math.min(1, m.r / 5) + Math.sin(m.a) * m.r * 0.25; mp[n * 3 + 2] = C.z + 0.4 + Math.abs(Math.sin(m.a)) * m.r * 0.5;
    }
    mgeo.attributes.position.needsUpdate = true;
    if (q > END && !seq.done) { seq.done = true; seq.onArrive(); }
  });

  return w.finish();
}
