// Every piece of wording on the site, one record each, for the text editor artifact.
//   node tools/texts.mjs extract <out.json>     write all records (id, group, place, field, kind, file, quote, original)
//   node tools/texts.mjs apply <edits.json>     write edited values back: each record's `original` is replaced, exactly once,
//                                               by its `value` in its file (escaped for the kind of quotes it sits in)
import fs from 'fs';
const R = (f) => fs.readFileSync(f, 'utf8');

async function extract() {
  const out = [];
  const add = (r) => out.push({ ...r, id: r.id.replace(/[^A-Za-z0-9_.~:@+-]/g, '-').slice(0, 190) });
  // the panels: kicker, title, paragraphs, notes still to answer, link labels
  const { CONTENT } = await import('../src/content.js');
  const src = R('src/content.js');
  const where = (k) => (k.match(/^(.*?)\s·/) ? k.match(/^(.*?)\s·/)[1] : k);
  for (const [key, c] of Object.entries(CONTENT)) {
    const group = /^Office|^Archive/.test(c.kicker) ? 'The Office' : /^Home/.test(c.kicker) ? 'Home among the stars' : /^Night market/.test(c.kicker) ? 'The Night Market' : 'The Terminal';
    const place = c.title;
    for (const f of ['kicker', 'title', 'body', 'todo']) {
      if (typeof c[f] !== 'string') continue;
      const quote = src.includes('`' + c[f] + '`') ? '`' : src.includes("'" + c[f] + "'") ? "'" : '"';
      add({ id: `panel.${key}.${f}`, group, place, order: out.length, field: { kicker: 'Small heading', title: 'Title', body: 'Paragraphs', todo: 'Note (still to answer)' }[f], kind: f === 'body' ? 'html' : 'line', file: 'src/content.js', pre: quote, post: quote, original: c[f] });
    }
    (c.links || []).forEach(([label]) => { if (src.split("'" + label + "'").length === 2 && !out.some((x) => x.field === 'Link label' && x.original === label)) add({ id: `panel.${key}.link.${label}`, group, place, order: out.length, field: 'Link label', kind: 'line', file: 'src/content.js', pre: "'", post: "'", original: label }); });
    void where;
  }
  // the prompts that float over things in each world
  for (const w of ['terminal', 'home', 'office', 'market']) {
    const f = `src/worlds/${w}.js`; if (!fs.existsSync(f)) continue;
    const group = { terminal: 'The Terminal', home: 'Home among the stars', office: 'The Office', market: 'The Night Market' }[w];
    for (const m of R(f).matchAll(/w\.hot\([^,]+,[^,]+,\s*'([^']+)',\s*'([^']+)'/g))
      add({ id: `prompt.${w}.${m[2]}.${m[1]}`, group, place: 'Prompts in the world', order: out.length, field: `Prompt (opens “${m[2]}”)`, kind: 'line', file: f, pre: "'", post: "'", original: m[1] });
  }
  // the station sign
  const t = R('src/worlds/terminal.js'), sm = t.match(/sign\(s, \[([^\]]+)\]/);
  if (sm) [...sm[1].matchAll(/'([^']+)'/g)].forEach((m, i) => add({ id: `sign.line${i + 1}`, group: 'The Terminal', place: 'The station sign', order: out.length, field: ['Big name', 'Second line', 'Directions'][i] || `Line ${i + 1}`, kind: 'line', file: 'src/worlds/terminal.js', pre: "'", post: "'", original: m[1] }));
  // the page around the world: intro card, ticket choice, buttons
  const html = R('index.html');
  const pick = (id, field, re, place = 'Around the world') => { const m = html.match(re); if (m) add({ id, group: 'The page', place, order: out.length, field, kind: 'line', file: 'index.html', pre: m[1], post: m[3], original: m[2], all: /^page\.nav\./.test(id) }); };
  pick('page.intro.name', 'Name', /(<h1>)([^<]+)(<\/h1>)/, 'The intro card');
  pick('page.intro.text', 'Introduction', /(<\/h1>\s*<p>)([^<]+)(<\/p>)/, 'The intro card');
  pick('page.intro.start', 'Start button', /(<button id="start">)([^<]+)(<\/button>)/, 'The intro card');
  pick('page.intro.keys', 'Controls (computer)', /(<span class="desk">)([^<]+)(<\/span>)/, 'The intro card');
  pick('page.intro.touch', 'Controls (phone)', /(<span class="touch">)([^<]+)(<\/span>)/, 'The intro card');
  pick('page.ticket.question', 'Question', /(<p>)(The crossing bell[^<]*)(<\/p>)/, 'Choosing a ticket');
  for (const [d, n] of [['home', 1], ['office', 2], ['market', 3]]) {
    pick(`page.ticket.${d}.name`, `Line ${n}: name`, new RegExp(`(data-dest="${d}"><b>[^<]+</b>)([^<]+)(<small>)`), 'Choosing a ticket');
    pick(`page.ticket.${d}.small`, `Line ${n}: small print`, new RegExp(`data-dest="${d}"><b>[^<]+</b>[^<]+(<small>)([^<]+)(</small>)`), 'Choosing a ticket');
  }
  pick('page.ticket.stand', 'Stand-up button', /(<button id="stand"[^>]*>)([^<]+)(<\/button>)/, 'Choosing a ticket');
  for (const d of ['terminal', 'home', 'office', 'market']) pick(`page.nav.${d}`, `Top-right button: ${d}`, new RegExp(`(<button data-go="${d}">)([^<]+)(</button>)`), 'Top-right buttons');
  pick('page.game.text', 'Game instructions', /(<p>)(Squash the bugs[^<]*)(<\/p>)/, 'The arcade game');
  const mm = R('src/main.js').match(/startBtn\.textContent = '([^']+)'/);
  if (mm) add({ id: 'page.loading', group: 'The page', place: 'The intro card', order: out.length, field: 'While it loads', kind: 'line', file: 'src/main.js', pre: "startBtn.textContent = '", post: "'", original: mm[1] });
  return out;
}

