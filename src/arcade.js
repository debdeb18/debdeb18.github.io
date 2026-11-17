// The one arcade machine: Bug Squash.
const el = document.getElementById('arcade'), cv = document.getElementById('game'), score = document.getElementById('score');
const g = cv.getContext('2d');
let bugs, pts, left, raf, last, over, onClose;

function spawn() { bugs.push({ x: 20 + Math.random() * 320, y: -10, v: 40 + Math.random() * 60 + pts * 2, w: Math.random() * 6 }); }
function frame(now) {
  const dt = Math.min(0.05, (now - last) / 1000); last = now;
  g.fillStyle = '#10131f'; g.fillRect(0, 0, 360, 270);
  g.fillStyle = '#ff5fa2'; g.fillRect(0, 262, 360, 8);
  g.font = '11px monospace'; g.fillStyle = '#ff9cc4'; g.textAlign = 'center'; g.fillText('PRODUCTION', 180, 258);
  if (!over) {
    left -= dt;
    if (Math.random() < dt * (1.6 + pts * 0.05)) spawn();
    for (const b of bugs) { b.y += b.v * dt; b.x += Math.sin(now / 200 + b.w) * 30 * dt; }
    const n = bugs.length; bugs = bugs.filter((b) => b.y < 262);
    left -= (n - bugs.length) * 1.5; // a bug in prod costs time
    if (left <= 0) { left = 0; over = true; }
  }
  g.font = '22px serif';
  for (const b of bugs) g.fillText('🐛', b.x, b.y);
  score.textContent = `${pts} squashed · ${Math.ceil(left)}s`;
  if (over) {
    g.fillStyle = 'rgba(16,19,31,.8)'; g.fillRect(0, 0, 360, 270);
    g.fillStyle = '#7fffd0'; g.font = 'bold 26px monospace'; g.fillText(`${pts} bugs squashed`, 180, 120);
    g.font = '14px monospace'; g.fillStyle = '#fff'; g.fillText('click to play again', 180, 155);
  }
  raf = requestAnimationFrame(frame);
}
function reset() { bugs = []; pts = 0; left = 20; over = false; }
cv.addEventListener('pointerdown', (e) => {
  if (over) return reset();
  const r = cv.getBoundingClientRect(), x = (e.clientX - r.left) * 360 / r.width, y = (e.clientY - r.top) * 270 / r.height;
  const i = bugs.findIndex((b) => Math.abs(b.x - x) < 22 && Math.abs(b.y - 8 - y) < 22);
  if (i >= 0) { bugs.splice(i, 1); pts++; }
});
export function closeArcade() { if (el.hidden) return; el.hidden = true; cancelAnimationFrame(raf); onClose && onClose(); }
export function openArcade(cb) { onClose = cb; el.hidden = false; reset(); last = performance.now(); raf = requestAnimationFrame(frame); }
document.getElementById('aclose').addEventListener('click', closeArcade);
