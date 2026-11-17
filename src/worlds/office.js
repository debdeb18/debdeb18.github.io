// The office: a small cut-away building. Dev room, archive, meeting room, pantry (+ one arcade machine).
import * as THREE from 'three';
import { makeWorld, box, cyl, sph, group, sign, sky, glowM, makeCrack, plant, M } from '../kit.js';

export function buildOffice() {
  const w = makeWorld('office', 'The Office');
  const s = w.scene;
  w.spawn.set(0, 0, 5.2);
  w.cam = { dist: 13, pitch: 0.95, yaw: 0.3 };
  w.bloom = 0.3;
  sky(s, 0x9cc4e8, 0xfbe7cf, 0xf3d9c0);
  s.add(new THREE.HemisphereLight(0xffffff, 0xd8c4a8, 1.6));
  w.sunlight(0xfff1dc, 1.7, 8, 16, 9);
  w.inside = (x, z) => Math.abs(x) < 10.8 && Math.abs(z) < 7.8;

  // slab + floors
  box(s, 23, 0.6, 17, 0xb8a58c, 0, -0.62, 0); box(s, 19, 2.5, 13, 0x9c8a74, 0, -3.1, 0);
  const floor = (x0, x1, z0, z1, c) => box(s, x1 - x0, 0.04, z1 - z0, c, (x0 + x1) / 2, -0.03, (z0 + z1) / 2);
  floor(-11, 0, -8, -1.5, 0xbfd0d8); floor(0, 11, -8, -1.5, 0xdccba6);
  floor(-11, 11, -1.5, 1.5, 0xeae4d8); floor(-2, 2, 1.5, 8, 0xeae4d8);
  floor(-11, -2, 1.5, 8, 0xbccdb2); floor(2, 11, 1.5, 8, 0xeed4ae);

  // walls (cut low so you can see inside)
  const H = 1.25, T = 0.25, WALL = 0xfaf5ea;
  const wall = (alongX, c, a, b, gaps = [], h = H) => {
    let from = a;
    for (const [g0, g1] of [...gaps, [b, b]]) {
      const len = g0 - from, mid = (from + g0) / 2;
      if (len > 0.01) {
        if (alongX) { box(s, len, h, T, WALL, mid, 0, c); w.solid(mid, c, len, T); }
        else { box(s, T, h, len, WALL, c, 0, mid); w.solid(c, mid, T, len); }
      }
      from = g1;
    }
  };
  wall(true, -8, -11, 11, [], 2.4); wall(true, 8, -11, 11, [[-1.2, 1.2]], 0.5);
  wall(false, -11, -8, 8, [], 2.4); wall(false, 11, -8, 8, [], 0.5);
  wall(true, -1.5, -11, 11, [[-6.4, -4.6], [4.6, 6.4]]);
  wall(false, 0, -8, -1.5);
  wall(true, 1.5, -11, -2, [[-7.4, -5.6]]); wall(true, 1.5, 2, 11, [[5.6, 7.4]]);
  wall(false, -2, 1.5, 8); wall(false, 2, 1.5, 8);
  const tag = (t, x, z, col) => sign(s, t, 2.2, 0.42, x, H + 0.3, z, { size: 0.2, bg: col, fg: '#ffffff', double: true });
  tag('DEV ROOM', -5.5, -1.5, '#4f7f8f'); tag('ARCHIVE', 5.5, -1.5, '#a9772f');
  tag('MEETING ROOM', -6.5, 1.5, '#5f8a5a'); tag('PANTRY', 6.5, 1.5, '#c9604a');

  const desk = (x, z, c = 0x9fd0ff) => {
    box(s, 2.2, 0.08, 1, 0xd9b991, x, 0.72, z); box(s, 0.08, 0.72, 0.9, 0x8f6440, x - 1, 0, z); box(s, 0.08, 0.72, 0.9, 0x8f6440, x + 1, 0, z);
    box(s, 0.9, 0.55, 0.05, 0x2c2b33, x - 0.45, 0.9, z - 0.25); box(s, 0.8, 0.45, 0.02, glowM(c, 1.3), x - 0.45, 0.95, z - 0.22);
    box(s, 0.9, 0.55, 0.05, 0x2c2b33, x + 0.5, 0.9, z - 0.25); box(s, 0.8, 0.45, 0.02, glowM(0x1f2b3a, 1), x + 0.5, 0.95, z - 0.22);
    box(s, 0.7, 0.03, 0.22, 0xf4f0e6, x, 0.8, z + 0.2);
    w.solid(x, z, 2.2, 1);
    chair(x, z + 1);
  };
  const chair = (x, z, c = 0x4f7f8f) => { cyl(s, 0.28, 0.28, 0.08, c, x, 0.45, z, 10); cyl(s, 0.04, 0.04, 0.45, 0x5b5560, x, 0, z, 6); box(s, 0.5, 0.5, 0.06, c, x, 0.5, z + 0.27); };

  // --- DEV ROOM ---
  desk(-8.6, -6.9); desk(-5.6, -6.9, 0x9ff0c0); desk(-2.6, -6.9, 0xffd27a);
  w.hot(-5.6, -5.6, 'Sit at my desk', 'skills');
  // whiteboard
  sign(s, ['devices → ingestion → MQTT', '→ ETL → Kafka / InfluxDB → cloud'], 3.4, 1.0, -3, 1.75, -7.84, { size: 0.17, fg: '#3f6f9f', border: '#9aa3ad', bg: '#ffffff' });
  // server rack
  box(s, 1, 2, 0.9, 0x2c2b33, -10.2, 0, -3.2);
  const leds = [];
  for (let i = 0; i < 14; i++) leds.push(box(s, 0.08, 0.05, 0.02, glowM(i % 3 ? 0x5fff9a : 0xffc04a, 2.5), -10.5 + (i % 2) * 0.5 + 0.05, 0.25 + Math.floor(i / 2) * 0.24, -2.74));
  for (let i = 0; i < 7; i++) box(s, 0.86, 0.02, 0.02, 0x4a4954, -10.2, 0.2 + i * 0.24, -2.74);
  w.ticks.push((t) => leds.forEach((l, i) => { l.visible = Math.sin(t * (3 + i) + i * 1.7) > -0.3; }));
  w.solid(-10.2, -3.2, 1, 0.9);
  w.hot(-9.6, -2.6, 'Inspect the server rack', 'core', { y: 2.6 });
  w.hot(-3, -6, 'Read the whiteboard', 'pipeline', { y: 2.8, r: 1.4 });
  plant(s, -0.7, 0, -2.2);

  // --- ARCHIVE ---
  const cols = [0xd9483b, 0x3f8fd1, 0xf2c94c, 0x5fa46b, 0x9d8bd3, 0xe8a05a];
  for (let k = 0; k < 3; k++) {
    const x = 2.6 + k * 3;
    box(s, 2.6, 2.1, 0.5, 0x8f6440, x, 0, -7.55);
    for (let r = 0; r < 3; r++) for (let i = 0; i < 9; i++) box(s, 0.2, 0.46, 0.3, cols[(i * 5 + r + k) % 6], x - 1 + i * 0.25, 0.14 + r * 0.66, -7.35);
    w.solid(x, -7.55, 2.6, 0.5);
  }
  const files = [['traffic', 0x3f8fd1, 'TRAFFIC'], ['logistics', 0x5fa46b, 'LOGISTICS'], ['v2x', 0x9d8bd3, 'V2X · WATER'], ['tools', 0xe8a05a, 'TOOLS · OPS']];
  files.forEach(([key, c, name], i) => {
    const x = 2.6 + i * 2.2, z = -4.4;
    box(s, 1, 1.25, 0.8, 0x8d949c, x, 0, z);
    for (let d = 0; d < 3; d++) { box(s, 0.86, 0.33, 0.03, c, x, 0.08 + d * 0.39, z + 0.41); box(s, 0.25, 0.05, 0.05, 0xf4f0e6, x, 0.22 + d * 0.39, z + 0.44); }
    sign(s, name, 0.95, 0.24, x, 1.42, z + 0.3, { size: 0.12, bg: '#fffaf0', fg: '#3b3a4a' }).rotation.x = -0.5;
    w.solid(x, z, 1, 0.8);
    w.hot(x, z + 0.9, `Open the "${name}" cabinet`, key, { y: 2.2, r: 1.25, color: c });
  });
  box(s, 0.7, 0.5, 0.6, 0xc9a27a, 10.2, 0, -2.3); box(s, 0.7, 0.5, 0.6, 0xc9a27a, 10.15, 0.5, -2.35).rotation.y = 0.2;
  w.solid(10.2, -2.3, 0.8, 0.7);

  // --- CORRIDOR: reception ---
  box(s, 2.6, 1, 0.7, 0xd9b991, 0, 0, -0.9); box(s, 2.8, 0.08, 0.9, 0x8f6440, 0, 1, -0.9);
  sign(s, ['DEBY ANGELINA', 'Backend / Platform Engineer'], 2.4, 0.7, 0, 0.5, -0.54, { size: [0.2, 0.12], fg: ['#3b3a4a', '#b0563f'], bg: '#fffaf0' });
  box(s, 0.14, 0.18, 0.14, glowM(0xffd27a, 2), 1, 1.08, -0.9);
  w.solid(0, -0.9, 2.6, 0.7);
  w.hot(0, 0, 'Ring the reception bell', 'naonworks', { y: 2 , r: 1.5 });
  plant(s, -10.3, 0, 0.9, 1.2); plant(s, 10.3, 0, -0.9, 1.2); plant(s, -1.5, 0, 7.3); plant(s, 1.5, 0, 7.3);
  box(s, 1.6, 0.03, 1, 0xb0563f, 0, 0, 6.2);

  // --- MEETING ROOM ---
  box(s, 4, 0.1, 1.6, 0xd9b991, -6.5, 0.72, 5.2); box(s, 0.3, 0.72, 0.3, 0x8f6440, -8, 0, 5.2); box(s, 0.3, 0.72, 0.3, 0x8f6440, -5, 0, 5.2);
  w.solid(-6.5, 5.2, 4, 1.6);
  for (const x of [-7.8, -6.5, -5.2]) { chair(x, 6.6, 0x5f8a5a); const c = group(s, x, 0, 3.8, Math.PI); cyl(c, 0.28, 0.28, 0.08, 0x5f8a5a, 0, 0.45, 0, 10); cyl(c, 0.04, 0.04, 0.45, 0x5b5560, 0, 0, 0, 6); box(c, 0.5, 0.5, 0.06, 0x5f8a5a, 0, 0.5, 0.27); }
  box(s, 0.08, 1.3, 2.4, 0x2c2b33, -10.8, 0.9, 5.2); box(s, 0.02, 1.15, 2.2, glowM(0xcfe6ff, 1.2), -10.74, 0.97, 5.2);
  sign(s, ['own the system,', 'not the ticket'], 2.1, 1.0, -10.72, 1.55, 5.2, { size: 0.2, bg: null, fg: '#2f3b52', ry: Math.PI / 2 });
  w.hot(-9.8, 5.2, 'Watch the presentation', 'ethic', { y: 2.8, r: 1.4 });
  sign(s, ['THE UNGLAMOROUS FIXES', 'dispose-race · int cast · atomic coils'], 3, 0.8, -9.3, 0.75, 1.64, { size: [0.17, 0.11], fg: ['#b0563f', '#3b3a4a'], border: '#c9b79c' });
  w.hot(-9.3, 2.5, 'Read the incident board', 'fixes', { y: 2, r: 1.4 });

  // --- PANTRY ---
  box(s, 0.9, 1.9, 0.8, 0xe8ecef, 2.8, 0, 2.15); box(s, 0.05, 0.6, 0.05, 0x9aa3ad, 3.1, 0.8, 2.57); w.solid(2.8, 2.15, 0.9, 0.8);
  box(s, 2.8, 0.9, 0.7, 0xf4f0e6, 9.3, 0, 2.05); box(s, 2.9, 0.06, 0.8, 0x8f6440, 9.3, 0.9, 2.05); w.solid(9.3, 2.05, 2.8, 0.7);
  box(s, 0.45, 0.55, 0.4, 0x2c2b33, 8.6, 0.96, 2.0); box(s, 0.1, 0.1, 0.02, glowM(0xff6b4a, 2.5), 8.6, 1.35, 2.21);
  cyl(s, 0.09, 0.07, 0.16, 0xffffff, 9.3, 0.96, 2.15, 8); cyl(s, 0.09, 0.07, 0.16, 0xffb7c9, 9.6, 0.96, 2.1, 8); cyl(s, 0.09, 0.07, 0.16, 0x9fd0ff, 9.9, 0.96, 2.2, 8);
  w.hot(8.8, 3, 'Make a coffee', 'fuel', { y: 2.3, r: 1.4 });
  cyl(s, 1, 1, 0.08, 0xd9b991, 6.6, 0.72, 5.6, 16); cyl(s, 0.1, 0.3, 0.72, 0x8f6440, 6.6, 0, 5.6, 8); w.solid(6.6, 5.6, 1.8, 1.8);
  for (let i = 0; i < 4; i++) cyl(s, 0.25, 0.25, 0.5, [0xc9604a, 0xf2c94c][i % 2], 6.6 + Math.cos(i * 1.57 + 0.8) * 1.5, 0, 5.6 + Math.sin(i * 1.57 + 0.8) * 1.5, 10);
  // the one arcade machine
  const ag = group(s, 4.4, 0, 2.15);
  box(ag, 1, 1.9, 0.85, 0x5b3fa0, 0, 0, 0); box(ag, 1.04, 0.35, 0.9, 0xff5fa2, 0, 1.9, 0);
  const scr = box(ag, 0.8, 0.6, 0.03, glowM(0x7fffd0, 1.8), 0, 1.15, 0.43);
  box(ag, 1, 0.1, 0.5, 0x2c2b33, 0, 0.9, 0.5).rotation.x = 0.25;
  sph(ag, 0.07, glowM(0xff3b30, 2), -0.2, 1.05, 0.6); cyl(ag, 0.06, 0.06, 0.04, glowM(0xf2c94c, 2), 0.15, 1.0, 0.6, 8); cyl(ag, 0.06, 0.06, 0.04, glowM(0x3f8fd1, 2), 0.32, 1.0, 0.6, 8);
  sign(ag, 'BUG SQUASH', 0.95, 0.26, 0, 2.08, 0.46, { size: 0.15, bg: '#ff5fa2', fg: '#fff', glow: 1.5 });
  w.ticks.push((t) => { scr.material.color.setHSL((t * 0.15) % 1, 0.7, 0.6).multiplyScalar(1.8); });
  w.solid(4.4, 2.15, 1, 0.85);
  w.hot(4.4, 3.1, 'Play the arcade machine', 'arcade', { y: 2.9, r: 1.3, color: 0xff5fa2 });

  const crack = makeCrack(0xbfe4ea); crack.position.set(0, 0, 7.6); s.add(crack);
  w.ticks.push((t) => { crack.tick(t); crack.scale.multiplyScalar(0.5); });
  w.hot(0, 7.0, 'Step back to the terminal', 'terminal', { y: 2.6, color: 0xbfe4ea, r: 1.3 });

  return w.finish();
}
