// Hand-painted surfaces. Each kind of surface (grass, sand, concrete, wood...) gets a tileable texture painted from
// thousands of brush strokes, then projected onto the models from above and from the sides (triplanar), so no UV maps
// are needed. Blender material names say what a surface is: c_<hex colour>.
import * as THREE from 'three';

const SIZE = 512;
function rng(seed) { return () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

// Tileable value noise, so light and dark patches wrap around the edges of the texture.
function noiseField(rand, cells) {
  const g = Array.from({ length: cells * cells }, rand);
  const at = (i, j) => g[((j % cells) + cells) % cells * cells + ((i % cells) + cells) % cells];
  return (x, y) => {
    const u = (x / SIZE) * cells, v = (y / SIZE) * cells, i = Math.floor(u), j = Math.floor(v), fu = u - i, fv = v - j;
    const s = (t) => t * t * (3 - 2 * t), a = at(i, j) + (at(i + 1, j) - at(i, j)) * s(fu), b = at(i, j + 1) + (at(i + 1, j + 1) - at(i, j + 1)) * s(fu);
    return a + (b - a) * s(fv);
  };
}
const fbm = (n1, n2, n3) => (x, y) => n1(x, y) * 0.55 + n2(x, y) * 0.3 + n3(x, y) * 0.15;

// Draw something that may cross the edge also on the opposite side, so the texture tiles seamlessly.
function wrap(x, y, r, draw) {
  for (const dx of [-SIZE, 0, SIZE]) for (const dy of [-SIZE, 0, SIZE]) {
    const X = x + dx, Y = y + dy;
    if (X + r < 0 || X - r > SIZE || Y + r < 0 || Y - r > SIZE) continue;
    draw(X, Y);
  }
}
const pick = (arr, k) => arr[Math.max(0, Math.min(arr.length - 1, Math.floor(k * arr.length)))];

// A tapered brush stroke: thick at the base, pointed at the tip, gently curved.
function stroke(g, x, y, len, wid, ang, bend, color, alpha) {
  const dx = Math.cos(ang), dy = Math.sin(ang), nx = -dy, ny = dx;
  const tx = x + dx * len, ty = y + dy * len, cx = x + dx * len * 0.5 + nx * bend, cy = y + dy * len * 0.5 + ny * bend;
  g.globalAlpha = alpha; g.fillStyle = color; g.beginPath();
  g.moveTo(x + nx * wid, y + ny * wid); g.quadraticCurveTo(cx + nx * wid * 0.6, cy + ny * wid * 0.6, tx, ty);
  g.quadraticCurveTo(cx - nx * wid * 0.6, cy - ny * wid * 0.6, x - nx * wid, y - ny * wid); g.closePath(); g.fill();
}
function dab(g, x, y, rx, ry, ang, color, alpha) {
  g.globalAlpha = alpha; g.fillStyle = color; g.beginPath(); g.ellipse(x, y, rx, ry, ang, 0, 6.2832); g.fill();
}

const PAINTERS = {
  // Grass, combed in one direction, dappled with light patches; a scatter of tiny white flowers.
  grass(g, r) {
    const light = fbm(noiseField(r, 3), noiseField(r, 7), noiseField(r, 15)), flow = noiseField(r, 3);
    // from cool blue-green shade up to warm sunlit yellow-green, like the Ghibli palette
    const tones = ['#163a37', '#1d4b3c', '#26603f', '#327642', '#468d43', '#64a745', '#8cc350', '#b8dc66', '#e0ef8c'];
    g.fillStyle = '#2c6640'; g.fillRect(0, 0, SIZE, SIZE);
    for (let i = 0; i < 220; i++) { const x = r() * SIZE, y = r() * SIZE, k = light(x, y); wrap(x, y, 60, (X, Y) => dab(g, X, Y, 30 + r() * 40, 16 + r() * 22, r() * 3, pick(tones, k * 0.95), 0.45)); }
    for (let i = 0; i < 4200; i++) {                                            // bold leafy strokes, combed one way
      const x = r() * SIZE, y = r() * SIZE, k = light(x, y), shade = Math.min(0.999, Math.max(0, (k - 0.5) * 1.7 + 0.5 + (r() - 0.5) * 0.3));
      const a = -1.3 + (flow(x, y) - 0.5) * 1.4 + (r() - 0.5) * 0.6, len = 12 + r() * 20;
      wrap(x, y, len + 6, (X, Y) => stroke(g, X, Y, len, 2.2 + r() * 2.6, a, (r() - 0.5) * 9, pick(tones, shade), 0.85));
    }
    for (let i = 0; i < 900; i++) {                                             // sunlit tips catching the light
      const x = r() * SIZE, y = r() * SIZE; if (light(x, y) < 0.5) continue;
      wrap(x, y, 16, (X, Y) => stroke(g, X, Y, 8 + r() * 10, 1.6 + r(), -1.3 + (r() - 0.5) * 0.7, (r() - 0.5) * 5, pick(tones.slice(6), r()), 0.9));
    }
    for (let i = 0; i < 55; i++) {                                              // little white flowers
      const x = r() * SIZE, y = r() * SIZE;
      wrap(x, y, 5, (X, Y) => { for (let p = 0; p < 4; p++) dab(g, X + Math.cos(p * 1.57) * 2.2, Y + Math.sin(p * 1.57) * 2.2, 1.9, 1.7, 0, '#f6f8ee', 0.95); dab(g, X, Y, 1.2, 1.2, 0, '#f2d35a', 1); });
    }
  },
  // Pale beach sand: soft blotches, speckles and faint ripples.
  sand(g, r) {
    const n = fbm(noiseField(r, 3), noiseField(r, 8), noiseField(r, 20));
    g.fillStyle = '#e4d3a6'; g.fillRect(0, 0, SIZE, SIZE);
    const tones = ['#c9b382', '#d6c294', '#e2d0a3', '#ecdeb6', '#f4ead0'];
    for (let i = 0; i < 380; i++) { const x = r() * SIZE, y = r() * SIZE; wrap(x, y, 40, (X, Y) => dab(g, X, Y, 18 + r() * 26, 10 + r() * 14, r() * 3, pick(tones, n(x, y)), 0.3)); }
    for (let i = 0; i < 160; i++) { const x = r() * SIZE, y = r() * SIZE, len = 30 + r() * 50; wrap(x, y, len, (X, Y) => stroke(g, X, Y, len, 1.4, 0.1 + (r() - 0.5) * 0.3, 8, n(x, y) > 0.5 ? '#f6ecd3' : '#cdb788', 0.35)); }
    for (let i = 0; i < 5000; i++) { const x = r() * SIZE, y = r() * SIZE; dab(g, x, y, 0.7 + r() * 0.8, 0.7 + r() * 0.6, 0, r() < 0.5 ? '#b89e6c' : '#fbf3de', 0.55); }
  },
  // Weathered concrete platform: brushed patches, stains, hairline cracks, slab joints with a little moss.
  concrete(g, r) {
    const n = fbm(noiseField(r, 3), noiseField(r, 7), noiseField(r, 16));
    g.fillStyle = '#c6bca8'; g.fillRect(0, 0, SIZE, SIZE);
    const tones = ['#aca290', '#b9af9d', '#c4baa8', '#cfc6b5', '#d9d1c2'];
    for (let i = 0; i < 2600; i++) { const x = r() * SIZE, y = r() * SIZE, len = 14 + r() * 30; wrap(x, y, len, (X, Y) => stroke(g, X, Y, len, 2.5 + r() * 3.5, (r() - 0.5) * 0.25, (r() - 0.5) * 4, pick(tones, n(x, y) * 0.9 + r() * 0.1), 0.35)); }
    for (let i = 0; i < 26; i++) { const x = r() * SIZE, y = r() * SIZE; wrap(x, y, 40, (X, Y) => dab(g, X, Y, 14 + r() * 26, 8 + r() * 16, r() * 3, '#9c927f', 0.12)); }
    g.globalAlpha = 0.5; g.strokeStyle = '#8f8676'; g.lineWidth = 1;
    for (let i = 0; i < 9; i++) { let x = r() * SIZE, y = r() * SIZE; g.beginPath(); g.moveTo(x, y); for (let k = 0; k < 6; k++) { x += (r() - 0.3) * 18; y += (r() - 0.5) * 14; g.lineTo(x, y); } g.stroke(); }
    for (const x of [0, SIZE / 2]) {                                            // slab joints every 2 m
      g.globalAlpha = 0.55; g.fillStyle = '#958b7a'; g.fillRect(x - 1.5, 0, 3, SIZE);
      for (let y = 0; y < SIZE; y += 6) if (r() < 0.35) wrap(x, y, 6, (X, Y) => dab(g, X + (r() - 0.5) * 3, Y, 2 + r() * 2.5, 1.5 + r() * 2, 0, r() < 0.5 ? '#6f9a4a' : '#8cb35a', 0.7));
    }
  },
  // Gravel ballast: rounded pebbles with a lit top and a shadowed underside.
  gravel(g, r) {
    g.fillStyle = '#9b927f'; g.fillRect(0, 0, SIZE, SIZE);
    const tones = ['#8a8170', '#a39a87', '#b7ae9a', '#c9c1ae', '#7c7466'];
    for (let i = 0; i < 2200; i++) {
      const x = r() * SIZE, y = r() * SIZE, rr = 3 + r() * 6, c = pick(tones, r());
      wrap(x, y, rr + 2, (X, Y) => { dab(g, X + 1, Y + 1.5, rr, rr * 0.8, 0, '#5d564b', 0.5); dab(g, X, Y, rr, rr * 0.8, r(), c, 1); dab(g, X - rr * 0.3, Y - rr * 0.3, rr * 0.4, rr * 0.3, 0, '#e3dccb', 0.5); });
    }
  },
  // Track ballast: tightly packed blue-grey stones, each lit on top and shadowed underneath.
  ballast(g, r) {
    g.fillStyle = '#5f6875'; g.fillRect(0, 0, SIZE, SIZE);
    const tones = ['#6f7884', '#828c98', '#95a0ab', '#a9b3bc', '#7c7f86', '#8f8a84'];
    for (let i = 0; i < 3800; i++) {
      const x = r() * SIZE, y = r() * SIZE, rr = 2.5 + r() * 5, c = pick(tones, r());
      wrap(x, y, rr + 2, (X, Y) => { dab(g, X + 1, Y + 1.5, rr, rr * 0.75, 0, '#3c434d', 0.55); dab(g, X, Y, rr, rr * 0.75, r(), c, 1); dab(g, X - rr * 0.3, Y - rr * 0.35, rr * 0.45, rr * 0.3, 0, '#dfe5ea', 0.45); });
    }
  },
  // Wood grain (grey, tinted by each part's own colour): plank bands, wavy grain lines, knots.
  wood(g, r) {
    g.fillStyle = '#c8c8c8'; g.fillRect(0, 0, SIZE, SIZE);
    for (let y = 0; y < SIZE;) { const h = 18 + r() * 40, v = 180 + r() * 50 | 0; g.globalAlpha = 0.6; g.fillStyle = `rgb(${v},${v},${v})`; g.fillRect(0, y, SIZE, h); y += h; }
    for (let i = 0; i < 700; i++) {
      const y = r() * SIZE, len = 60 + r() * 220, x = r() * SIZE, dark = r() < 0.6;
      wrap(x, y, len, (X, Y) => stroke(g, X, Y, len, 0.6 + r() * 1.4, (r() - 0.5) * 0.03, (r() - 0.5) * 5, dark ? '#7a7a7a' : '#e8e8e8', 0.35));
    }
    for (let i = 0; i < 10; i++) {
      const x = r() * SIZE, y = r() * SIZE;
      wrap(x, y, 14, (X, Y) => { dab(g, X, Y, 8, 4, 0, '#8a8a8a', 0.5); dab(g, X, Y, 3.5, 2, 0, '#5a5a5a', 0.8); g.globalAlpha = 0.35; g.strokeStyle = '#6a6a6a'; g.lineWidth = 1; g.beginPath(); g.ellipse(X, Y, 13, 6, 0, 0, 6.28); g.stroke(); });
    }
  },
  // Stone (grey, tinted): blotches, chips of light on top, a few dark cracks.
  stone(g, r) {
    const n = fbm(noiseField(r, 3), noiseField(r, 7), noiseField(r, 15));
    g.fillStyle = '#bdbdbd'; g.fillRect(0, 0, SIZE, SIZE);
    const tones = ['#8e8e8e', '#a4a4a4', '#b8b8b8', '#cdcdcd', '#e2e2e2'];
    for (let i = 0; i < 1600; i++) { const x = r() * SIZE, y = r() * SIZE; wrap(x, y, 30, (X, Y) => dab(g, X, Y, 6 + r() * 18, 4 + r() * 10, r() * 3, pick(tones, n(x, y) * 0.85 + r() * 0.15), 0.4)); }
    g.globalAlpha = 0.45; g.strokeStyle = '#6e6e6e'; g.lineWidth = 1.2;
    for (let i = 0; i < 12; i++) { let x = r() * SIZE, y = r() * SIZE; g.beginPath(); g.moveTo(x, y); for (let k = 0; k < 5; k++) { x += (r() - 0.5) * 22; y += r() * 14; g.lineTo(x, y); } g.stroke(); }
  },
  // Bark (grey, tinted): long vertical strokes, darker furrows, a few lighter ridges catching the light.
  bark(g, r) {
    g.fillStyle = '#a8a8a8'; g.fillRect(0, 0, SIZE, SIZE);
    for (let i = 0; i < 900; i++) {
      const x = r() * SIZE, y = r() * SIZE, len = 40 + r() * 120, dark = r() < 0.55;
      wrap(x, y, len, (X, Y) => stroke(g, X, Y, len, 2 + r() * 4, Math.PI / 2 + (r() - 0.5) * 0.12, (r() - 0.5) * 10, dark ? '#5e5e5e' : '#d4d4d4', dark ? 0.45 : 0.35));
    }
    for (let i = 0; i < 40; i++) { const x = r() * SIZE, y = r() * SIZE; wrap(x, y, 16, (X, Y) => dab(g, X, Y, 6 + r() * 10, 3 + r() * 4, 0, r() < 0.5 ? '#7c8f6a' : '#4c4c4c', 0.35)); }
  },
  // Plaster walls (grey, tinted): soft cloudy patches, rain stains running down from the top, a few chips.
  plaster(g, r) {
    const n = fbm(noiseField(r, 3), noiseField(r, 6), noiseField(r, 13));
    g.fillStyle = '#dedede'; g.fillRect(0, 0, SIZE, SIZE);
    const tones = ['#c8c8c8', '#d2d2d2', '#dcdcdc', '#e6e6e6', '#f0f0f0'];
    for (let i = 0; i < 1800; i++) { const x = r() * SIZE, y = r() * SIZE, len = 16 + r() * 34; wrap(x, y, len, (X, Y) => stroke(g, X, Y, len, 4 + r() * 6, (r() - 0.5) * 0.5, (r() - 0.5) * 8, pick(tones, n(x, y) * 0.85 + r() * 0.15), 0.3)); }
    for (let i = 0; i < 40; i++) {                                             // rain streaks (texture v runs down the wall)
      const x = r() * SIZE, y = r() * SIZE, len = 40 + r() * 120;
      wrap(x, y, len, (X, Y) => stroke(g, X, Y, len, 2 + r() * 4, Math.PI / 2 + (r() - 0.5) * 0.05, (r() - 0.5) * 3, '#a8a8a8', 0.08));
    }
    for (let i = 0; i < 18; i++) { const x = r() * SIZE, y = r() * SIZE; wrap(x, y, 8, (X, Y) => { dab(g, X, Y, 3 + r() * 4, 2 + r() * 3, r() * 3, '#bcbcbc', 0.35); dab(g, X - 1, Y - 1, 2, 1.5, 0, '#f8f8f8', 0.5); }); }
  },
  // Roof tiles (grey, tinted): each tile lighter at its lower lip, streaks of weather, rust and a little moss.
  roof(g, r) {
    g.fillStyle = '#bcbcbc'; g.fillRect(0, 0, SIZE, SIZE);
    const rows = 10, cols = 8, h = SIZE / rows, w = SIZE / cols;
    for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
      const x = i * w + (j % 2) * w / 2, y = j * h, v = 150 + r() * 70 | 0;
      wrap(x + w / 2, y + h / 2, w, (X, Y) => {
        const gr = g.createLinearGradient(0, Y - h / 2, 0, Y + h / 2); gr.addColorStop(0, `rgb(${v - 30},${v - 30},${v - 30})`); gr.addColorStop(0.75, `rgb(${v},${v},${v})`); gr.addColorStop(1, `rgb(${v + 30},${v + 30},${v + 30})`);
        g.globalAlpha = 1; g.fillStyle = gr; g.fillRect(X - w / 2 + 1, Y - h / 2 + 1, w - 2, h - 2);
        g.globalAlpha = 0.5; g.fillStyle = '#5a5a5a'; g.fillRect(X - w / 2, Y + h / 2 - 2, w, 2);
      });
    }
    for (let i = 0; i < 70; i++) { const x = r() * SIZE, y = r() * SIZE, len = 20 + r() * 80; wrap(x, y, len, (X, Y) => stroke(g, X, Y, len, 2 + r() * 3, Math.PI / 2, (r() - 0.5) * 2, r() < 0.5 ? '#7a6a5a' : '#e8e8e8', 0.2)); }
    for (let i = 0; i < 26; i++) { const x = r() * SIZE, y = r() * SIZE; wrap(x, y, 12, (X, Y) => dab(g, X, Y, 4 + r() * 8, 3 + r() * 5, r() * 3, r() < 0.6 ? '#a07a52' : '#8aa860', 0.45)); }
  },
  // Painted timber, white or coloured (grey, tinted): vertical brush marks, worn edges where the wood shows through.
  paint(g, r) {
    g.fillStyle = '#e2e2e2'; g.fillRect(0, 0, SIZE, SIZE);
    for (let i = 0; i < 1500; i++) { const x = r() * SIZE, y = r() * SIZE, len = 30 + r() * 60; wrap(x, y, len, (X, Y) => stroke(g, X, Y, len, 1.5 + r() * 3, Math.PI / 2 + (r() - 0.5) * 0.06, (r() - 0.5) * 2, r() < 0.5 ? '#cfcfcf' : '#f2f2f2', 0.4)); }
    for (let i = 0; i < 30; i++) { const x = r() * SIZE, y = r() * SIZE; wrap(x, y, 14, (X, Y) => dab(g, X, Y, 3 + r() * 9, 1.5 + r() * 3, r() * 3, '#8c7a66', 0.55)); }
  },
  // Platform seats: stylised painted wood. Soft brown bands, long flowing grain lines in light tan with a thin dark line
  // beside each, a few "cathedral" arches where the grain bends, little dark pores. The vertices multiply this: light
  // worn edges, a touch darker in the shallow grooves (the body is a little under white, so the colours here are a little brighter).
  seatwood(g, r) {
    const up = (h) => { const n = parseInt(h.slice(1), 16), f = (v) => Math.min(255, Math.round(v * 1.12)); return `rgb(${f(n >> 16)},${f((n >> 8) & 255)},${f(n & 255)})`; };
    const tones = ['#6f4430', '#7a4a34', '#845238', '#8d593d'].map(up);
    g.fillStyle = up('#7d4c34'); g.fillRect(0, 0, SIZE, SIZE);
    for (let y = 0; y < SIZE;) { const h = 14 + r() * 40; g.globalAlpha = 0.45; g.fillStyle = pick(tones, r()); g.fillRect(0, y, SIZE, h); y += h; }
    for (let i = 0; i < 60; i++) { const x = r() * SIZE, y = r() * SIZE; wrap(x, y, 120, (X, Y) => dab(g, X, Y, 60 + r() * 80, 6 + r() * 10, 0, pick(tones, r()), 0.35)); }
    for (let i = 0; i < 22; i++) {                                               // the grain: long tapered light streaks that
      const x = r() * SIZE, y = r() * SIZE, len = 140 + r() * 260, bend = (r() - 0.5) * 14, a = (r() - 0.5) * 0.05;   // flow gently,
      wrap(x, y, len, (X, Y) => {                                                // each with a thin dark line just below it
        stroke(g, X, Y + 2.2, len * 0.9, 0.8, a, bend, up('#4f2a1e'), 0.5);
        stroke(g, X, Y, len, 1.4 + r() * 2.2, a, bend, up('#c99468'), 0.7);
      });
    }
    for (let i = 0; i < 25; i++) {                                               // broad soft highlights along the grain
      const x = r() * SIZE, y = r() * SIZE, len = 120 + r() * 200;
      wrap(x, y, len, (X, Y) => stroke(g, X, Y, len, 5 + r() * 6, (r() - 0.5) * 0.04, (r() - 0.5) * 10, up('#a06c4a'), 0.35));
    }
    for (let i = 0; i < 2; i++) {                                                // a soft arch where the grain bends
      const x0 = r() * SIZE, yc = r() * SIZE, len = 150 + r() * 120;
      for (let j = 1; j <= 2; j++) {
        const w = j * (7 + r() * 3);
        wrap(x0 + len / 2, yc, len, (X, Y) => {
          const xs = X - len / 2; g.globalAlpha = 0.5; g.strokeStyle = up('#d39c66'); g.lineWidth = 1.4; g.beginPath();
          for (let t = 0; t <= 1.0001; t += 0.05) { const x = xs + t * len, y = Y - w * Math.sqrt(t); t ? g.lineTo(x, y) : g.moveTo(x, y); }
          for (let t = 1; t >= -0.0001; t -= 0.05) g.lineTo(xs + t * len, Y + w * Math.sqrt(t));
          g.stroke();
        });
      }
    }
    for (let i = 0; i < 140; i++) { const x = r() * SIZE, y = r() * SIZE; wrap(x, y, 8, (X, Y) => stroke(g, X, Y, 4 + r() * 6, 0.6, 0, 0, up('#5a3022'), 0.35)); }
  },
  // The seats' iron frame: dark blue-grey paint laid on in short strokes, a cool sheen, chips and a little rust.
  seatiron(g, r) {
    const n = fbm(noiseField(r, 2), noiseField(r, 5), noiseField(r, 11));
    const tones = ['#2a2d37', '#323642', '#3b404d', '#454b59'];
    g.fillStyle = '#343844'; g.fillRect(0, 0, SIZE, SIZE);
    for (let i = 0; i < 700; i++) { const x = r() * SIZE, y = r() * SIZE, len = 40 + r() * 90; wrap(x, y, len, (X, Y) => stroke(g, X, Y, len, 4 + r() * 6, (r() < 0.5 ? 0 : Math.PI / 2) + (r() - 0.5) * 0.1, (r() - 0.5) * 6, pick(tones, n(x, y) * 0.85 + r() * 0.15), 0.35)); }
    for (let i = 0; i < 40; i++) { const x = r() * SIZE, y = r() * SIZE, len = 30 + r() * 60; wrap(x, y, len, (X, Y) => stroke(g, X, Y, len, 2 + r() * 2, (r() - 0.5) * 0.1, 0, '#6a7790', 0.25)); }
    for (let i = 0; i < 14; i++) { const x = r() * SIZE, y = r() * SIZE; wrap(x, y, 14, (X, Y) => dab(g, X, Y, 4 + r() * 6, 2 + r() * 3, r() * 3, '#8a5236', 0.35)); }
  },
};
// How each kind is applied: `replace` uses the painted colours as they are; `tint` multiplies them with the part's own colour.
const KINDS = { grass: { scale: 1 / 3.2, mode: 'replace' }, sand: { scale: 1 / 4, mode: 'replace' }, concrete: { scale: 1 / 4, mode: 'replace' },
  gravel: { scale: 1 / 2, mode: 'replace' }, ballast: { scale: 1 / 1.6, mode: 'replace' }, wood: { scale: 1 / 2.2, mode: 'tint' }, stone: { scale: 1 / 2.5, mode: 'tint' },
  bark: { scale: 1 / 1.6, mode: 'tint' }, plaster: { scale: 1 / 3, mode: 'tint' }, roof: { scale: 1 / 2.4, mode: 'tint' }, paint: { scale: 1 / 1.6, mode: 'tint' },
  seatwood: { scale: 1 / 0.7, mode: 'replace' }, seatiron: { scale: 1 / 1.6, mode: 'replace' } };

