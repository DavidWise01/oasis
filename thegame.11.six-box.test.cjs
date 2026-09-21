/* Run: node --test thegame.11.six-box.test.cjs */
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const E = require('./thegame.11.six-box.engine.js');

function changeTo(state, id, target) {
  let token = state.cells.flat().find(t => t?.id === id);
  while (token.value !== target) {
    state = E.apply(state, {type: 'shift', id, delta: Math.sign(target - token.value)});
    token = state.cells.flat().find(t => t?.id === id);
  }
  return state;
}
function focus(state, row) {
  return state.window === row ? state : E.apply(state, {type: 'focus', row});
}
function solveSeed() {
  let state = E.apply(E.initial(), {type: 'shift', id: 'b1-1', delta: 1});
  for (let row = 1; row < 6; row++) {
    const isAB = row % 2 === 1;
    state = E.apply(state, {type: 'shift', id: 'b' + (row + 1) + '-' + (isAB ? 0 : 1), delta: isAB ? 1 : -1});
    state = focus(state, row - row % 2);
    state = E.apply(state, {type: 'ablate', direction: row % 2 ? 'S' : 'N'});
  }
  return state;
}

test('six two-slot boxes preserve the supplied seed and alternating frames', () => {
  const s = E.initial();
  assert.deepEqual(s.cells.map(row => row.map(t => E.letter(t.value)).join('')), ['gh','ab','mn','ab','mn','ab']);
  assert.deepEqual(s.cells.map((_, i) => E.orientation(i)), ['eo','oe','eo','oe','eo','oe']);
  assert.equal(E.count(s), 12);
  assert.equal(new Set(s.cells.flat().map(t => t.id)).size, 12);
  assert.equal(E.status(s), 'playing');
});

test('±1 changes one number and preserves the prior state and event prefix', () => {
  const start = E.initial();
  const up = E.apply(start, {type: 'shift', id: 'b1-1', delta: 1});
  const down = E.apply(up, {type: 'shift', id: 'b1-1', delta: -1});
  assert.equal(start.cells[0][1].value, 8);
  assert.equal(up.cells[0][1].value, 9);
  assert.equal(down.cells[0][1].value, 8);
  assert.equal(down.register.length, 2);
  assert.deepEqual(down.register[0], up.register[0]);
  assert.throws(() => { down.cells[0][1].value = 99; }, TypeError);
});

test('out-of-range values and non-unit steps reject without a register write', () => {
  const s = E.initial(), before = E.save(s);
  assert.throws(() => E.apply(s, {type:'shift', id:'b2-0', delta:-1}), /a=1/);
  assert.throws(() => E.apply(s, {type:'shift', id:'b2-0', delta:2}), /exactly/);
  assert.throws(() => E.apply(s, {type:'ablate', direction:'W'}), /equal numbers/);
  assert.equal(E.save(s), before);
});

test('the X scan visits exactly three groups of four, then returns to the top', () => {
  let s = E.initial();
  const windows = [s.window];
  for (let i = 0; i < 3; i++) { s = E.apply(s, {type:'scan'}); windows.push(s.window); }
  assert.deepEqual(windows, [0, 2, 4, 0]);
  assert.throws(() => E.apply(s, {type:'focus', row:1}), /three four-slot/);
});

test('equal diagonals never count as a cardinal match', () => {
  let s = E.initial();
  for (const [id, value] of [['b1-0',3],['b1-1',4],['b2-0',4],['b2-1',3]]) s = changeTo(s, id, value);
  assert.deepEqual(s.cells.slice(0,2).map(r => r.map(t => t.value)), [[3,4],[4,3]]);
  assert.deepEqual(E.matches(s), []);
  for (const direction of ['N','S','E','W']) assert.throws(() => E.apply(s, {type:'ablate', direction}), /equal numbers/);
});

test('horizontal ablation removes exactly two letters and retains the holes', () => {
  let s = E.apply(E.initial(), {type:'shift', id:'b2-0', delta:1});
  assert.ok(E.matches(s).some(m => m.direction === 'S'));
  s = E.apply(s, {type:'ablate', direction:'S'});
  assert.deepEqual(s.cells[1], [null,null]);
  assert.deepEqual(s.cells[2].map(t => t.value), [13,14]);
  assert.equal(E.count(s), 10);
  assert.equal(s.needsCompression, false);
  assert.throws(() => E.apply(s, {type:'compress'}), /vertical ablation/);
});

