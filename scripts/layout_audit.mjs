#!/usr/bin/env node
// Layout gate: opens film/index.html in headless Chrome, seeks the GSAP
// timeline every 0.1 s, and measures where things actually sit.
//
// Neither film_audit.py (code) nor frame_audit.py (pixels) can see placement:
// a headline hidden under a card, a logo sitting on a word, a card hanging off
// the frame edge all pass both. This one fails them.
//
//   text hidden     text covered by a later-painted opaque box / image
//   text collision  two pieces of text overlapping each other
//   text clipped    text cut by the frame edge
//   safe area       text inside the outer 48 px margin
//   parked off-edge a card / image holding still while partly off-frame
//                   (a deliberate bleed: put data-bleed on it and give it >= 25% off-frame)
//
// Each problem must last >= 0.3 s to count (passing motion is allowed).
//
// usage: node layout_audit.mjs <project>/film/index.html [--step 0.1] [--shots dir]
// needs: puppeteer-core (npm i puppeteer-core) and Chrome; set CHROME_PATH
//        if Chrome is not in the usual place.
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
import os from 'os';
import { pathToFileURL } from 'url';

const args = process.argv.slice(2);
const file = args.find(a => !a.startsWith('--'));
if (!file) { console.error('usage: layout_audit.mjs film/index.html [--step 0.1] [--shots dir]'); process.exit(2); }
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const STEP = parseFloat(opt('--step', '0.1'));
const SHOTS = opt('--shots', null);
const MIN_RUN = 0.3, SAFE = 48, W = 1920, H = 1080;