const textures = {};
export function paintedTexture(kind) {
  if (textures[kind]) return textures[kind];
  const c = document.createElement('canvas'); c.width = c.height = SIZE;
  const g = c.getContext('2d'); PAINTERS[kind](g, rng(kind.length * 977 + 13)); g.globalAlpha = 1;
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  return (textures[kind] = t);
}

// Which Blender colours are which surface (the hex in the material name). Unlisted colours keep their flat paint.
export const SURFACES = {
  '8c97a3': 'ballast', '7a8490': 'stone', '6a7380': 'stone', '96a0aa': 'stone',
  '7db85a': 'grass', 'e6d6a8': 'sand', d2cbbc: 'concrete', a39c8f: 'concrete', c9bfa8: 'gravel', '8f877d': 'gravel',
  '9a6a45': 'wood', c9a374: 'wood', '8a5a3c': 'wood', '4a3226': 'wood', '4e3528': 'wood', b9b2a8: 'stone',
  '5a3f30': 'bark', f0e4c8: 'plaster', '41626f': 'roof', '2f4b58': 'roof', '5e8f7a': 'roof', '45725f': 'roof', f1e6cc: 'paint', e8f0f4: 'paint', b8403a: 'paint', f0e2c0: 'paint',
  a0623a: 'seatwood', '2f3036': 'seatiron',
};
export function surfaceOf(material) { const m = /^c_([0-9a-f]{6})/.exec(material.name || ''); return m ? SURFACES[m[1]] : null; }