test('vertical ablation removes one above and below, then requires stable compression', () => {
  let s = changeTo(E.initial(), 'b2-0', 7);
  const rightIDs = s.cells.map(row => row[1].id);
  s = E.apply(s, {type:'ablate', direction:'W'});
  assert.equal(s.cells[0][0], null);
  assert.equal(s.cells[1][0], null);
  assert.equal(E.status(s), 'compress');
  assert.throws(() => E.apply(s, {type:'shift', id:'b1-1', delta:1}), /Compress/);
  s = E.apply(s, {type:'compress'});
  assert.deepEqual(s.cells.map(r => r[0]?.value ?? null), [13,1,13,1,null,null]);
  assert.deepEqual(s.cells.map(r => r[1].id), rightIDs);
  assert.equal(E.count(s), 10);
  assert.equal(s.window, 0);
  assert.equal(E.status(s), 'playing');
});

test('a legal route reaches gi without a special rename operation', () => {
  const s = solveSeed();
  assert.equal(E.count(s), 2);
  assert.equal(E.remaining(s), 'gi');
  assert.equal(E.status(s), 'solved');
  assert.equal(s.cells[0][0].id, 'b1-0');
  assert.equal(s.cells[0][1].id, 'b1-1');
  assert.equal(s.register.filter(e => e.action.type === 'ablate').length, 5);
  assert.equal(s.register.filter(e => e.action.type === 'shift').length, 6);
  assert.throws(() => E.apply(s, {type:'scan'}), /round has stopped/);
});

test('two surviving letters alone do not claim a gi win', () => {
  let s = E.initial();
  for (let row = 1; row < 6; row++) {
    const isAB = row % 2 === 1;
    s = E.apply(s, {type:'shift', id:'b' + (row+1) + '-' + (isAB ? 0 : 1), delta:isAB ? 1 : -1});
    s = focus(s, row - row % 2);
    s = E.apply(s, {type:'ablate', direction:row % 2 ? 'S' : 'N'});
  }
  assert.equal(E.count(s), 2);
  assert.equal(E.remaining(s), 'gh');
  assert.equal(E.status(s), 'playing');
  s = E.apply(s, {type:'shift', id:'b1-0', delta:1});
  s = focus(s, 0);
  s = E.apply(s, {type:'ablate', direction:'N'});
  assert.equal(E.status(s), 'empty');
});

test('register save and replay restore the same complete board and history', () => {
  const s = solveSeed(), restored = E.restore(E.save(s));
  assert.deepEqual(restored, s);
  assert.equal(E.save(restored), E.save(s));
});

test('a changed event, wrong schema or skipped ordinal fails replay', () => {
  const s = solveSeed();
  const broken = JSON.parse(E.save(s));
  broken.register[0].after = '{}';
  assert.throws(() => E.restore(JSON.stringify(broken)), /mismatch at move 1/);
  broken.register[0].after = s.register[0].after;
  broken.register[0].seq = 20;
  assert.throws(() => E.restore(JSON.stringify(broken)), /mismatch at move 1/);
  assert.throws(() => E.restore('{"version":"wrong","register":[]}'), /supported/);
});

test('new round appends a restart and keeps the complete previous register', () => {
  const solved = solveSeed(), fresh = E.apply(solved, {type:'restart'});
  assert.equal(fresh.register.length, solved.register.length + 1);
  assert.deepEqual(fresh.register.slice(0,-1), solved.register);
  assert.deepEqual(fresh.cells, E.initial().cells);
  assert.deepEqual(E.restore(E.save(fresh)), fresh);
});

test('the delivered page loads this engine and its inline JavaScript parses', () => {
  const html = fs.readFileSync(path.join(__dirname, 'thegame.11.six-box.html'), 'utf8');
  assert.ok(html.includes('src="./thegame.11.six-box.engine.js"'));
  const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
  assert.equal(scripts.length, 1);
  for (const [, source] of scripts) new vm.Script(source);
});

