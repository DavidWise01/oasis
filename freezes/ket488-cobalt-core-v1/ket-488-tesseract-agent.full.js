

(()=>{'use strict';
const $=id=>document.getElementById(id);
const canvas=$('scene'),ctx=canvas.getContext('2d',{alpha:false});
if(!ctx){$('hudmode').textContent='CANVAS 2D UNAVAILABLE';return}
const ROOTS=[{name:'+H',color:'#f05c65'},{name:'+O',color:'#33d3a0'},{name:'−N',color:'#ab75ff'},{name:'+N',color:'#54c9ff'}];
const TOKEN='-+001122334455667788990099887766554433221100-+';
const KEY='ket488-tesseract-agent-palette-v1';
const CENTER=Object.freeze({x:0,y:0,z:0,w:0});
const COBALT_CORE=Object.freeze({symbol:'Co',label:'Cobalt Core',hex:'#0047AB',glow:'#4fa3ff',ring:'#dff3ff',origin:CENTER});
const VERTICES=Array.from({length:16},(_,i)=>[(i&1)?1:-1,(i&2)?1:-1,(i&4)?1:-1,(i&8)?1:-1]);
const EDGES=[];for(let i=0;i<16;i++)for(let d=0;d<4;d++){const j=i^(1<<d);if(i<j)EDGES.push({a:i,b:j,dim:d})}
const CORE_LINKS=Object.freeze({vertices:VERTICES.length,chromatic:488,total:VERTICES.length+488});
const STATES=['patrol','trace','harmonize','vertex'];
const TOROID_SHAPE=Object.freeze([3,3,3]);
const TOROID_CHOICES=3*3, TOROID_PER_VERTEX=TOROID_CHOICES**3;
const VERTEX_TOROIDS=VERTICES.map((coords,id)=>Object.freeze({id,coords:Object.freeze([...coords]),count:TOROID_PER_VERTEX}));
const TOTAL_VERTEX_STATES=VERTEX_TOROIDS.length*TOROID_PER_VERTEX;
const localIndex=digits=>digits[0]*81+digits[1]*9+digits[2];
const unpackIndex=i=>[Math.floor(i/81),Math.floor(i/9)%9,i%9];
function hslHex(h,s,l){
 s/=100;l/=100;const a=s*Math.min(l,1-l);
 const f=n=>{const k=(n+h/30)%12;return Math.round(255*(l-a*Math.max(-1,Math.min(k-3,9-k,1))))};
 return '#'+[0,8,4].map(n=>f(n).toString(16).padStart(2,'0')).join('');
}
function baseColor(i){return hslHex(360*(i+.5)/488,85,48+(i*13)%19)}
function baseRecords(){return Array.from({length:488},(_,i)=>({address:i+1,hex:baseColor(i),wavelength_nm:null,source:'procedural-neon-address'}))}
let records=baseRecords(),paletteKind='PROCEDURAL';
function fromStorage(){
 try{const saved=localStorage.getItem(KEY);if(!saved)return;const data=JSON.parse(saved);
  const list=validateRecords(data.records||data);records=list;paletteKind='LOCALLY IMPORTED';
 }catch(err){console.warn('Local palette unavailable:',err)}
}
function validateRecords(payload){
 if(!Array.isArray(payload)||payload.length!==488)throw Error('Need exactly 488 records.');
 const arr=Array(488).fill(null);
 for(const item of payload){
  if(!item||!Number.isInteger(item.address)||item.address<1||item.address>488)throw Error('Address must be integer 1..488');
  const col=item.hex;if(typeof col!=='string'||!/^#[0-9a-f]{6}$/i.test(col))throw Error('Each address must have #RRGGBB');
  if(arr[item.address-1])throw Error('Duplicate address '+item.address);
  const w=item.wavelength_nm==null?null:Number(item.wavelength_nm);
  if(w!==null&&(!Number.isFinite(w)||w<=0))throw Error('Wavelength must be positive or null');
  arr[item.address-1]={address:item.address,hex:col.toLowerCase(),wavelength_nm:w,source:String(item.source||'user-supplied-unverified').slice(0,220)};
 }
 return arr;
}
fromStorage();
if(VERTICES.length!==16||EDGES.length!==32||CORE_LINKS.total!==504||COBALT_CORE.origin!==CENTER||TOROID_PER_VERTEX!==729||TOTAL_VERTEX_STATES!==11664||records.length!==488||new Set(baseRecords().map(r=>r.hex)).size!==488)throw Error('GEOMETRY_OR_TOROID_INVARIANT');
const state={selected:184,policy:'patrol',agent:true,cadence:1200,ticks:0,steps:0,carry:0,speed:.65,spin:0,axis:{w:0,x:0,y:0,z:0},
 yaw:.32,pitch:.16,zoom:1,vertex:0,digits:[0,0,0],show:{edges:true,vertices:true,wraps:true,nodes:true,corelinks:true,neon:true,trails:true,motion:true},trail:[],hover:null};
const root=z=>Math.floor((z-1)/122),slot=z=>(z-1)%122+1,addr=(r,s)=>122*r+s;
const props=z=>({id:z,root:root(z),slot:slot(z),entry:records[z-1]});
const name=z=>ROOTS[root(z)].name+slot(z);
const rgb=hex=>[1,3,5].map(k=>parseInt(hex.slice(k,k+2),16));
const targetRGB=rgb('#e8a5ce');
function dist(a,b){return Math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2+(a[2]-b[2])**2)}
function log(s){
 const li=document.createElement('li');li.textContent='#'+String(state.steps).padStart(3,'0')+' · '+s;
 $('events').prepend(li);while($('events').childElementCount>14)$('events').lastElementChild.remove();
}
function select(z,source='USER',eventLog=true){
 if(!Number.isInteger(z)||z<1||z>488)return;
 state.selected=z;state.trail.push(z);if(state.trail.length>32)state.trail.shift();
 if(eventLog)log(source+' → Z'+z+' / '+name(z));
 update();
}
function agentStep(){
 state.steps++;
 const prior=state.selected;let dest=prior;let reason='';
 if(state.policy==='patrol'){dest=((prior-1+37)%488)+1;reason='PATROL +37'}
 else if(state.policy==='trace'){dest=addr((root(prior)+1)%4,slot(prior));reason='SAME SLOT '+slot(prior)}
 else if(state.policy==='vertex'){
  const global=(state.vertex*TOROID_PER_VERTEX+localIndex(state.digits)+1)%TOTAL_VERTEX_STATES;
  state.vertex=Math.floor(global/TOROID_PER_VERTEX);
  state.digits=unpackIndex(global%TOROID_PER_VERTEX);
  log('VERTEX-WALK · V'+String(state.vertex).padStart(2,'0')+' T'+String(localIndex(state.digits)).padStart(3,'0'));
  update();return;
 }
 else if(state.policy==='harmonize'){
  const nextSlot=(slot(prior)%122)+1;
  const candidates=[0,1,2,3].map(r=>addr(r,nextSlot));
  dest=candidates.reduce((best,z)=>dist(rgb(records[z-1].hex),targetRGB)<dist(rgb(records[best-1].hex),targetRGB)?z:best,candidates[0]);
  reason='ROSE-QUARTZ MIN ΔRGB '+dist(rgb(records[dest-1].hex),targetRGB).toFixed(1);
 }
 select(dest,reason);
}
const nodes=[];
for(let i=0;i<488;i++){
 const r=Math.floor(i/122),loc=i%122;
 const u=2*Math.PI*(r/4+(loc+.5)/488);
 const v=2*Math.PI*((loc*47)%122+.5)/122+r*.18;
 const R=.81,minor=.24;
 nodes.push({address:i+1,q:[(R+minor*Math.cos(v))*Math.cos(u),(R+minor*Math.cos(v))*Math.sin(u),minor*Math.sin(v),.14*Math.sin(2*u+v)]});
}
function rotate(q,a,b,theta){const c=Math.cos(theta),s=Math.sin(theta),x=q[a],y=q[b];q[a]=x*c-y*s;q[b]=x*s+y*c}
let width=0,height=0,dpr=1;
function resize(){
 const box=canvas.getBoundingClientRect();width=Math.max(350,box.width);height=Math.max(320,box.height);
 dpr=Math.min(2,window.devicePixelRatio||1);canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);
 ctx.setTransform(dpr,0,0,dpr,0,0);
}
const RAD=Math.PI/180;
function project(v){
 const q=v.slice();
 rotate(q,0,3,(state.axis.w*RAD)+state.spin*.64);
 rotate(q,1,3,state.axis.y*RAD-state.spin*.31);
 rotate(q,2,3,state.axis.z*RAD+state.spin*.29);
 rotate(q,0,1,state.axis.x*RAD+state.spin*.21);
 const persp4=3.7/(3.7-q[3]),r=[q[0]*persp4,q[1]*persp4,q[2]*persp4];
 rotate(r,0,2,state.yaw);rotate(r,1,2,state.pitch);
 const persp3=4.3/(4.3-r[2]);
 const sc=Math.min(width*.40,height*.30)*state.zoom;
 return {x:width/2+r[0]*persp3*sc,y:height/2-r[1]*persp3*sc,depth:r[2],s:persp3};
}
function strokePoints(path,color,widthPx=1,alpha=1){
 if(path.length<2)return;
 ctx.beginPath();ctx.moveTo(path[0].x,path[0].y);
 for(let i=1;i<path.length;i++)ctx.lineTo(path[i].x,path[i].y);
 ctx.strokeStyle=color;ctx.lineWidth=widthPx;ctx.globalAlpha=alpha;ctx.stroke();ctx.globalAlpha=1;
}
function backdrop(t){
 const g=ctx.createRadialGradient(width*.5,height*.48,10,width*.5,height*.48,width*.68);
 g.addColorStop(0,'#193154');g.addColorStop(.47,'#0a1730');g.addColorStop(1,'#040913');ctx.fillStyle=g;ctx.fillRect(0,0,width,height);
 for(let i=0;i<120;i++){
  const x=((i*7919)%997)/997*width,y=((i*4357)%991)/991*height;
  ctx.fillStyle=i%9===0?'#c2c9ff87':'#6689bf55';ctx.fillRect(x,y,i%15===0?2:1,i%15===0?2:1);
 }
}
function torusWraps(){
 if(!state.show.wraps)return;
 const colors=['#e56a87','#6aefc3','#faf7ff','#c995f6','#74c9ff'];
 for(let k=0;k<5;k++){
  const line=[];
  for(let t=0;t<=168;t++){
   const u=2*Math.PI*t/168;
   const v=u*(k%2===0?2:3)+k*.8;
   const radius=.61+k*.085,minor=.12+(k%2)*.036;
   line.push(project([(radius+minor*Math.cos(v))*Math.cos(u),(radius+minor*Math.cos(v))*Math.sin(u),minor*Math.sin(v),.14*Math.sin(2*u+v)]));
  }
  strokePoints(line,colors[k],k===2?2.5:1.65,k===2?.85:.51);
 }
}
const vertexPixels=[];
function tesseract(v){
 vertexPixels.length=0;v.forEach((p,id)=>vertexPixels.push({id,x:p.x,y:p.y,depth:p.depth}));
 if(!state.show.edges&&!state.show.vertices)return;
 if(state.show.edges){
 const edges=EDGES.map(e=>({...e,z:(v[e.a].depth+v[e.b].depth)/2})).sort((a,b)=>a.z-b.z);
 for(const e of edges){
  const a=v[e.a],b=v[e.b];const grad=ctx.createLinearGradient(a.x,a.y,b.x,b.y);
  grad.addColorStop(0,e.dim===3?'#d79aff':'#75dcff');
  grad.addColorStop(1,e.dim===3?'#ffcc87':'#bfffff');
  ctx.lineWidth=e.dim===3?1.5:1.15;
  ctx.globalAlpha=e.dim===3?.84:.62;
  ctx.strokeStyle=grad;ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();
 }
 }
 ctx.globalAlpha=1;
 if(state.show.vertices){
  for(let i=0;i<v.length;i++){
   const p=v[i],active=i===state.vertex;
   const color=records[(i*29)%488].hex;
   ctx.save();ctx.shadowColor=active?'#ffecff':color;ctx.shadowBlur=active?25:12;
   ctx.beginPath();ctx.fillStyle=active?'#f8e9ff':color;ctx.arc(p.x,p.y,active?10:7,0,Math.PI*2);ctx.fill();
   ctx.shadowBlur=0;ctx.lineWidth=active?2.5:1;ctx.strokeStyle=active?'#f9feff':'#d2ebff';ctx.stroke();
   ctx.fillStyle='#f9f5ff';ctx.textAlign='center';ctx.font='10px ui-monospace,monospace';
   ctx.fillText('V'+String(i).padStart(2,'0'),p.x,p.y-14);
   ctx.restore();
  }
 }
}
const particlePixels=[];
function particles(projections){
 particlePixels.length=0;
 const order=projections.slice().sort((a,b)=>a.p.depth-b.p.depth);
 for(const {address,p} of order){
  particlePixels[address-1]={x:p.x,y:p.y};
  if(!state.show.nodes)continue;
  const sel=address===state.selected,near=slot(address)===slot(state.selected);
  const radius=(sel?7:near?3.3:2.6)*Math.max(.75,Math.min(1.3,p.s));
  if(sel){ctx.shadowColor=records[address-1].hex;ctx.shadowBlur=17}
  ctx.globalAlpha=sel?1:near?.94:.86;
  ctx.beginPath();ctx.fillStyle=records[address-1].hex;ctx.arc(p.x,p.y,radius,0,Math.PI*2);ctx.fill();
  if(sel){ctx.strokeStyle='#ffffff';ctx.lineWidth=1.6;ctx.stroke();ctx.shadowBlur=0}
 }
 ctx.globalAlpha=1;
}
function trail(){
 if(!state.show.trails||state.trail.length<2)return;
 const pixels=state.trail.map(z=>particlePixels[z-1]).filter(Boolean);
 strokePoints(pixels,'#ffffff',1.6,.55);
}
function origin(p){
 ctx.save();ctx.shadowColor=COBALT_CORE.glow;ctx.shadowBlur=25;
 ctx.beginPath();ctx.arc(p.x,p.y,21,0,Math.PI*2);ctx.fillStyle=COBALT_CORE.hex;ctx.fill();
 ctx.shadowBlur=0;ctx.lineWidth=2.2;ctx.strokeStyle=COBALT_CORE.ring;ctx.stroke();
 ctx.beginPath();ctx.arc(p.x,p.y,28,0,Math.PI*2);ctx.strokeStyle='#82cbff88';ctx.lineWidth=1.2;ctx.stroke();
 ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillStyle='#fff';
 ctx.font='bold 15px ui-monospace,monospace';ctx.fillText(COBALT_CORE.symbol,p.x,p.y-4);
 ctx.fillStyle='#dbebff';ctx.font='bold 10px ui-monospace,monospace';ctx.fillText('0',p.x,p.y+10);
 ctx.fillStyle='#bad9ff';ctx.font='11px ui-monospace,monospace';ctx.fillText('Co·0 · PINNED',p.x,p.y+44);
 ctx.restore();return p;
}
function drawCoreLinks(core,chromatic,vertices){
 if(!state.show.corelinks)return;
 if(chromatic.length!==CORE_LINKS.chromatic||vertices.length!==CORE_LINKS.vertices)throw Error('COBALT_LINK_COUNT_MISMATCH');
 ctx.save();ctx.lineCap='round';
 ctx.beginPath();for(const a of chromatic){ctx.moveTo(core.x,core.y);ctx.lineTo(a.p.x,a.p.y)}
 ctx.strokeStyle='#398bf5';ctx.globalAlpha=.13;ctx.lineWidth=.75;ctx.stroke();
 ctx.beginPath();for(const v of vertices){ctx.moveTo(core.x,core.y);ctx.lineTo(v.x,v.y)}
 ctx.strokeStyle='#8ad0ff';ctx.globalAlpha=.25;ctx.lineWidth=1.15;ctx.stroke();
 const p=chromatic[state.selected-1]?.p;
 if(p){ctx.beginPath();ctx.moveTo(core.x,core.y);ctx.lineTo(p.x,p.y);ctx.strokeStyle='#ddf1ff';ctx.globalAlpha=.78;ctx.lineWidth=2;ctx.stroke()}
 const selected=vertices[state.vertex];
 if(selected){ctx.beginPath();ctx.moveTo(core.x,core.y);ctx.lineTo(selected.x,selected.y);ctx.strokeStyle='#efd4ff';ctx.globalAlpha=.85;ctx.lineWidth=2.7;ctx.stroke()}
 ctx.restore();
}
function neonInset(){
 if(!state.show.neon)return;
 const x=width-88,y=height-84;
 ctx.save();ctx.strokeStyle='#8bdcf6aa';ctx.lineWidth=1;
 for(const r of [23,50]){ctx.beginPath();ctx.arc(x,y,r,0,2*Math.PI);ctx.stroke()}
 for(let i=0;i<10;i++){
  const inner=i<2,local=inner?i:i-2,total=inner?2:8,r=inner?23:50,ang=local/total*Math.PI*2-state.spin*.3;
  ctx.beginPath();ctx.fillStyle=inner?'#74efff':'#d4a4ff';ctx.arc(x+Math.cos(ang)*r,y+Math.sin(ang)*r,4.2,0,Math.PI*2);ctx.fill()
 }
 ctx.fillStyle='#f7ecff';ctx.font='bold 16px ui-monospace,monospace';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('Ne',x,y);
 ctx.fillStyle='#afc3de';ctx.font='10px ui-monospace,monospace';ctx.fillText('10 e⁻ · 2|8',x,y+69);ctx.restore();
}
function draw(){
 if(!width)return;
 const chromatic=nodes.map(n=>({address:n.address,p:project(n.q)}));
 const vertices=VERTICES.map(v=>project(v.map(n=>n*1.18)));
 const core=project([CENTER.x,CENTER.y,CENTER.z,CENTER.w]);
 backdrop(state.spin);torusWraps();drawCoreLinks(core,chromatic,vertices);
 particles(chromatic);tesseract(vertices);trail();origin(core);neonInset();
}
const swatches=[];
function buildPalette(){
 $('palette').replaceChildren();swatches.length=0;
 for(let z=1;z<=488;z++){
  const b=document.createElement('button');b.type='button';b.className='swatch';b.title='Z'+z+' '+name(z);
  b.style.setProperty('--c',records[z-1].hex);
  b.setAttribute('aria-label','Select chromatic address Z'+z+' '+name(z));
  b.onclick=()=>select(z);$('palette').append(b);swatches.push(b);
 }
}
function buildRoots(){
 $('roots').replaceChildren();
 ROOTS.forEach((r,i)=>{
  const b=document.createElement('button');b.type='button';b.style.setProperty('--c',r.color);
  const title=document.createElement('strong');title.textContent=r.name;
  const sub=document.createElement('small');sub.textContent=(i*122+1)+'–'+((i+1)*122);
  b.append(title,sub);b.onclick=()=>select(i*122+1,'ROOT');
  $('roots').append(b);
 });
}

const vertexButtons=[],tripletButtons=[];
function selectVertex(id,source='USER'){
 if(!Number.isInteger(id)||id<0||id>=16)return;
 state.vertex=id;log(source+' VERTEX V'+String(id).padStart(2,'0'));update()
}
function selectDigit(plane,digit,source='USER'){
 if(plane<0||plane>=3||digit<0||digit>=9)return;
 state.digits[plane]=digit;log(source+' TOROID PLANE '+(plane+1)+' CELL '+(digit+1));update()
}
function makeVertexUI(){
 const host=$('vertices-grid');
 VERTEX_TOROIDS.forEach(v=>{
  const btn=document.createElement('button');btn.type='button';btn.className='vertex-button';
  btn.append(document.createElement('b'),document.createElement('small'));
  btn.firstChild.textContent='V'+String(v.id).padStart(2,'0');
  btn.lastChild.textContent=v.coords.map(n=>n>0?'+':'−').join('');
  btn.onclick=()=>selectVertex(v.id);
  btn.setAttribute('aria-label','Select tesseract vertex '+v.id+', 729 configurations');
  host.append(btn);vertexButtons.push(btn);
 });
 const panel=$('triplets');
 for(let plane=0;plane<3;plane++){
  const box=document.createElement('div');box.className='triplet';
  const title=document.createElement('h3');title.textContent='PLANE '+(plane+1)+' · 3×3';box.append(title);
  const grid=document.createElement('div');grid.className='triplet-grid';
  const buttons=[];
  for(let k=0;k<9;k++){
   const b=document.createElement('button');b.type='button';b.textContent=String(k+1);
   b.setAttribute('aria-label','Plane '+(plane+1)+' row '+(Math.floor(k/3)+1)+' column '+(k%3+1));
   b.onclick=()=>selectDigit(plane,k);
   buttons.push(b);grid.append(b);
  }
  box.append(grid);panel.append(box);tripletButtons.push(buttons);
 }
 $('vertex-next').onclick=()=>selectVertex((state.vertex+1)%16,'NEXT');
 $('config-next').onclick=()=>{
  const next=(localIndex(state.digits)+1)%TOROID_PER_VERTEX;
  state.digits=unpackIndex(next);log('NEXT REGISTER T'+String(next).padStart(3,'0'));update();
 };
}
function updateVertexUI(){
 vertexButtons.forEach((button,index)=>button.setAttribute('aria-pressed',String(index===state.vertex)));
 tripletButtons.forEach((grid,p)=>grid.forEach((button,k)=>button.setAttribute('aria-pressed',String(state.digits[p]===k))));
 const v=VERTEX_TOROIDS[state.vertex],loc=localIndex(state.digits),global=state.vertex*TOROID_PER_VERTEX+loc;
 $('vertex-status').textContent='V'+String(v.id).padStart(2,'0')+' · 4D SIGN ['+v.coords.join(', ')+']\n'+
 'PER-VERTEX  {{3×3}}^{{3}} = 9³ = 729\n'+
 'PLANE CELLS '+state.digits.map(n=>Math.floor(n/3)+1+','+(n%3+1)).join(' | ')+
 '\nLOCAL INDEX '+loc+' / 728   [T'+String(loc).padStart(3,'0')+']'+
 '\nGLOBAL INDEX '+global+' / 11663\n'+
 'TOTAL 16 VERTICES × 729 = 11,664 STATES\n'+
 'PIN 0=(0,0,0,0) · KET 488 COLORS SEPARATE';
}

const DESCRIPTIONS={
 vertex:'Traverse 16 anchored vertices, each with 729 ordered 3×3×3 state configurations; log each next state.',
 patrol:'Advance exactly 37 mod 488 each step; this visits all 488 addresses before repeating.',
 trace:'Move to the next of four roots at the same slot, preserving the 1–122 local coordinate.',
 harmonize:'Advance one local slot, compare its four colors to rose-quartz #E8A5CE in RGB distance, then select the nearest.'
};
function update(){
 updateVertexUI();
 $('address').value=state.selected;$('address-v').textContent=name(state.selected);
 $('agentstatus').textContent=state.agent?'RUNNING':'PAUSED';
 $('hudmode').textContent=state.policy.toUpperCase()+' · '+(state.agent?'RUNNING':'PAUSED');
 $('corelinks-status').textContent='504 NODE→CORE LINKS '+(state.show.corelinks?'ACTIVE':'HIDDEN');
 $('auto').textContent=state.agent?'Ⅱ PAUSE AGENT':'▶ RESUME AGENT';
 $('policy').textContent=DESCRIPTIONS[state.policy];
 $('cadence-v').textContent=(state.cadence/1000).toFixed(1)+' s';
 $('speed-v').textContent=state.speed.toFixed(2)+'×';
 for(const id of ['w','x','y','z'])$('axis-'+id+'-v').textContent=state.axis[id]+'°';
 const p=props(state.selected),e=p.entry;
 $('inspector').textContent='Z'+p.id+' :: '+ROOTS[p.root].name+p.slot+'\nROOT '+(p.root+1)+'/4 · SLOT '+p.slot+'/122'+
 '\nCOLOR '+e.hex.toUpperCase()+' · '+paletteKind+
 '\nWAVELENGTH '+(e.wavelength_nm==null?'NOT PROVIDED':e.wavelength_nm+' nm (supplied)')+
 '\nSOURCE '+e.source+
 '\nAGENT '+state.policy.toUpperCase()+' / '+(state.agent?'ACTIVE':'PAUSED')+
 '\nCORE '+COBALT_CORE.label+' / Co·0 / '+COBALT_CORE.hex+
 '\nLINKS '+CORE_LINKS.vertices+' vertex + '+CORE_LINKS.chromatic+' chromatic = '+CORE_LINKS.total+
 '\nPIN ((((( wx0yz ))))) · CENTER ZERO FIXED'+
 '\n8×3 REGISTER SLOT '+(((p.id-1)%24)+1)+'/24';
 swatches.forEach((b,i)=>{b.dataset.active=String(i+1===state.selected);b.style.setProperty('--c',records[i].hex)});
 $('quartet').replaceChildren();
 for(let i=0;i<4;i++){
  const z=addr(i,p.slot),q=document.createElement('button');q.type='button';q.style.setProperty('--c',records[z-1].hex);
  const head=document.createElement('strong');head.textContent=ROOTS[i].name+p.slot;
  const small=document.createElement('small');small.textContent='Z'+z;
  q.append(head,small);q.setAttribute('aria-pressed',String(z===state.selected));q.onclick=()=>select(z,'INTERSECTION');
  $('quartet').append(q);
 }
 $('register').textContent='REGISTRY  488 = 4 × 122\nTESSY     4D = 16V / 32E\nVESSEL    ((((( wx0yz )))))\nPIN       (0,0,0,0) · IMMUTABLE\n'+
 'COBALT    Co·0 / 504 symbolic core connections\n8×3       24 symbolic register slots\nFOCUS     '+(Math.floor((p.id-1)%24/3)+1)+' / '+(((p.id-1)%3)+1)+
 '\nNEON      Z10 · 1s² 2s² 2p⁶ · shell 2|8\nQCD       color charge ≠ optical color';
}
for(const input of document.querySelectorAll('input[data-axis]')){
 input.oninput=e=>{state.axis[e.target.dataset.axis]=Number(e.target.value);update()};
}
for(const id of ['edges','vertices','wraps','nodes','corelinks','neon','trails','motion']){
 $(id).onchange=e=>{state.show[id]=e.target.checked;update();draw()};
}
$('mode').onchange=e=>{state.policy=e.target.value;state.carry=0;log('POLICY '+state.policy.toUpperCase());update()};
$('auto').onclick=()=>{state.agent=!state.agent;state.carry=0;log(state.agent?'AGENT RESUMED':'AGENT PAUSED');update()};
$('step').onclick=()=>{state.carry=0;agentStep()};
$('address').onchange=e=>{const z=Number(e.target.value);Number.isInteger(z)&&z>=1&&z<=488?select(z):update()};
$('cadence').oninput=e=>{state.cadence=Number(e.target.value);update()};
$('speed').oninput=e=>{state.speed=Number(e.target.value);update()};
$('reset').onclick=()=>{
 state.selected=184;state.vertex=0;state.digits=[0,0,0];state.policy='patrol';state.agent=true;state.steps=0;state.carry=0;state.trail=[];state.axis={w:0,x:0,y:0,z:0};
 $('events').replaceChildren();$('mode').value='patrol';
 for(const id of ['w','x','y','z'])$('axis-'+id).value=0;
 select(184,'GENESIS');
};
$('camera').onclick=()=>{state.yaw=.32;state.pitch=.16;state.zoom=1;state.spin=0;draw()};
$('restore').onclick=()=>{
 records=baseRecords();paletteKind='PROCEDURAL';
 try{localStorage.removeItem(KEY)}catch(e){}
 $('importstate').textContent='Procedural palette restored · 488 unique generated colors';update()
};
$('import').onchange=async e=>{
 const file=e.target.files?.[0];if(!file)return;
 try{
  if(file.size>350000)throw Error('JSON exceeds 350 KB limit');
  const data=JSON.parse(await file.text());const list=validateRecords(data.records||data);
  records=list;paletteKind='USER-SUPPLIED';
  try{localStorage.setItem(KEY,JSON.stringify({records:list}))}catch(err){console.warn('Palette storage unavailable:',err)}
  $('importstate').textContent='Loaded 488 supplied addresses · wavelength fields are not independently verified';update();log('IMPORTED 488-COLOR PALETTE');
 }catch(err){$('importstate').textContent='Import rejected: '+err.message}
 e.target.value='';
};
$('export').onclick=()=>{
 const content=JSON.stringify({
  schema:'ket488-neon-agent-v1',
  vessel:'((((( wx0yz )))))',center:CENTER,
  tesseract:{vertices:16,edges:32,projection:'R4 to R3 to R2'},
  cobalt:{symbol:COBALT_CORE.symbol,pin:CENTER,hex:COBALT_CORE.hex,links:CORE_LINKS,visible:state.show.corelinks},
  provenance:paletteKind,selected:state.selected,
  agent:{policy:state.policy,steps:state.steps,cadence_ms:state.cadence},
  axis:state.axis,vertex:{id:state.vertex,local_index:localIndex(state.digits),global_index:state.vertex*TOROID_PER_VERTEX+localIndex(state.digits),digits:state.digits},vertex_toroid:{per_vertex:TOROID_PER_VERTEX,total:TOTAL_VERTEX_STATES},records
 },null,2);
 const blob=new Blob([content],{type:'application/json'});
 const url=URL.createObjectURL(blob),a=document.createElement('a');
 a.href=url;a.download='ket488-neon-tesseract-state.json';a.click();
 setTimeout(()=>URL.revokeObjectURL(url),1000);
};
let down=null;
canvas.addEventListener('pointerdown',e=>{
 down={x:e.clientX,y:e.clientY,yaw:state.yaw,pitch:state.pitch,moved:false};
 canvas.classList.add('dragging');canvas.setPointerCapture(e.pointerId);
});
canvas.addEventListener('pointermove',e=>{
 if(!down)return;
 const dx=e.clientX-down.x,dy=e.clientY-down.y;
 if(Math.abs(dx)+Math.abs(dy)>6)down.moved=true;
 if(down.moved){state.yaw=down.yaw+dx*.007;state.pitch=Math.max(-1.4,Math.min(1.4,down.pitch+dy*.006))}
});
canvas.addEventListener('pointerup',e=>{
 const old=down;down=null;canvas.classList.remove('dragging');
 if(!old||old.moved)return;
 const box=canvas.getBoundingClientRect();
 const x=(e.clientX-box.left)*width/box.width,y=(e.clientY-box.top)*height/box.height;
 if(state.show.vertices){
  const hit=vertexPixels.map(v=>({...v,d:(x-v.x)**2+(y-v.y)**2})).sort((a,b)=>a.d-b.d)[0];
  if(hit&&hit.d<16*16){selectVertex(hit.id,'CANVAS');return}
 }
 let best=-1,dmin=16*16;
 for(let i=0;i<particlePixels.length;i++){const p=particlePixels[i];if(!p)continue;
  const d=(x-p.x)**2+(y-p.y)**2;if(d<dmin){dmin=d;best=i+1}
 }
 if(best>0)select(best,'CANVAS');
});
canvas.addEventListener('pointercancel',()=>{down=null;canvas.classList.remove('dragging')});
canvas.addEventListener('wheel',e=>{e.preventDefault();state.zoom=Math.max(.45,Math.min(2.35,state.zoom*(e.deltaY>0?.92:1.08)))},{passive:false});
canvas.addEventListener('keydown',e=>{
 if(e.key==='v'){e.preventDefault();selectVertex((state.vertex+1)%16,'KEY')}
 if(e.key==='ArrowRight'){e.preventDefault();select(state.selected%488+1,'KEY')}
 if(e.key==='ArrowLeft'){e.preventDefault();select((state.selected+486)%488+1,'KEY')}
 if(e.key==='+'){state.zoom=Math.min(2.35,state.zoom*1.08)}
 if(e.key==='-'){state.zoom=Math.max(.45,state.zoom*.92)}
});
document.addEventListener('visibilitychange',()=>{if(document.hidden){state.agent=false;state.carry=0;update()}});
let last=0;
function animate(now){
 if(!last)last=now;const dt=Math.min(100,(now-last));last=now;
 if(state.show.motion&&!window.matchMedia('(prefers-reduced-motion: reduce)').matches)state.spin+=dt*.00031*state.speed;
 if(state.agent){state.carry+=dt;while(state.carry>=state.cadence){state.carry-=state.cadence;agentStep()}}
 draw();requestAnimationFrame(animate);
}
resize();window.addEventListener('resize',resize);
makeVertexUI();buildRoots();buildPalette();update();state.trail=[184];log('GENESIS Z184 · 488 nodes · 16 vertices / 32 edges');
requestAnimationFrame(animate);
})();

