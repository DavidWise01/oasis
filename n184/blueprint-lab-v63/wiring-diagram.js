'use strict';
/* N184 visual wiring diagram — zero writes to recovery system. */
(()=>{
const G=window.N184Geometry,$=id=>document.getElementById(id);
const card=document.createElement('section');card.className='panel';
card.style.gridColumn='1 / -1';
card.innerHTML='<h2>16 · Wiring schematic / transaction signal view</h2><canvas id="wiringMap" style="width:100%;height:360px;display:block;border:1px solid #315c76;cursor:crosshair;touch-action:none"></canvas><div id="wiringLegend" class="muted" style="padding-top:8px"></div><button id="wiringPrev">PREV SIGNAL</button><button id="wiringNext">NEXT SIGNAL</button><button id="wiringPlay">AUTO STEP</button><button id="wiringReset">RESET SIGNAL</button><pre id="wiringReadout"></pre><p class="muted">Diagrammatic data route of the frozen mapping. Gateway/commit/replay are labeled visual stages, not live IndexedDB transactions. Red branch depicts rejected/aborted routing without modifying persisted state.</p>';
const footer=document.querySelector('.footer');footer.parentElement.insertBefore(card,footer);
const canvas=$('wiringMap'),ctx=canvas.getContext('2d');
let step=0,auto=false,last=0,selected=0,route='success';
const stages=['SOURCE','GATEWAY','LATTICE 60×40','X CORE','FORWARD','COMMIT','ACK','REVERSE'];
const cols=['#f6bf79','#f9df8c','#64d3f2','#fcf5e5','#70e4ae','#6a9cf7','#8ceac8','#aad3ff'];
function points(w,h){const gap=62,n=stages.length,space=(w-gap*2)/(n-1),y=h*.47;return stages.map((s,i)=>({x:gap+i*space,y,label:s}))}
function line(a,b,color='#438ba9',width=2){ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke()}
function arrow(a,b,color='#4faacb'){line(a,b,color,2);let angle=Math.atan2(b.y-a.y,b.x-a.x),r=7;ctx.fillStyle=color;ctx.beginPath();ctx.moveTo(b.x,b.y);ctx.lineTo(b.x-r*Math.cos(angle-.5),b.y-r*Math.sin(angle-.5));ctx.lineTo(b.x-r*Math.cos(angle+.5),b.y-r*Math.sin(angle+.5));ctx.closePath();ctx.fill()}
function draw(){const d=Math.min(2,devicePixelRatio||1),w=Math.max(1,Math.round(canvas.clientWidth*d)),h=Math.max(1,Math.round(canvas.clientHeight*d));if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h}
ctx.fillStyle='#061729';ctx.fillRect(0,0,w,h);ctx.strokeStyle='#16445b';ctx.lineWidth=.7*d;for(let x=0;x<w;x+=28*d){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,h);ctx.stroke()}for(let y=0;y<h;y+=28*d){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke()}
const p=points(w,h),radius=Math.max(7,13*d);for(let i=0;i<p.length-1;i++)arrow({x:p[i].x+radius,y:p[i].y},{x:p[i+1].x-radius,y:p[i+1].y},i<step?'#6fddbc':'#37667d');
p.forEach((point,i)=>{ctx.fillStyle=i===step?'#ffe4a9':cols[i];ctx.strokeStyle='#d0f3ff';ctx.lineWidth=i===step?3*d:1*d;ctx.beginPath();ctx.arc(point.x,point.y,radius,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.fillStyle='#cce6f1';ctx.font=Math.max(10,11*d)+'px monospace';ctx.textAlign='center';ctx.fillText(String(i),point.x,point.y+4*d);let label=point.label.split(' ');ctx.fillText(label[0],point.x,point.y-29*d);if(label.length>1)ctx.fillText(label.slice(1).join(' '),point.x,point.y-16*d)});
let reject={x:p[5].x,y:h*.83};arrow({x:p[5].x,y:p[5].y+radius},{x:reject.x,y:reject.y-11*d},'#c76f7e');ctx.fillStyle='#f29cac';ctx.font=12*d+'px monospace';ctx.textAlign='center';ctx.fillText('STALE / ABORT: NO COMMIT',reject.x,reject.y);
const addr=Math.min(2399,Math.max(0,Number($('address').value)||0)),nib=Math.min(15,Math.max(0,Number($('nibble').value)||0)),f=G.transformAddress(addr,nib),b=G.inverseAddress(f.address,f.nibble);
ctx.fillStyle='#b7dfec';ctx.textAlign='left';ctx.font=12*d+'px monospace';ctx.fillText('SOURCE '+addr+':'+nib+'     TRANSFORM '+f.address+':'+f.nibble+'     INVERSE '+b.address+':'+b.nibble,17*d,h-17*d);
$('wiringReadout').textContent='VISUAL SIGNAL '+step+'/7: '+stages[step]+'\nADDRESS '+addr+' → '+f.address+' → '+b.address+'\nNIBBLE '+nib+' → '+f.nibble+' → '+b.nibble+'\nMAPPING RECONSTRUCTION '+(b.address===addr&&b.nibble===nib?'PASS':'FAIL');
$('wiringLegend').textContent='Amber ingress · Cyan lattice · White X-core · Green forward map · Blue commit · Red rejected/aborted branch (illustrative)';
}
function sync(){const input=$('step');input.value=step;input.dispatchEvent(new Event('input'));draw()}
$('wiringPrev').onclick=()=>{step=(step+7)%8;sync()};$('wiringNext').onclick=()=>{step=(step+1)%8;sync()};
$('wiringReset').onclick=()=>{step=0;auto=false;sync()};
$('wiringPlay').onclick=()=>{auto=!auto;$('wiringPlay').textContent=auto?'PAUSE SIGNAL':'AUTO STEP'};
canvas.addEventListener('click',e=>{let rect=canvas.getBoundingClientRect(),x=(e.clientX-rect.left)*canvas.width/rect.width;let ps=points(canvas.width,canvas.height),min=Infinity;ps.forEach((p,i)=>{const d=Math.abs(p.x-x);if(d<min){min=d;selected=i}});step=selected;sync()});
function loop(ts){if(auto&&ts-last>700){step=(step+1)%8;sync();last=ts}else if(!auto&&ts-last>280){draw();last=ts}requestAnimationFrame(loop)}
requestAnimationFrame(loop);
})();