// Optional browser gate: install Playwright + Chromium, then run
// SIX_BOX_BROWSER_CHECK=1 node --test thegame.11.six-box.test.cjs
test('browser: play, reload, export, compress, recover and fit mobile', {
  skip: process.env.SIX_BOX_BROWSER_CHECK === '1' ? false : 'Optional: requires Playwright and Chromium.'
}, async () => {
  const http = require('node:http');
  const {chromium} = require('playwright');
  const server = http.createServer((req, res) => {
    const name = req.url === '/' ? 'thegame.11.six-box.html' : req.url.slice(1);
    if (!['thegame.11.six-box.html','thegame.11.six-box.engine.js'].includes(name)) { res.writeHead(404); res.end(); return; }
    res.setHeader('Content-Type', name.endsWith('.js') ? 'application/javascript' : 'text/html');
    res.end(fs.readFileSync(path.join(__dirname, name)));
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  let browser;
  try {
    browser = await chromium.launch({headless:true});
    const page = await browser.newPage({viewport:{width:1180,height:1000}});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto('http://127.0.0.1:' + server.address().port + '/');
    assert.equal(await page.locator('[data-box]').count(), 6);
    assert.equal(await page.locator('.cell').count(), 12);
    if (process.env.SIX_BOX_SCREENSHOT) await page.screenshot({path:process.env.SIX_BOX_SCREENSHOT,fullPage:true});
    await page.locator('[data-cell="0,1"]').click();
    await page.locator('#plus').click();
    await page.reload();
    assert.equal(await page.locator('[data-cell="0,1"] .letter').textContent(), 'i');
    for (let row = 1; row < 6; row++) {
      const isAB = row % 2 === 1;
      await page.locator('[data-cell="' + row + ',' + (isAB ? 0 : 1) + '"]').click();
      await page.locator(isAB ? '#plus' : '#minus').click();
      const x = page.locator('[data-group="' + (Math.floor(row / 2) + 1) + '"] .x-button');
      if (await x.isEnabled()) await x.click();
      await page.locator('[data-direction="' + (row % 2 ? 'S' : 'N') + '"]').click();
    }
    assert.match(await page.locator('#feedback').textContent(), /gi · distilled/);
    assert.equal(await page.locator('.cell:not(.hole)').count(), 2);
    await page.reload();
    assert.match(await page.locator('#feedback').textContent(), /gi · distilled/);
    const downloading = page.waitForEvent('download');
    await page.locator('#export').click();
    const download = await downloading;
    const chunks = [];
    for await (const chunk of await download.createReadStream()) chunks.push(chunk);
    const exported = Buffer.concat(chunks).toString('utf8');
    assert.equal(E.status(E.restore(exported)), 'solved');
    const priorCount = E.restore(exported).register.length;
    await page.locator('#restart').click();
    assert.equal(await page.locator('#register li').count(), priorCount + 1);
    await page.locator('[data-cell="0,0"]').click();
    for (let i = 0; i < 6; i++) await page.locator('#minus').click();
    await page.locator('[data-direction="W"]').click();
    assert.equal(await page.locator('#plus').isEnabled(), false);
    assert.equal(await page.locator('#scan').isEnabled(), false);
    assert.equal(await page.locator('#compress').isEnabled(), true);
    await page.locator('#compress').click();
    assert.equal(await page.locator('[data-cell="0,0"] .letter').textContent(), 'm');
    assert.equal(await page.locator('.cell:not(.hole)').count(), 10);
    await page.reload();
    assert.equal(await page.locator('[data-cell="0,0"] .letter').textContent(), 'm');
    await page.setViewportSize({width:390,height:844});
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), true);
    if (process.env.SIX_BOX_SCREENSHOT) await page.screenshot({path:process.env.SIX_BOX_SCREENSHOT.replace(/\.png$/, '.mobile.png'),fullPage:true});
    await page.evaluate(() => {
      const key = 'thegame.six-box.11.register';
      const data = JSON.parse(localStorage.getItem(key));
      data.register[0].after = '{}'; localStorage.setItem(key, JSON.stringify(data));
    });
    await page.reload();
    assert.match(await page.locator('#feedback').textContent(), /Saved register could not replay/);
    assert.equal(await page.locator('#plus').isEnabled(), false);
    await page.locator('#storage-recovery').click();
    await page.reload();
    assert.equal(await page.locator('.cell:not(.hole)').count(), 12);
    assert.equal(await page.locator('#plus').isEnabled(), true);
    assert.equal(await page.evaluate(() => JSON.parse(localStorage.getItem('thegame.six-box.11.register')).register[0].after), '{}');
    assert.deepEqual(errors, []);
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
});
