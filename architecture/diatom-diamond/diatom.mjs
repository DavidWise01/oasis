// OASIS {{d}} v0.1 — separate, lossless 4/3 carrier. Frozen kernel unchanged.
export const FRAME = '|.|.|.|';
export const VERSION = '0.1.0';
export const LANES = Object.freeze([
  ['.',':','|',"'",'z'], ['a','b','c','d','e'],
  ['f','g','h','i','j','k'], ['l','m','n','o','p'],
  ['q','r','s','t','u','v'], ['w','x','y','0','1'],
  ['2','4','6','8','0'], ['1','3','5','7','9']
].map(row => Object.freeze(row)));
export const ADDRESS_SPACE = Object.freeze(LANES.flatMap((row, i) =>
  row.map((glyph, j) => Object.freeze({ address:'i'+(i+1)+':'+j, glyph }))));
function fail(message) { throw new Error('d-lang: '+message); }
function view(n) {
  if (!Number.isInteger(n) || n < 0 || n > 7) fail('view must be 0..7');
  return n;
}
export function glyphAt(addr) {
  const match = typeof addr === 'string' && /^i([1-8]):([0-9]+)$/.exec(addr);
  if (!match) fail('bad address: '+addr);
  const lane = Number(match[1])-1, index = Number(match[2]);
  if (!Number.isSafeInteger(index) || index >= LANES[lane].length) fail('out-of-bounds address: '+addr);
  return LANES[lane][index];
}
export function encode(addresses, sourceView=0) {
  view(sourceView);
  if (!Array.isArray(addresses)) fail('expected coordinate array');
  addresses.forEach(glyphAt);
  const cells=[];
  for (let i=0;i<addresses.length;i+=4) {
    const part=addresses.slice(i,i+4);
    cells.push({count:part.length,nodes:part.concat(Array(4-part.length).fill('_'))});
  }
  return {language:'d',version:VERSION,frame:FRAME,sourceView,view:sourceView,length:addresses.length,cells};
}
function check(p) {
  if (!p || p.language!=='d' || p.version!==VERSION || p.frame!==FRAME) fail('bad packet');
  view(p.sourceView);view(p.view);
  if (!Array.isArray(p.cells) || !Number.isSafeInteger(p.length) || p.length<0) fail('bad length/cells');
  let length=0;
  p.cells.forEach((cell,i)=>{
    if (!cell || !Number.isInteger(cell.count) || cell.count<1 || cell.count>4 ||
        !Array.isArray(cell.nodes) || cell.nodes.length!==4) fail('bad cell');
    if (i<p.cells.length-1 && cell.count!==4) fail('non-final partial cell');
    cell.nodes.forEach((token,j)=>{
      if (j<cell.count) glyphAt(token);
      else if (token!=='_') fail('padding must be _');
    });
    length+=cell.count;
  });
  if (length!==p.length) fail('length mismatch');
  return p.cells;
}
export function decode(packet) {
  return check(packet).flatMap(cell=>cell.nodes.slice(0,cell.count));
}
export function project(packet,targetView) {
  view(targetView);check(packet);
  return {...packet,view:targetView,cells:packet.cells.map(c=>({count:c.count,nodes:c.nodes.slice()}))};
}
export function serialize(packet) {
  const cells=check(packet);
  const header='{{d::v'+packet.sourceView+'>v'+packet.view+'::'+FRAME+'::';
  return cells.length ? cells.map(c=>header+c.count+'::'+c.nodes.join(',')+'}}').join('\n')
                      : header+'0::_}}';
}
export function deserialize(source) {
  if (typeof source!=='string' || !source.trim()) fail('empty source');
  const lines=source.trim().split(/\r?\n/);
  const re=/^\{\{d::v([0-7])>v([0-7])::\|\.\|\.\|\.\|::([0-4])::([^{}]+)\}\}$/;
  let sourceView=null,currentView=null;
  const cells=[];
  lines.forEach((line,i)=>{
    const m=re.exec(line.trim());
    if (!m) fail('bad record at line '+(i+1));
    if (sourceView===null) {sourceView=Number(m[1]);currentView=Number(m[2]);}
    else if (sourceView!==Number(m[1]) || currentView!==Number(m[2])) fail('mixed views');
    const count=Number(m[3]),raw=m[4];
    if (count===0) {
      if (lines.length!==1 || raw!=='_') fail('invalid empty packet');
    } else cells.push({count,nodes:raw.split(',')});
  });
  const packet={language:'d',version:VERSION,frame:FRAME,sourceView,view:currentView,
    length:cells.reduce((n,c)=>n+c.count,0),cells};
  check(packet);
  return packet;
}
