// The night market: who I am outside work. Stalls, food trucks, lanterns.
import * as THREE from 'three';
import { twistedTree, grass, rock, mound } from '../nature.js';
import { makeWorld, box, cyl, cone, sph, group, sign, sky, stars, glowM, makeCrack, M } from '../kit.js';

export function buildMarket() {
  const w = makeWorld('market', 'The Night Market');
  const s = w.scene;
  w.spawn.set(0, 0, 7.6);
  w.cam = { dist: 12, pitch: 0.5, yaw: 0.35 };
  w.bloom = 0.42;
  sky(s, 0x070a22, 0x2c2152, 0x1a1535);
  s.fog = new THREE.Fog(0x1d1840, 45, 150);
  stars(s, 1500, 300, 420, 1.3, true);
  s.add(new THREE.HemisphereLight(0x8a96e0, 0x3a2a45, 1.25));
  w.sunlight(0xaebcff, 0.9, -8, 16, 8);
  sph(s, 9, glowM(0xfff4d6, 1.25), -70, 90, -160, 3);
  w.inside = (x, z) => Math.abs(x) < 16 && Math.abs(z) < 10.6;

  // plaza
  box(s, 36, 0.5, 25, 0x514a6b, 0, -0.5, 0); box(s, 38, 0.3, 27, 0x3a3552, 0, -0.7, 0);
  for (let i = 0; i < 70; i++) box(s, 0.9 + Math.random(), 0.01, 0.6 + Math.random() * 0.6, 0x5c5578, (Math.random() - 0.5) * 33, 0, (Math.random() - 0.5) * 22);
  // twisted trees, rocks and grass around the plaza
  for (const [x, z, sc, ry] of [[-21, -9, 2.2, 0], [20.5, -10, 2.6, 2], [22, 6, 2, 4], [-22, 7, 2.4, 1], [-9, -15, 2.1, 3], [9, -15.5, 2.3, 5]]) twistedTree(s, x, -0.6, z, sc, { ry, leaf: [0x1f4f5a, 0x5fb89a], dark: 0x5a3a4a, light: 0xc98a5a });
  mound(s, 0, -1.1, 0, 27, 0.5, 0x3f7a6a, 0x2c5560, 0x2a3550);
  const gr = grass(s, 1500, 0x1f5f58, 0x6fcf9a);
  for (let i = 0; i < 250; i++) { const a = Math.random() * 6.28, r = 20.5 + Math.random() * 6, x = Math.cos(a) * r * 1.0, z = Math.sin(a) * r * 0.82; if (Math.abs(x) > 18.6 || Math.abs(z) > 13.2) gr.clump(x, -0.6, z, 0.5 + Math.random() * 0.7); }
  for (const [x, z, sc] of [[-19.5, -3, 1.1], [-20.5, -1.5, 0.6], [19.6, -4, 0.9], [19.4, 10, 1.2], [-13, 13.6, 0.8], [4, -14, 0.7], [14, 13.8, 0.6]]) rock(s, x, -0.65, z, sc, 0x4a4a6a, 0xa9a4c4);
  const warm = (x, y, z, i = 45) => { const l = new THREE.PointLight(0xffb86b, i, 15); l.position.set(x, y, z); s.add(l); };

  // a stall: counter, striped awning, glowing sign, goods
  const stall = (x, z, name, c1, c2, key, label, goods) => {
    const g = group(s, x, 0, z);
    box(g, 3, 1, 1.1, 0x8f6440, 0, 0, 0); box(g, 3.2, 0.08, 1.3, 0xd9b991, 0, 1, 0);
    for (const px of [-1.5, 1.5]) for (const pz of [-0.55, 0.75]) cyl(g, 0.05, 0.05, 2.7, 0x5b5560, px, 0, pz, 6);
    for (let i = 0; i < 6; i++) { const a = box(g, 0.56, 0.06, 1.9, i % 2 ? c1 : c2, -1.4 + i * 0.56, 2.62, 0.2); a.rotation.x = 0.22; }
    sign(g, name, 2.6, 0.5, 0, 3.15, 0.3, { size: 0.3, bg: '#2a2140', fg: '#ffe9b0', glow: 1.7, double: true });
    sph(g, 0.2, glowM(0xffc56b, 1.8), -1.2, 2.25, 0.9); sph(g, 0.2, glowM(0xffc56b, 1.8), 1.2, 2.25, 0.9);
    goods(g);
    w.solid(x, z, 3.2, 1.4);
    w.hot(x, z + 1.5, label, key, { y: 3.9, r: 1.7 });
  };
  const row = (g, cols, shape) => { for (let i = 0; i < 7; i++) shape(g, cols[i % cols.length], -1.2 + i * 0.4, 1.08, 0.1 + (i % 2) * 0.25); };

  stall(-11.5, -6.8, 'PLAY', 0x5b3fa0, 0xf4f0e6, 'games', 'Browse the game stall', (g) => row(g, [0xd9483b, 0x3f8fd1, 0x5fa46b], (g, c, x, y, z) => box(g, 0.28, 0.36, 0.06, c, x, y, z).rotation.x = -0.3));
  stall(-5.8, -6.8, 'ART', 0xff8fab, 0xf4f0e6, 'gallery', 'Browse the art stall', (g) => row(g, [0xffb7c9, 0x8fb4ff, 0xf2c94c, 0x9ff0c0], (g, c, x, y, z) => box(g, 0.3, 0.3, 0.04, c, x, y + 0.05, z).rotation.x = -0.4));
  stall(0, -6.8, 'WORDS', 0x3f8fd1, 0xf4f0e6, 'words', 'Flip through the zines', (g) => row(g, [0xf4f0e6, 0xe9dcc6, 0xffe9b0], (g, c, x, y, z) => box(g, 0.3, 0.05, 0.4, c, x, y, z).rotation.y = x));
  stall(5.8, -6.8, 'SIDE QUESTS', 0x5fa46b, 0xf4f0e6, 'side', 'Browse the side projects', (g) => row(g, [0x9d8bd3, 0xe8a05a, 0x4f7f8f], (g, c, x, y, z) => box(g, 0.26, 0.26, 0.26, c, x, y, z).rotation.y = x * 2));
  stall(11.5, -6.8, 'THE LAB', 0xe8a05a, 0xf4f0e6, 'lab', 'Poke around the lab', (g) => row(g, [0x7fffd0, 0xff8fab, 0xffe08a], (g, c, x, y, z) => cyl(g, 0.08, 0.12, 0.34, glowM(c, 1.6), x, y, z, 8)));
  for (const x of [-8.6, -2.9, 2.9, 8.6]) warm(x, 3, -4.6);

  // food truck
  { const g = group(s, -12, 0, 1.5, Math.PI / 2);
    box(g, 4.4, 2.2, 2, 0xf4e3c1, 0, 0.45, 0); box(g, 1.3, 1.5, 1.9, 0xd9483b, 2.8, 0.45, 0); box(g, 0.05, 0.6, 1.5, glowM(0x9fd0ff, 1.1), 3.46, 1.2, 0);
    for (const xx of [-1.4, 2.6]) for (const zz of [-1, 1]) cyl(g, 0.42, 0.42, 0.25, 0x2c2b33, xx, 0.03, zz, 12).rotation.x = Math.PI / 2;
    box(g, 2.6, 0.9, 0.05, glowM(0xffe2a6, 1.5), -0.4, 1.4, 1.01);
    const aw = box(g, 3, 0.07, 1.2, 0xd9483b, -0.4, 2.45, 1.5); aw.rotation.x = 0.25;
    box(g, 2.8, 0.08, 0.5, 0xd9b991, -0.4, 1.3, 1.25);
    sign(g, 'EATS', 2.2, 0.5, -0.4, 3.0, 1.02, { size: 0.32, bg: '#d9483b', fg: '#fff5d6', glow: 1.6, double: true });
    for (let i = 0; i < 4; i++) cyl(g, 0.13, 0.09, 0.14, [0xffffff, 0xf2c94c][i % 2], -1.3 + i * 0.6, 1.38, 1.3, 8);
    w.solid(-12, 1.1, 2.2, 5.4); w.hot(-10.2, 1.9, 'Order something from the food truck', 'food', { y: 3.8 }); warm(-9.6, 2.8, 1.9); }

  // goods shop
  { const g = group(s, 12.6, 0, 1.6, -Math.PI / 2);
    box(g, 5, 2.8, 2.6, 0x6a5a8a, 0, 0, -0.4); cone(g, 3.9, 1.4, 0xb0563f, 0, 2.8, -0.4, 4).rotation.y = Math.PI / 4;
    box(g, 2, 1.3, 0.05, glowM(0xffe2a6, 1.4), -1, 0.9, 0.92); box(g, 1, 2, 0.06, 0x8f6440, 1.4, 0, 0.92);
    for (let i = 0; i < 5; i++) sph(g, 0.16, [0xff8fab, 0x7fffd0, 0xffe08a][i % 3], -1.8 + i * 0.4, 1.1, 1.0, 0);
    sign(g, 'GOODS', 2.4, 0.5, -0.2, 2.5, 0.95, { size: 0.32, bg: '#2a2140', fg: '#ffe9b0', glow: 1.7 });
    w.solid(12.6, 1.6, 3.2, 5); w.hot(10.6, 2.4, 'Peek into the goods shop', 'goods', { y: 3.6 }); warm(9.8, 2.8, 1.6); }

  // collaboration hub: a round table under a big lantern
  { const g = group(s, 0, 0, 0.6);
    cyl(g, 1.5, 1.5, 0.1, 0xd9b991, 0, 0.75, 0, 20); cyl(g, 0.15, 0.4, 0.75, 0x8f6440, 0, 0, 0, 8);
    for (let i = 0; i < 6; i++) cyl(g, 0.3, 0.3, 0.45, [0xff8fab, 0x8fb4ff, 0xffe08a][i % 3], Math.cos(i * 1.047) * 2.2, 0, Math.sin(i * 1.047) * 2.2, 10);
    cyl(g, 0.05, 0.05, 4.4, 0x5b5560, 0, 0.8, 0, 6);
    const lan = sph(g, 0.75, glowM(0xff9a5a, 1.8), 0, 4.6, 0, 1); lan.scale.y = 0.8;
    sign(g, 'COLLAB HUB', 2.4, 0.45, 0, 3.6, 0, { size: 0.28, bg: '#2a2140', fg: '#ffe9b0', glow: 1.7, double: true });
    box(g, 0.5, 0.03, 0.36, 0xf4f0e6, 0.4, 0.85, 0.3); cyl(g, 0.1, 0.08, 0.16, 0xffffff, -0.5, 0.85, 0.2, 8);
    w.solid(0, 0.6, 2.6, 2.6); w.hot(0, 3.1, 'Pull up a stool at the collab hub', 'contact', { y: 3.2, r: 1.8 }); warm(0, 4, 1.6, 70); }

  // string lights around the plaza
  const poles = [[-16, -10], [-5.5, -10], [5.5, -10], [16, -10], [16, 10], [5.5, 10], [-5.5, 10], [-16, 10]];
  poles.forEach(([x, z]) => cyl(s, 0.07, 0.1, 5, 0x3a3552, x, 0, z, 6));
  const links = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 0], [1, 6], [2, 5]];
  const bulbs = new THREE.InstancedMesh(new THREE.SphereGeometry(0.11, 12, 8), new THREE.MeshBasicMaterial(), links.length * 14);
  const mt = new THREE.Matrix4(), col = new THREE.Color(), pal = [0xffd27a, 0xff8fab, 0x8fd0ff, 0xfff3d0];
  let n = 0;
  for (const [a, b] of links) for (let i = 1; i <= 14; i++) {
    const k = i / 15, x = poles[a][0] + (poles[b][0] - poles[a][0]) * k, z = poles[a][1] + (poles[b][1] - poles[a][1]) * k;
    bulbs.setMatrixAt(n, mt.makeTranslation(x, 4.9 - Math.sin(k * Math.PI) * 1.1, z));
    bulbs.setColorAt(n++, col.set(pal[n % 4]).multiplyScalar(1.6));
  }
  bulbs.userData.noShadow = true; s.add(bulbs);

  // sky lanterns drifting up
  const lans = [];
  for (let i = 0; i < 26; i++) { const l = box(s, 0.5, 0.65, 0.5, glowM(i % 3 ? 0xffb05a : 0xff7a6a, 1.7), (Math.random() - 0.5) * 90, Math.random() * 45 + 6, -14 - Math.random() * 70); l.userData.noShadow = true; lans.push(l); }
  w.ticks.push((t, dt) => { for (const l of lans) { l.position.y += dt * 0.5; l.position.x += Math.sin(t * 0.3 + l.position.z) * dt * 0.3; if (l.position.y > 55) l.position.y = 5; } });

  // benches + crates for texture
  for (const [x, z] of [[-5.5, 5.5], [5.5, 5.5]]) { box(s, 2.2, 0.1, 0.6, 0x8f6440, x, 0.45, z); box(s, 0.1, 0.45, 0.5, 0x5b5560, x - 0.9, 0, z); box(s, 0.1, 0.45, 0.5, 0x5b5560, x + 0.9, 0, z); w.solid(x, z, 2.2, 0.6); }
  box(s, 0.8, 0.6, 0.8, 0xa9772f, -14.6, 0, -8.6); box(s, 0.7, 0.5, 0.7, 0xa9772f, -14.5, 0.6, -8.5); w.solid(-14.6, -8.6, 0.9, 0.9);

  const crack = makeCrack(0xbfe4ea); crack.position.set(0, 0, 9.9); s.add(crack);
  w.ticks.push((t) => { crack.tick(t); crack.scale.multiplyScalar(0.6); });
  w.hot(0, 9.3, 'Step back to the terminal', 'terminal', { y: 3.2, color: 0xbfe4ea, r: 1.4 });

  return w.finish();
}