/** Patch a material's shader so it shows the painted texture of `kind`, projected in world space. */
export function painted(material, kind, extra) {
  const { scale, mode } = KINDS[kind], tex = paintedTexture(kind);
  material.onBeforeCompile = (sh) => {
    sh.uniforms.uPaint = { value: tex };
    sh.vertexShader = 'varying vec3 vPW;\nvarying vec3 vPN;\n' + sh.vertexShader.replace('#include <project_vertex>', `#include <project_vertex>
      vec4 pw = vec4(transformed, 1.0); vec3 pn = objectNormal;
      #ifdef USE_INSTANCING
        pw = instanceMatrix * pw; pn = mat3(instanceMatrix) * pn;
      #endif
      vPW = (modelMatrix * pw).xyz; vPN = normalize(mat3(modelMatrix) * pn);`);
    sh.fragmentShader = 'uniform sampler2D uPaint;\nvarying vec3 vPW;\nvarying vec3 vPN;\n' + sh.fragmentShader.replace('#include <map_fragment>', `#include <map_fragment>
      vec3 bw = pow(abs(normalize(vPN)), vec3(6.0)); bw /= (bw.x + bw.y + bw.z);
      vec3 p = vPW * ${scale.toFixed(4)};
      vec3 paint = texture2D(uPaint, p.zy).rgb * bw.x + texture2D(uPaint, p.xz).rgb * bw.y + texture2D(uPaint, p.xy).rgb * bw.z;
      diffuseColor.rgb = ${mode === 'tint' ? 'diffuseColor.rgb * paint * 1.28' : 'paint'};`);
    if (extra) extra(sh);
  };
  material.customProgramCacheKey = () => 'paint-' + kind + (extra ? '+' : '');
  return material;
}