function loadPuppeteer() {
  const tries = [process.cwd(), path.dirname(path.resolve(file)), path.dirname(new URL(import.meta.url).pathname)];
  for (const base of tries) {
    try { return createRequire(path.join(base, 'x.js'))('puppeteer-core'); } catch {}
  }
  // npx cache (hyperframes pulls puppeteer-core in)
  const npx = path.join(os.homedir(), '.npm', '_npx');
  if (fs.existsSync(npx)) for (const d of fs.readdirSync(npx)) {
    const p = path.join(npx, d, 'node_modules', 'puppeteer-core');
    if (fs.existsSync(p)) { try { return createRequire(path.join(npx, d, 'x.js'))('puppeteer-core'); } catch {} }
  }
  console.error('puppeteer-core not found: run `npm i puppeteer-core` in the project folder'); process.exit(2);
}
function chromePath() {
  const c = [process.env.CHROME_PATH,
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'].filter(Boolean);
  const hit = c.find(p => fs.existsSync(p));
  if (!hit) { console.error('Chrome not found: set CHROME_PATH'); process.exit(2); }
  return hit;
}

const puppeteer = loadPuppeteer().default || loadPuppeteer();
const browser = await puppeteer.launch({ executablePath: chromePath(), headless: true,
  args: ['--allow-file-access-from-files', '--disable-web-security'] });
const page = await browser.newPage();
await page.setViewport({ width: W, height: H, deviceScaleFactor: 1 });
await page.goto(pathToFileURL(path.resolve(file)).href, { waitUntil: 'networkidle0', timeout: 60000 });
await page.evaluate(() => document.fonts && document.fonts.ready);
const dur = await page.evaluate(() => {
  const r = document.querySelector('[data-composition-id]');
  const tls = Object.values(window.__timelines || {});
  if (!tls.length) return -1;
  return parseFloat(r && r.dataset.duration) || Math.max(...tls.map(t => t.duration()));
});
if (dur < 0) { console.error('no window.__timelines found'); process.exit(2); }

// in-page probe -------------------------------------------------------------
const probe = ({ SAFE, W, H }) => {
  const label = el => el.id ? '#' + el.id
    : (el.className && typeof el.className === 'string' ? el.tagName.toLowerCase() + '.' + el.className.trim().split(/\s+/)[0] : el.tagName.toLowerCase());
  const nameOf = el => { // nearest ancestor with an id gives a readable path
    let n = el, parts = [];
    while (n && n.nodeType === 1 && parts.length < 3) { parts.unshift(label(n)); if (n.id) break; n = n.parentElement; }
    return parts.join(' ');
  };
  const effOpacity = el => { let o = 1; for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
    const cs = getComputedStyle(n); if (cs.display === 'none' || cs.visibility === 'hidden') return 0; o *= parseFloat(cs.opacity); } return o; };
  const alpha = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return c === 'transparent' ? 0 : 1; const p = m[1].split(/[ ,/]+/).filter(Boolean); return p.length > 3 ? parseFloat(p[3]) : 1; };
  const all = [...document.querySelectorAll('body *')];
  // make everything hit-testable so stacking can be read
  if (!document.getElementById('__la')) { const s = document.createElement('style'); s.id = '__la'; s.textContent = '*{pointer-events:auto !important}'; document.head.appendChild(s); }

  const isSolid = el => {
    if (effOpacity(el) < 0.6) return false;
    const cs = getComputedStyle(el);
    if (cs.mixBlendMode !== 'normal') return false;
    const r = el.getBoundingClientRect();
    if (r.width * r.height < 1500 || r.width * r.height > W * H * 0.8) return false;
    if (el.tagName === 'IMG' || el.tagName === 'svg' || el.tagName === 'CANVAS' || el.tagName === 'VIDEO') return true;
    return alpha(cs.backgroundColor) > 0.8 || (cs.backgroundImage !== 'none' && !cs.backgroundImage.includes('radial-gradient'));
  };

  // a closing lid / flipping card hiding its own face is the shot, not a mistake
  const rig = el => { for (let n = el.parentElement; n; n = n.parentElement) if (getComputedStyle(n).transformStyle === 'preserve-3d') return n; return null; };
  const same3d = (a, b) => { const r = rig(b); return !!r && r.contains(a); };

  const texts = [];
  for (const el of all) {
    if (['SCRIPT', 'STYLE'].includes(el.tagName)) continue;
    const tn = [...el.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim());
    if (!tn.length) continue;
    const op = effOpacity(el); if (op < 0.35) continue;           // ghost type is decoration
    const cs = getComputedStyle(el); if (alpha(cs.color) < 0.35) continue;
    if (parseFloat(cs.fontSize) * 1 < 9) continue;
    const range = document.createRange(); let box = null;
    for (const n of tn) { range.selectNodeContents(n); for (const r of range.getClientRects()) {
      if (r.width < 2 || r.height < 2) continue;
      box = box ? { l: Math.min(box.l, r.left), t: Math.min(box.t, r.top), r: Math.max(box.r, r.right), b: Math.max(box.b, r.bottom) }
                : { l: r.left, t: r.top, r: r.right, b: r.bottom }; } }
    if (!box) continue;
    texts.push({ el, box, text: tn.map(n => n.textContent.trim()).join('').slice(0, 18) });
  }

  const out = [];
  const inter = (a, b) => Math.max(0, Math.min(a.r, b.r) - Math.max(a.l, b.l)) * Math.max(0, Math.min(a.b, b.b) - Math.max(a.t, b.t));
  const vis = [];
  for (const T of texts) {
    const { box } = T, w = box.r - box.l, h = box.b - box.t;
    const onArea = inter(box, { l: 0, t: 0, r: W, b: H });
    if (onArea <= 0) continue;                                    // fully off-frame: camera elsewhere
    // hit-test a grid inside the glyph box
    let seen = 0, hidden = 0, by = null;
    for (let i = 0; i < 6; i++) for (let j = 0; j < 3; j++) {
      const x = box.l + w * (i + 0.5) / 6, y = box.t + h * (j + 0.5) / 3;
      if (x < 0 || y < 0 || x >= W || y >= H) continue;
      const stack = document.elementsFromPoint(x, y);
      const k = stack.findIndex(e => e === T.el || T.el.contains(e));
      if (k < 0) continue;                                        // clipped by a parent: not visible here
      seen++;
      const cover = stack.slice(0, k).find(e => !e.contains(T.el) && !T.el.contains(e) && isSolid(e) && !same3d(e, T.el));
      if (cover) { hidden++; by = by || cover; }
    }
    if (!seen) continue;
    vis.push(T);
    const name = nameOf(T.el) + ' "' + T.text + '"';
    if (hidden / seen >= 0.2) out.push({ kind: 'text hidden', key: name, detail: 'under ' + nameOf(by) });
    if (onArea < w * h * 0.97) out.push({ kind: 'text clipped', key: name, detail: 'cut by frame edge, holding still', rect: [box.l, box.t, w, h].map(Math.round) });
    else if (box.l < SAFE || box.t < SAFE || box.r > W - SAFE || box.b > H - SAFE)
      out.push({ kind: 'safe area', key: name, detail: `inside ${SAFE}px margin` });
  }
  for (let a = 0; a < vis.length; a++) for (let b = a + 1; b < vis.length; b++) {
    const A = vis[a], B = vis[b];
    if (A.el.contains(B.el) || B.el.contains(A.el)) continue;
    // letters of one split line flying together are one word animating
    if (A.el.parentElement === B.el.parentElement && A.text.length <= 2 && B.text.length <= 2) continue;
    const small = Math.min((A.box.r - A.box.l) * (A.box.b - A.box.t), (B.box.r - B.box.l) * (B.box.b - B.box.t));
    if (inter(A.box, B.box) > small * 0.12)
      out.push({ kind: 'text collision', key: nameOf(A.el) + ' "' + A.text + '" x ' + nameOf(B.el) + ' "' + B.text + '"', detail: '' });
  }
  // solid blocks partly off-frame (checked for stillness outside)
  const blocks = [];
  for (const el of all) {
    if (!isSolid(el)) continue;
    const r = el.getBoundingClientRect(), area = r.width * r.height;
    if (area < 20000) continue;
    const on = inter({ l: r.left, t: r.top, r: r.right, b: r.bottom }, { l: 0, t: 0, r: W, b: H });
    // declared bleed (data-bleed) may hang off by >= 25%; anything shy of that reads as a mistake
    const hi = el.closest('[data-bleed]') ? 0.75 : 0.95;
    if (on > area * 0.3 && on < area * hi) blocks.push({ key: nameOf(el), rect: [r.left, r.top, r.width, r.height].map(Math.round) });
    else if (hi < 0.95 && on >= area * 0.75 && on < area * 0.95)
      blocks.push({ key: nameOf(el) + ' (data-bleed but only ' + Math.round(100 - on / area * 100) + '% off — commit or pull it in)', rect: [r.left, r.top, r.width, r.height].map(Math.round) });
  }
  return { out, blocks };
};

