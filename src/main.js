import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { box, cyl, sph, group } from './kit.js';
import { CONTENT } from './content.js';
import { buildTerminal } from './worlds/terminal.js';
import { buildHome } from './worlds/home.js';
import { buildOffice } from './worlds/office.js';
import { buildMarket } from './worlds/market.js';
import { openArcade, closeArcade } from './arcade.js';

const $ = (id) => document.getElementById(id);
const canvas = $('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 1000);

const worlds = { terminal: buildTerminal(), home: buildHome(), office: buildOffice(), market: buildMarket() };
let world = worlds.terminal;

const composer = new EffectComposer(renderer);
const renderPass = new RenderPass(world.scene, camera);
const bloom = new UnrealBloomPass(new THREE.Vector2(1, 1), 0.5, 0.6, 1.0);
composer.addPass(renderPass); composer.addPass(bloom); composer.addPass(new OutputPass());

// ---------- the little traveller ----------
const player = new THREE.Group();
const legs = [-0.12, 0.12].map((x) => { const g = group(player, x, 0.45, 0); box(g, 0.17, 0.45, 0.19, 0x2f3b6b, 0, -0.45, 0); return g; });
const body = group(player, 0, 0.45, 0);
box(body, 0.52, 0.55, 0.3, 0xd3323f, 0, 0, 0);                 // the red cardigan
box(body, 0.2, 0.5, 0.31, 0x8f1f2c, 0, 0.05, 0.005);
const arms = [-0.33, 0.33].map((x) => { const g = group(body, x, 0.52, 0); box(g, 0.13, 0.5, 0.15, 0xd3323f, 0, -0.5, 0); sph(g, 0.07, 0xf2c9a4, 0, -0.55, 0, 0); return g; });
sph(body, 0.25, 0xf2c9a4, 0, 0.8, 0, 2, { flatShading: false });
const hair = sph(body, 0.275, 0x1f1a1c, 0, 0.84, -0.05, 2, { flatShading: false }); hair.scale.set(1, 1, 0.95);
box(body, 0.5, 0.5, 0.14, 0x1f1a1c, 0, 0.4, -0.2);
for (const x of [-0.1, 0.1]) { const t = new THREE.Mesh(new THREE.TorusGeometry(0.065, 0.012, 6, 14), new THREE.MeshBasicMaterial({ color: 0x2c2b33 })); t.position.set(x, 0.82, 0.235); body.add(t); }
player.traverse((o) => { if (o.isMesh) o.castShadow = true; });
function swing(moving, t) {
  const sw = moving ? Math.sin(walkPhase) * 0.7 : 0;
  legs[0].rotation.x = sw; legs[1].rotation.x = -sw; arms[0].rotation.x = -sw * 0.8; arms[1].rotation.x = sw * 0.8;
  body.position.y = 0.45 + (moving ? Math.abs(Math.sin(walkPhase)) * 0.05 : Math.sin(t * 2) * 0.008);
}
function pose(sitting) { legs.forEach((l) => { l.rotation.x = sitting ? -Math.PI / 2 : 0; }); arms.forEach((a) => { a.rotation.x = sitting ? -0.5 : 0; }); body.position.y = 0.45; }

// the view you see inside the crack: a live render of the destination
const portalRT = new THREE.WebGLRenderTarget(512, 896);
const portalCam = new THREE.PerspectiveCamera(58, 0.57, 0.1, 1000);
const PORTAL = { home: [[0, 6.5, 19], [0, 1.5, 0]], office: [[7, 13, 17], [0, 0, 0]], market: [[0, 5.5, 21], [0, 2.5, -2]] };
let dest = null, arriveT = 0;

// ---------- state ----------
let state = 'walk';            // walk | sit | depart
let yaw = 0, pitch = 0.5, dist = 10, walkPhase = 0, activeHot = null, panelHot = null, busy = false;
const look = new THREE.Vector3(), tmp = new THREE.Vector3();
const keys = new Set(), joy = { x: 0, y: 0 };

function enter(name, swoop) {
  world = worlds[name];
  renderPass.scene = world.scene;
  world.scene.add(player);
  player.position.copy(world.spawn); player.rotation.y = world.spawnYaw; pose(false);
  ({ yaw, pitch, dist } = world.cam);
  bloom.strength = world.bloom;
  worlds.terminal.reset();
  state = 'walk'; closePanel(); $('tickets').hidden = true;
  $('where').textContent = world.title;
  document.querySelectorAll('#nav button').forEach((b) => b.classList.toggle('on', b.dataset.go === name));
  history.replaceState(null, '', name === 'terminal' ? location.pathname : '#' + name);
  if (swoop && PORTAL[name]) { camera.position.set(...PORTAL[name][0]); look.set(...PORTAL[name][1]); camera.lookAt(look); arriveT = 2.2; }
  else placeCamera(1);
}
function go(name, swoop) {
  if (busy || !worlds[name]) return;
  busy = true; $('fade').classList.add('on');
  setTimeout(() => { enter(name, swoop); $('fade').classList.remove('on'); busy = false; }, 480);
}

const sitHot = worlds.terminal.hots.find((h) => h.action === 'sit');

// ---------- UI ----------
function showPanel(key, hot) {
  const c = CONTENT[key]; if (!c) return;
  $('kicker').textContent = c.kicker; $('ptitle').textContent = c.title;
  $('pbody').innerHTML = c.body + (c.todo ? `<div class="todo">${c.todo}</div>` : '');
  $('plinks').innerHTML = (c.links || []).map(([l, u]) => `<a href="${u}" target="_blank" rel="noopener">${l} ↗</a>`).join('');
  $('panel').hidden = false; $('panel').scrollTop = 0; panelHot = hot;
}
function closePanel() { $('panel').hidden = true; panelHot = null; }
function sit() {
  state = 'sit'; closePanel();
  player.position.copy(worlds.terminal.chair); player.position.z += 0.02; player.rotation.y = Math.PI; pose(true);
  $('tickets').hidden = false;
}
function stand() { state = 'walk'; pose(false); player.position.set(0, world.groundY, 2.85); $('tickets').hidden = true; }
function interact() {
  if (state !== 'walk' || !activeHot || busy) return;
  const a = activeHot.action;
  if (a === 'sit') sit();
  else if (a === 'arcade') { keys.clear(); openArcade(); }
  else if (worlds[a]) go(a);
  else showPanel(a, activeHot);
}
$('prompt').addEventListener('click', interact);
$('close').addEventListener('click', closePanel);
$('stand').addEventListener('click', stand);
document.querySelectorAll('#tickets [data-dest]').forEach((b) => b.addEventListener('click', () => {
  if (state !== 'sit') return;
  state = 'depart'; $('tickets').hidden = true; dest = b.dataset.dest;
  portalCam.position.set(...PORTAL[dest][0]); portalCam.lookAt(...PORTAL[dest][1]);
  worlds.terminal.crack.setPortal(portalRT.texture);
  worlds.terminal.depart(dest, () => go(dest, true));
}));
document.querySelectorAll('#nav button').forEach((b) => b.addEventListener('click', () => go(b.dataset.go)));
$('start').addEventListener('click', () => $('intro').classList.add('gone'));

// ---------- input ----------
addEventListener('keydown', (e) => {
  if (!$('arcade').hidden) { if (e.key === 'Escape') closeArcade(); return; }
  const k = e.key.toLowerCase();
  if (k === 'e' || k === 'enter') { if (!$('intro').classList.contains('gone')) $('intro').classList.add('gone'); else interact(); }
  else if (k === 'escape') { if (state === 'sit') stand(); else closePanel(); }
  else keys.add(k);
});
addEventListener('keyup', (e) => keys.delete(e.key.toLowerCase()));
addEventListener('blur', () => keys.clear());
let drag = null;
canvas.addEventListener('pointerdown', (e) => { drag = { id: e.pointerId, x: e.clientX, y: e.clientY }; canvas.setPointerCapture(e.pointerId); });
canvas.addEventListener('pointermove', (e) => {
  if (!drag || drag.id !== e.pointerId) return;
  yaw -= (e.clientX - drag.x) * 0.005; pitch = THREE.MathUtils.clamp(pitch + (e.clientY - drag.y) * 0.004, 0.1, 1.4);
  drag.x = e.clientX; drag.y = e.clientY;
});
const endDrag = (e) => { if (drag && drag.id === e.pointerId) drag = null; };
canvas.addEventListener('pointerup', endDrag); canvas.addEventListener('pointercancel', endDrag);
canvas.addEventListener('wheel', (e) => { e.preventDefault(); dist = THREE.MathUtils.clamp(dist * (1 + Math.sign(e.deltaY) * 0.1), 4, 22); }, { passive: false });
if (matchMedia('(pointer: coarse)').matches) {
  const j = $('joy'), nub = j.firstElementChild; j.hidden = false;
  const move = (e) => {
    const r = j.getBoundingClientRect();
    let x = (e.clientX - r.left - r.width / 2) / (r.width / 2), y = (e.clientY - r.top - r.height / 2) / (r.height / 2);
    const l = Math.hypot(x, y); if (l > 1) { x /= l; y /= l; }
    joy.x = x; joy.y = -y; nub.style.transform = `translate(${x * 34}px, ${y * 34}px)`;
  };
  j.addEventListener('pointerdown', (e) => { j.setPointerCapture(e.pointerId); move(e); });
  j.addEventListener('pointermove', (e) => { if (j.hasPointerCapture(e.pointerId)) move(e); });
  const up = () => { joy.x = joy.y = 0; nub.style.transform = ''; };
  j.addEventListener('pointerup', up); j.addEventListener('pointercancel', up);
}

// ---------- loop ----------
function placeCamera(k) {
  if (state === 'walk') {
    tmp.copy(player.position); tmp.y += 1.2;
    look.lerp(tmp, k);
    tmp.set(Math.sin(yaw) * Math.cos(pitch), Math.sin(pitch), Math.cos(yaw) * Math.cos(pitch)).multiplyScalar(dist).add(look);
    camera.position.lerp(tmp, k);
  } else {
    const c = worlds.terminal.cine;
    if (c.snap) { k = 1; c.snap = false; }
    camera.position.lerp(c.pos, k); look.lerp(c.look, k);
    bloom.strength = world.bloom + c.glow;
  }
  camera.lookAt(look);
  if (state !== 'walk') { const c = worlds.terminal.cine; camera.position.x += (Math.random() - 0.5) * c.shake; camera.position.y += (Math.random() - 0.5) * c.shake; }
}
function resize() {
  const w = innerWidth, h = innerHeight;
  renderer.setSize(w, h, false); composer.setSize(w, h);
  camera.aspect = w / h; camera.fov = w < h ? 62 : 50; camera.updateProjectionMatrix();
}
addEventListener('resize', resize);

const clock = new THREE.Clock();
function frame() {
  const dt = Math.min(clock.getDelta(), 0.05), t = clock.elapsedTime;
  let moving = false;
  if (state === 'walk' && $('arcade').hidden) {
    let ix = joy.x, iy = joy.y;
    if (keys.has('w') || keys.has('arrowup')) iy += 1;
    if (keys.has('s') || keys.has('arrowdown')) iy -= 1;
    if (keys.has('d') || keys.has('arrowright')) ix += 1;
    if (keys.has('a') || keys.has('arrowleft')) ix -= 1;
    const l = Math.hypot(ix, iy);
    if (l > 0.08) {
      moving = true;
      const sp = 4.6 * Math.min(1, l) * dt / l;
      const mx = (Math.cos(yaw) * ix - Math.sin(yaw) * iy) * sp, mz = (-Math.sin(yaw) * ix - Math.cos(yaw) * iy) * sp;
      const p = player.position;
      if (world.canWalk(p.x + mx, p.z)) p.x += mx;
      if (world.canWalk(p.x, p.z + mz)) p.z += mz;
      let d = Math.atan2(mx, mz) - player.rotation.y;
      d = Math.atan2(Math.sin(d), Math.cos(d));
      player.rotation.y += d * Math.min(1, dt * 12);
      walkPhase += dt * 11;
    }
    swing(moving, t);

    // nearest hotspot
    let best = null, bd = 1e9;
    for (const h of world.hots) { const d = Math.hypot(h.x - player.position.x, h.z - player.position.z); if (d < h.r && d < bd) { best = h; bd = d; } }
    if (panelHot && Math.hypot(panelHot.x - player.position.x, panelHot.z - player.position.z) > panelHot.r * 1.7) closePanel();
    activeHot = best;
  } else activeHot = null;
  if (state === 'depart') {
    const q = worlds.terminal.seqT;
    if (q > 5.7) {                       // stand up, walk off the platform and into the crack
      const k = THREE.MathUtils.clamp((q - 5.95) / 1.5, 0, 1);
      player.position.set(0, 0.6 - 0.4 * THREE.MathUtils.smoothstep(k, 0.34, 0.48), 1.2 - k * 3.3);
      walkPhase += dt * 10; swing(k > 0 && k < 1, t);
    }
    if (q > 3.6 && dest) {               // render the destination into the crack
      worlds[dest].update(t, dt);
      renderer.setRenderTarget(portalRT); renderer.render(worlds[dest].scene, portalCam); renderer.setRenderTarget(null);
    }
  }
  const show = activeHot && activeHot !== panelHot && !busy;
  if (show) $('prompt').textContent = activeHot.label;
  $('prompt').hidden = !show;

  world.update(t, dt);
  sitHot.mark.visible = state === 'walk';
  if (world.sun) { world.sun.target.position.copy(player.position); world.sun.position.copy(player.position).add(world.sun.userData.offset); }
  arriveT = Math.max(0, arriveT - dt);
  placeCamera(1 - Math.exp(-dt * (state !== 'walk' ? 2.5 : arriveT > 0 ? 1.6 + (2.2 - arriveT) * 2.4 : 7)));
  composer.render();
  requestAnimationFrame(frame);
}

resize();
const start = location.hash.slice(1);
enter(worlds[start] ? start : 'terminal');
window.portfolio = { go, worlds, player, get state() { return state; } };
frame();
