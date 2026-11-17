// Smoke test: serve the site, open it in a real browser, and make sure every world loads without errors.
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');

const root = path.resolve(__dirname, '..');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.glb': 'model/gltf-binary', '.png': 'image/png', '.jpeg': 'image/jpeg', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml' };
const server = http.createServer((req, res) => {
  const file = path.join(root, decodeURIComponent(req.url.split('?')[0]).replace(/\/$/, '/index.html'));
  if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end('not found'); }
  res.writeHead(200, { 'Content-Type': types[path.extname(file)] || 'application/octet-stream' }); fs.createReadStream(file).pipe(res);
});

const failures = [];
const check = (ok, what) => { console.log((ok ? 'ok   ' : 'FAIL ') + what); if (!ok) failures.push(what); };

(async () => {
  // 1. every model the layout asks for exists on disk
  const layoutFile = path.join(root, 'models/terminal/layout.json');
  if (fs.existsSync(layoutFile)) {
    const layout = JSON.parse(fs.readFileSync(layoutFile, 'utf8'));
    const missing = [...new Set(layout.pieces.filter((p) => p.model).map((p) => p.name))].filter((n) => !fs.existsSync(path.join(root, 'models/terminal', n + '.glb')));
    check(missing.length === 0, 'every piece in the terminal layout has a model' + (missing.length ? ' (missing: ' + missing.join(', ') + ')' : ''));
  }

  // 2. the site runs in a browser
  await new Promise((r) => server.listen(0, r));
  const url = 'http://localhost:' + server.address().port + '/';
  const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1000, height: 640 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push('page error: ' + e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push('console error: ' + m.text()); });
  page.on('response', (r) => { if (r.status() >= 400) errors.push(r.status() + ' ' + r.url()); });

  await page.goto(url);
  await page.waitForFunction(() => window.portfolio && window.portfolio.worlds, null, { timeout: 60000 }).catch(() => {});
  check(await page.evaluate(() => !!(window.portfolio && window.portfolio.worlds)), 'the world starts');
  check(await page.isVisible('#intro'), 'the intro card shows');
  await page.click('#start', { timeout: 180000 });                  // the button waits for the station models to arrive
  for (const world of ['home', 'office', 'market', 'terminal']) {
    await page.evaluate((w) => window.portfolio.go(w), world);
    const want = world === 'terminal' ? '' : '#' + world;
    await page.waitForFunction((h) => location.hash === h, want, { timeout: 30000 }).catch(() => {});
    check(await page.evaluate((h) => location.hash === h, want), 'can travel to ' + world);
  }
  const hots = await page.evaluate(() => Object.values(window.portfolio.worlds).reduce((n, w) => n + w.hots.length, 0));
  check(await page.evaluate(() => portfolio.worlds.terminal.loaded === true), 'the station models load');
  check(hots > 20, 'there are things to interact with (' + hots + ')');
  check(errors.length === 0, 'no errors or missing files' + (errors.length ? '\n     ' + errors.join('\n     ') : ''));

  await browser.close(); server.close();
  if (failures.length) { console.error('\n' + failures.length + ' check(s) failed'); process.exit(1); }
  console.log('\nall checks passed');
})().catch((e) => { console.error(e); process.exit(1); });
