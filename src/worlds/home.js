// Home: a studio floating in space, under a glass dome.
import * as THREE from 'three';
import { makeWorld, box, cyl, cone, sph, group, sign, stars, glowM, makeCrack, plant, photo, M } from '../kit.js';

export function buildHome() {
  const w = makeWorld('home', 'Home among the stars');
  const s = w.scene;
  w.spawn.set(0, 0, 4.6);
  w.cam = { dist: 11, pitch: 0.55, yaw: 0.45 };
  w.bloom = 0.5;
  s.background = new THREE.Color(0x04050d);
  s.add(new THREE.HemisphereLight(0x9fb0ff, 0x4a3a5a, 1.3));
  w.sunlight(0xdfe6ff, 1.5, 7, 14, 6);
  const R = 9;
  w.inside = (x, z) => x * x + z * z < (R - 0.7) ** 2;

  // --- the sky outside ---
  const st = stars(s, 3500, 180, 400, 1.5);
  w.ticks.push((t) => { st.rotation.y = t * 0.004; });
  const blob = (hex, x, y, z, sc) => {
    const c = document.createElement('canvas'); c.width = c.height = 128;
    const g = c.getContext('2d'), gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    gr.addColorStop(0, hex); gr.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), blending: THREE.AdditiveBlending, opacity: 0.4, depthWrite: false }));
    sp.position.set(x, y, z); sp.scale.setScalar(sc); s.add(sp);
  };
  blob('#6a4cff', -120, 40, -160, 220); blob('#ff5fa2', 90, -20, -170, 180); blob('#2fd3c9', 150, 70, 60, 200); blob('#4466ff', -100, -60, 120, 220);
  const planet = sph(s, 16, 0xd9916b, -46, 6, -62, 3, { flatShading: false });
  const ring = new THREE.Mesh(new THREE.RingGeometry(21, 30, 48), new THREE.MeshBasicMaterial({ color: 0xf1d3a8, side: THREE.DoubleSide, transparent: true, opacity: 0.55 }));
  ring.position.copy(planet.position); ring.rotation.set(1.25, 0.3, 0); s.add(ring);
  sph(s, 3, 0xcfd6e6, 38, 24, -50, 2, { flatShading: false });
  planet.userData.noShadow = true;
  w.ticks.push((t) => { planet.rotation.y = t * 0.02; });
  // a shooting star every so often
  const shoot = box(s, 6, 0.06, 0.06, glowM(0xffffff, 3), 0, 0, 0);
  w.ticks.push((t) => { const k = (t % 9) / 1.2; shoot.visible = k < 1; shoot.position.set(60 - k * 120, 50 - k * 30, -90); shoot.rotation.z = 0.25; });

  // --- the station ---
  cyl(s, R, R, 0.4, 0xc9a27a, 0, -0.4, 0, 40);
  cyl(s, R + 0.5, R + 0.3, 0.5, 0xe8e4f0, 0, -0.6, 0, 40);
  cyl(s, R + 0.3, 4, 2.6, 0x3a4160, 0, -3.2, 0, 40);
  cyl(s, 4, 1.2, 1.6, 0x2b3050, 0, -4.8, 0, 24);
  const halo = new THREE.Mesh(new THREE.TorusGeometry(R + 0.55, 0.07, 6, 80), glowM(0x7fe3ff, 2.5));
  halo.rotation.x = Math.PI / 2; halo.position.y = -0.75; halo.userData.noShadow = true; s.add(halo);
  const dome = new THREE.Mesh(new THREE.SphereGeometry(R + 0.2, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2),
    new THREE.MeshBasicMaterial({ color: 0x9fc4ff, transparent: true, opacity: 0.07, side: THREE.DoubleSide, depthWrite: false }));
  s.add(dome);
  for (let i = 0; i < 4; i++) {
    const rib = new THREE.Mesh(new THREE.TorusGeometry(R + 0.2, 0.05, 6, 48, Math.PI), M(0xe8ecff));
    rib.rotation.y = (i / 4) * Math.PI; rib.userData.noShadow = true; s.add(rib);
  }
  cyl(s, 2.8, 2.8, 0.03, 0x7d6bb3, 0, 0, 0, 32); cyl(s, 2.1, 2.1, 0.035, 0x9d8bd3, 0, 0, 0, 32);

  const face = (x, z) => Math.atan2(-x, -z); // rotate a piece so its front looks at the centre

  // memory wall: photo + who I am
  { const x = -5.2, z = -4.4, g = group(s, x, 0, z, face(x, z));
    box(g, 3.4, 2.4, 0.12, 0xe9dcc6, 0, 0.5, 0); box(g, 0.1, 0.5, 0.4, 0x8f6440, -1.4, 0, 0); box(g, 0.1, 0.5, 0.4, 0x8f6440, 1.4, 0, 0);
    photo(g, 'photos/deby-cherry-blossom.jpeg', 1.5, 1.5, -0.7, 1.75, 0.13);
    sign(g, ['Deby Angelina', '안젤리나 데비', 'Semarang → Seoul'], 1.3, 1.2, 0.9, 1.75, 0.07, { size: [0.17, 0.14, 0.11], fg: ['#3b3a4a', '#6a5a8a', '#b0563f'], bg: '#fffaf0' });
    w.solid(x, z, 2.6, 2.6); w.hot(x + 1.1, z + 1.0, 'Look at the memory wall', 'about', { y: 3.4, r: 2.4 }); }

  // desk + globe: the journey
  { const x = 6, z = -1.2, g = group(s, x, 0, z, face(x, z));
    box(g, 2.2, 0.08, 1, 0xb98556, 0, 0.8, 0); for (const [a, b] of [[-1, -0.4], [1, -0.4], [-1, 0.4], [1, 0.4]]) box(g, 0.08, 0.8, 0.08, 0x8f6440, a, 0, b);
    const gl = sph(g, 0.3, 0x4f9fd8, -0.6, 1.3, 0, 2, { flatShading: false }); cyl(g, 0.12, 0.16, 0.1, 0x8f6440, -0.6, 0.88, 0);
    sph(g, 0.31, 0x6fbf73, -0.55, 1.33, 0.02, 0).scale.set(0.7, 0.6, 0.9);
    box(g, 0.9, 0.55, 0.05, 0x2c2b33, 0.4, 0.95, -0.2); box(g, 0.8, 0.45, 0.02, glowM(0x9fd0ff, 1.3), 0.4, 1.0, -0.17);
    w.ticks.push((t) => { gl.rotation.y = t * 0.4; });
    w.solid(x, z, 1.6, 2.2); w.hot(x - 1, z, 'Spin the globe', 'journey'); }

  // bookshelf: education
  { const x = -7.2, z = 1.6, g = group(s, x, 0, z, face(x, z));
    box(g, 2.4, 2.2, 0.5, 0x8f6440, 0, 0, 0);
    const cols = [0xd9483b, 0x3f8fd1, 0xf2c94c, 0x5fa46b, 0x9d8bd3, 0xf4f0e6];
    for (let r = 0; r < 3; r++) for (let i = 0; i < 9; i++) box(g, 0.18, 0.42 + (i % 3) * 0.06, 0.3, cols[(i + r) % 6], -0.95 + i * 0.24, 0.2 + r * 0.68, 0.16);
    w.solid(x, z, 1.2, 2.4); w.hot(x + 1, z, 'Browse the bookshelf', 'education'); }

  // easel: art
  { const x = 3.6, z = -5.6, g = group(s, x, 0, z, face(x, z));
    for (const a of [-0.5, 0.5]) { const l = box(g, 0.07, 2.2, 0.07, 0x8f6440, a, 0, 0); l.rotation.z = -a * 0.3; }
    box(g, 0.07, 2.1, 0.07, 0x8f6440, 0, 0, -0.5).rotation.x = -0.3;
    box(g, 1.3, 1, 0.06, 0xfffaf0, 0, 0.9, 0.1);
    box(g, 0.5, 0.5, 0.02, 0xffb7c9, -0.2, 1.3, 0.14); box(g, 0.4, 0.3, 0.02, 0x8fb4ff, 0.3, 1.1, 0.14); box(g, 0.3, 0.2, 0.02, 0xf2c94c, 0, 1.0, 0.145);
    cyl(g, 0.3, 0.3, 0.5, 0x6a5a8a, 1.1, 0, 0.3, 10);
    w.solid(x, z, 1.5, 1.2); w.hot(x - 0.6, z + 1, 'Look at the easel', 'art'); }

  // TV + beanbag: play
  { const x = 4.6, z = 4.6, g = group(s, x, 0, z, face(x, z));
    box(g, 2, 0.5, 0.5, 0x5b5560, 0, 0, 0); box(g, 1.8, 1.05, 0.08, 0x2c2b33, 0, 0.6, 0);
    box(g, 1.65, 0.9, 0.02, glowM(0x7fe3c0, 1.4), 0, 0.68, 0.05);
    box(g, 0.4, 0.1, 0.3, 0xf4f0e6, -0.5, 0.5, 0.05);
    sph(g, 0.6, 0xff8fab, 0.2, 0.35, 2, 1).scale.y = 0.6;
    w.solid(x, z, 1.6, 1.6); w.hot(x - 0.9, z - 0.9, 'Pick up the controller', 'play'); }

  // telescope: the dream
  { const x = 0, z = -7, g = group(s, x, 0, z);
    for (let i = 0; i < 3; i++) { const l = cyl(g, 0.04, 0.04, 1.5, 0x5b5560, Math.cos(i * 2.1) * 0.35, 0, Math.sin(i * 2.1) * 0.35, 5); l.rotation.set(Math.sin(i * 2.1) * 0.3, 0, -Math.cos(i * 2.1) * 0.3); }
    const tube = cyl(g, 0.2, 0.14, 1.8, 0xe8e4f0, 0, 1.1, -0.2, 12); tube.rotation.x = -0.9;
    w.solid(x, z, 0.9, 0.9); w.hot(x, z + 0.8, 'Look through the telescope', 'dream'); }

  // bed, lamp, plants: just cosy
  { const x = -3.4, z = 5.8, g = group(s, x, 0, z, face(x, z) + Math.PI / 2);
    box(g, 3, 0.4, 1.6, 0x8f6440, 0, 0, 0); box(g, 2.9, 0.25, 1.5, 0xf4f0e6, 0, 0.4, 0); box(g, 1.9, 0.27, 1.52, 0x6a7fd0, 0.5, 0.4, 0); box(g, 0.6, 0.15, 1, 0xffffff, -1.1, 0.65, 0);
    w.solid(x, z, 2.6, 2.6); }
  cyl(s, 0.04, 0.04, 1.7, 0x5b5560, -1.2, 0, -6.6, 6); cone(s, 0.35, 0.4, glowM(0xffd9a0, 1.6), -1.2, 1.6, -6.6, 10);
  const pl = new THREE.PointLight(0xffc98a, 14, 16); pl.position.set(-1.2, 2.2, -5.8); s.add(pl);
  const pl2 = new THREE.PointLight(0xffc98a, 14, 14); pl2.position.set(2, 2.5, 3); s.add(pl2);
  plant(s, 7.4, 0, 2.2, 1.3); plant(s, -7.6, 0, -1.2, 1.2); plant(s, 1.8, 0, 7.6, 1); plant(s, -6.2, 0, 4.4, 0.9);

  const crack = makeCrack(0xbfe4ea); crack.position.set(0, 0, 7.4); crack.scale.setScalar(0.7); s.add(crack);
  w.ticks.push((t) => { crack.tick(t); crack.scale.multiplyScalar(0.62); });
  w.hot(0, 7.0, 'Step back to the terminal', 'terminal', { y: 3.2, color: 0xbfe4ea, r: 1.5 });

  return w.finish();
}
