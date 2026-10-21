(function (root) {
  const O3HASH = "9ed23de7504fc284af95d4c39209a754d40886c0909d7d15c9121ff683e4d282";
  const CHANNELS = ["MYTH", "OBSERVED", "AUTHORITY", "SACRED / INTERPRETED", "MODEL / WORKING SCIENCE", "HIDDEN PROVENANCE"];
  const GLYPH = "+ k < | A | /\\ | N | /\\/ | A | /\\ | >-K";
  function witness(bytes) {
    let x = 2166136261;
    for (const b of bytes) x = Math.imul(x ^ b, 16777619);
    return x >>> 0;
  }
  function through(payload, capacity) {
    if (payload.length > capacity) throw Error('box');
    const encoded = payload.map(b => (b + 1) & 255);
    return encoded.map(b => (b - 1) & 255);
  }
  function factO3() {
    const parent = 1, outputs = 2, width = 6, verify = 2;
    const nodes = parent + outputs;
    if (nodes !== 3) throw Error('nodes ' + nodes);
    const envelope = nodes * width + verify;
    if (envelope !== 20) throw Error('envelope ' + envelope);
    return '1 parent + 2 outputs = 3; 3 x 6 + 2 = 20';
  }
  function factReturn() {
    const payload = [1, 1, 2, 3, 5, 8];
    const back = through(payload, 8);
    if (back.join(',') !== payload.join(',')) throw Error('round trip');
    if (witness(back) !== witness(payload)) throw Error('witness');
    let refused = false;
    try { through([1, 2, 3, 4, 5, 6, 7, 8, 9], 8); }
    catch (e) { refused = e.message === 'box'; }
    if (!refused) throw Error('capacity');
    return '6 bytes out and back; a 9th byte is refused';
  }
  function factChannels(names) {
    if (!names || names.length !== 6) throw Error('count ' + (names && names.length));
    if (names.join('|') !== CHANNELS.join('|')) throw Error('names');
    if (new Set(names).size !== 6) throw Error('unique');
    return 'six channels, each once';
  }
  function factKana(glyph) {
    if (glyph !== GLYPH) throw Error('glyph');
    const a = (glyph.match(/\| A \|/g) || []).length;
    const n = (glyph.match(/\| N \|/g) || []).length;
    if (a !== 2 || n !== 1) throw Error('anchors ' + a + ' ' + n);
    if (!glyph.startsWith('+ k') || !glyph.endsWith('>-K')) throw Error('envelope');
    return 'two A anchors, one N, envelope +k to -K';
  }
  const api = { O3HASH, CHANNELS, GLYPH, factO3, factReturn, factChannels, factKana };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else Object.assign(root, api);
})(typeof globalThis !== 'undefined' ? globalThis : this);