function esc(v, r) {
  const q = r.file.endsWith('.html') ? 'html' : r.pre.endsWith('`') ? '`' : r.pre.endsWith("'") ? "'" : '"';
  if (q === 'html') return v.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  return escq(v, q);
}
function escq(v, q) { return q === "'" ? v.replace(/\\/g, '\\\\').replace(/'/g, "\\'") : q === '`' ? v.replace(/\\/g, '\\\\').replace(/`/g, '\\`').replace(/\$\{/g, '\\${') : q === '"' ? v.replace(/"/g, '\\"') : v; }
function apply(edits) {
  const files = {}, done = [], skipped = [];
  for (const r of edits) {
    if (r.value == null || r.value === r.original) continue;
    const f = files[r.file] ??= R(r.file);
    const from = r.pre + esc(r.original, r) + r.post, to = r.pre + esc(r.value, r) + r.post;
    const n = f.split(from).length - 1;
    if (n !== 1 && !(r.all && n > 1)) { skipped.push(`${r.id} (found ${n} times)`); continue; }
    files[r.file] = f.split(from).join(to); done.push(r.id);   // (r.all: the same button in two places)
  }
  for (const [f, s] of Object.entries(files)) fs.writeFileSync(f, s);
  console.log(`applied ${done.length}` + (skipped.length ? `; skipped: ${skipped.join(', ')}` : ''));
}

const [cmd, file] = process.argv.slice(2);
if (cmd === 'extract') { const r = await extract(); fs.writeFileSync(file, JSON.stringify(r, null, 1)); console.log(r.length, 'texts'); }
else if (cmd === 'apply') apply(JSON.parse(R(file)));
else console.log('usage: node tools/texts.mjs extract|apply <file.json>');
