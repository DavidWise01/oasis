
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const f = require('./facts.js');
const root = path.join(__dirname, '..');
function sha(buf){ return crypto.createHash('sha256').update(buf).digest('hex'); }
function lf(buf){ return Buffer.from(Uint8Array.from(buf).filter ? buf.filter(b => b !== 13) : buf); }
const lean = fs.readFileSync(path.join(root, 'lean', 'O3.lean'));
const leanLf = Buffer.from([...lean].filter(b => b !== 13));
if (sha(leanLf) !== f.O3HASH) throw new Error('lean hash');
if (f.factO3().indexOf('20') < 0) throw new Error('o3');
if (f.factReturn().indexOf('refused') < 0) throw new Error('return');
const world = JSON.parse(fs.readFileSync(path.join(root, 'worlds', 'u1-du0', 'world.json'), 'utf8'));
f.factChannels(world.six_channels.map(c => c.name));
const kana = JSON.parse(fs.readFileSync(path.join(root, 'architecture', 'kana', 'kana-layer-map.json'), 'utf8'));
f.factKana(kana.glyph);
const index = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
for (const href of ['o3-twenty.html','the-return.html','six-channels.html','kana-anchors.html']) {
  if (!index.includes(href)) throw new Error('missing '+href);
  const html = fs.readFileSync(path.join(__dirname, href), 'utf8');
  if (html.includes('\r')) throw new Error('cr '+href);
  if (!html.includes('id="v3"')) throw new Error('stage '+href);
}
if (fs.readFileSync(path.join(__dirname, 'facts.js'), 'utf8').includes('\r')) throw new Error('cr facts');
console.log('SPHERES FACTS PASS');