// sample ---------------------------------------------------------------------
const runs = new Map();   // key -> { kind, detail, times: [] }
const lastBlocks = new Map();
const add = (kind, key, detail, t) => {
  const k = kind + '|' + key; if (!runs.has(k)) runs.set(k, { kind, key, detail, times: [] });
  runs.get(k).times.push(t);
};
for (let t = 0; t <= dur - 0.05; t = Math.round((t + STEP) * 1000) / 1000) {
  await page.evaluate(t => { for (const tl of Object.values(window.__timelines)) tl.seek(t, false); }, t);
  const { out, blocks } = await page.evaluate(probe, { SAFE, W, H });
  const seenNow = new Set();
  for (const o of out) {
    if (o.rect) {          // clipped text only counts once it stops moving (entering / exiting is fine)
      const k = 'clip|' + o.key, prev = lastBlocks.get(k); lastBlocks.set(k, o.rect); seenNow.add(k);
      if (!(prev && prev.every((v, i) => Math.abs(v - o.rect[i]) < 3))) continue;
    }
    add(o.kind, o.key, o.detail, t);
  }
  for (const b of blocks) {
    seenNow.add(b.key);
    const prev = lastBlocks.get(b.key);
    if (prev && prev.every((v, i) => Math.abs(v - b.rect[i]) < 3)) add('parked off-edge', b.key, 'holding still, partly off-frame', t);
    lastBlocks.set(b.key, b.rect);
  }
  for (const k of [...lastBlocks.keys()]) if (!seenNow.has(k)) lastBlocks.delete(k);
}

// longest continuous run per problem
const problems = [];
for (const r of runs.values()) {
  let best = [0, 0], s = r.times[0], p = r.times[0];
  for (const t of r.times.slice(1).concat([Infinity])) {
    if (t - p > STEP * 1.5) { if (p - s + STEP > best[1] - best[0]) best = [s, p + STEP]; s = t; }
    p = t;
  }
  const len = best[1] - best[0];
  if (len >= MIN_RUN - 1e-6) problems.push({ ...r, from: best[0], to: best[1], len });
}
problems.sort((a, b) => a.from - b.from);

if (SHOTS && problems.length) {
  fs.mkdirSync(SHOTS, { recursive: true });
  for (const [i, p] of problems.slice(0, 12).entries()) {
    const t = (p.from + p.to) / 2;
    await page.evaluate(t => { for (const tl of Object.values(window.__timelines)) tl.seek(t, false); }, t);
    await page.screenshot({ path: path.join(SHOTS, `layout-${String(i + 1).padStart(2, '0')}-${t.toFixed(1)}s.png`) });
  }
}
await browser.close();

const kinds = ['text hidden', 'text collision', 'text clipped', 'safe area', 'parked off-edge'];
console.log(`layout audit  ${path.resolve(file)}  (${dur}s, every ${STEP}s, problems lasting >= ${MIN_RUN}s)\n`);
for (const k of kinds) {
  const ps = problems.filter(p => p.kind === k);
  console.log(`  ${ps.length ? 'FAIL' : 'PASS'}  ${k.padEnd(18)} ${ps.length}`);
  for (const p of ps.slice(0, 8)) console.log(`        ${p.from.toFixed(1)}-${p.to.toFixed(1)}s  ${p.key}${p.detail ? '  — ' + p.detail : ''}`);
  if (ps.length > 8) console.log(`        … ${ps.length - 8} more`);
}
const failed = kinds.filter(k => problems.some(p => p.kind === k));
const gate = path.join(path.dirname(path.dirname(path.resolve(file))), '.gates');
const stamp = path.join(gate, 'layout_audit.ok');
if (failed.length) {
  if (fs.existsSync(stamp)) fs.unlinkSync(stamp);
  console.log(`\n  ${failed.length} failed: ${failed.join(', ')}`);
  console.log('  fix the placement (references/layout.md), re-run until 0 failed');
  process.exit(1);
} else {
  fs.mkdirSync(gate, { recursive: true }); fs.writeFileSync(stamp, new Date().toISOString().slice(0, 10) + '\n');
  console.log('\n  0 failed — layout clear');
}
