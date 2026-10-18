'use strict';
/* N184 3D/4D viewing instrument. Adds diagnostics, never changes model/runtime data. */
(()=>{
const $=id=>document.getElementById(id),G=window.N184Geometry;
const panel=document.createElement('section');panel.className='panel';
panel.innerHTML='<h2>17 · 4D separation and orientation instrument</h2><canvas id="orientationGauge" style="width:100%;height:180px;border:1px solid #326d83;display:block"></canvas><pre id="orientationReport" aria-live="polite"></pre><button id="orientationExpand">RESTORE EXPANDED 4D</button><button id="orientationFreeze">PAUSE 4D ORIENTATION MONITOR</button><p class="muted">Separations are measured in projected logical units. An aligned projection can collapse W-edges visually without deleting their endpoints or changing the tesseract graph.</p>';
document.querySelector('aside').append(panel);
const canvas=$('orientationGauge'),report=$('orientationReport');let paused=false,last=0;
const angles=()=>G.planes.map((_,i)=>Number($('rot'+i).value));
function analyze(){const a=angles(),mode=$('projection').value,d=Number($('distance').value),points=G.vertices.map(v=>G.projected4(v.map(x=>x*1.26),a,mode,d)),groups=[];
for(let axis=0;axis<4;axis++){const list=G.edges.filter(([u,v])=>G.vertices[u][axis]!==G.vertices[v][axis]).map(([u,v])=>Math.hypot(points[u].x-points[v].x,points[u].y-points[v].y,points[u].z-points[v].z));groups.push({axis:'XYZW'[axis],min:Math.min(...list),avg:list.reduce((a,b)=>a+b,0)/list.length,max:Math.max(...list)})}
let finite=points.every(p=>[p.x,p.y,p.z].every(Number.isFinite));return {groups,finite,wmin:groups[3].min,angles:a,mode,d}}
function paint(z){const dpr=Math.min(2,devicePixelRatio||1),w=Math.max(1,Math.round(canvas.clientWidth*dpr)),h=Math.max(1,Math.round(canvas.clientHeight*dpr));if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h}const ctx=canvas.getContext('2d');ctx.fillStyle='#071728';ctx.fillRect(0,0,w,h);const left=48*dpr,top=22*dpr,row=35*dpr,max=Math.max(1,...z.groups.map(g=>g.max)),usable=w-left-20*dpr;
z.groups.forEach((g,i)=>{ctx.fillStyle='#cbeefa';ctx.font=12*dpr+'px monospace';ctx.fillText(g.axis,left-31*dpr,top+i*row+12*dpr);ctx.fillStyle=i===3?'#f0c87e':'#62b9df';ctx.fillRect(left,top+i*row,Math.max(1,usable*g.avg/max),15*dpr);ctx.fillStyle='#deeff9';ctx.fillText(g.avg.toFixed(3),Math.min(w-82*dpr,left+usable*g.avg/max+5*dpr),top+i*row+12*dpr)})}
function update(){let z=analyze();if(!z.finite){report.textContent='PROJECTION INVALID: non-finite coordinates';return}const near=z.wmin<.025;report.textContent='4D VERTICES: '+G.vertices.length+'  EDGES: '+G.edges.length+'\nPROJECTION: '+z.mode+'\nMINIMUM PROJECTED W EDGE: '+z.wmin.toFixed(5)+' LU\nVIEW STATUS: '+(near?'NEAR-ALIGNED / DEGENERATE VIEW':'W EDGES SEPARATED')+'\nXY / XZ / XW / YZ / YW / ZW ROTATION\n'+z.angles.map((v,i)=>G.planes[i]+'='+v+'°').join('  ');paint(z);window.N184OrientationLast=z}
$('orientationExpand').onclick=()=>{if(window.N184ProjectionPresets)window.N184ProjectionPresets.setPreset('expanded');update()};
$('orientationFreeze').onclick=()=>{paused=!paused;$('orientationFreeze').textContent=paused?'RESUME 4D ORIENTATION MONITOR':'PAUSE 4D ORIENTATION MONITOR'};
function frame(t){if(!paused&&t-last>220){update();last=t}requestAnimationFrame(frame)}
requestAnimationFrame(frame);window.N184Orientation={analyze,update};
})();