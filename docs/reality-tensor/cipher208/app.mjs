import * as T from '../wave/tensor_kernel.mjs';
import * as W from '../wave/wave_kernel.mjs';
import * as C from './cipher208.mjs';
const $=id=>document.getElementById(id);
const params=()=>({wavelength:+$('lambda').value,theta:+$('theta').value,barKick:+$('kick').value});
const initial=()=>{const A=+$('amplitude').value;return [W.complex(A,0),W.complex(.38*A,.24*A)];};
let runtime,autoBusy=false;
function reset(){runtime=new C.Cipher208({params:params(),amplitudes:initial()});$('status').textContent='Initialized. Run 208 forward gates; mirror + invert; run 208 backward gates.';render();}
function drawRing(){
 const canvas=$('ring');const w=980,h=420;canvas.width=w;canvas.height=h;
 const ctx=canvas.getContext('2d');ctx.clearRect(0,0,w,h);
 const cx=490,cy=210,R=169,r=117;
 function tick(mark,start,end,color,thick){
   const a=-Math.PI/2+2*Math.PI*mark/208;ctx.strokeStyle=color;ctx.lineWidth=thick;ctx.beginPath();ctx.moveTo(cx+Math.cos(a)*start,cy+Math.sin(a)*start);ctx.lineTo(cx+Math.cos(a)*end,cy+Math.sin(a)*end);ctx.stroke();
 }
 for(let i=0;i<208;i++){
  const col=C.FORWARD[i]==='.'?'#57f1a5':'#6facc9';
  const backCol=C.BACKWARD[i]==='.'?'#7bbdb2':'#dfaf67';
  tick(i,R-18,R+(i%13===0?15:0),col,i%13===0?4.5:2.7);
  tick(i,r-8,r+4,backCol,2.5);
 }
 for(let i=0;i<16;i++){const a=2*Math.PI*i/16-Math.PI/2;
  ctx.fillStyle='#89b8a0';ctx.textAlign='center';ctx.font='10px ui-monospace, monospace';
  ctx.fillText(String(i+1).padStart(2,'0'),cx+Math.cos(a)*205,cy+Math.sin(a)*205+3);
 }
 // distinct temporal cursors for outer forward and inner inverse path
 const fi=runtime.mode==='forward'?runtime.tick:208;
 const bi=runtime.mode==='backward'?208-runtime.tick:0;
 for(const [index,radius,color] of [[fi,R,'#b2ffc5'],[bi,r,'#fad79d']]){
  const a=-Math.PI/2+index*Math.PI*2/208;ctx.beginPath();ctx.arc(cx+Math.cos(a)*radius,cy+Math.sin(a)*radius,7,0,Math.PI*2);ctx.fillStyle=color;ctx.fill();
 }
 const phase=runtime.mode==='forward'?'FORWARD':runtime.tick>0?'MIRRORED INVERSE':'RECOVERED';
 ctx.textAlign='center';ctx.fillStyle='#a6eec4';ctx.font='bold 14px system-ui';ctx.fillText(phase,cx,cy-10);
 ctx.fillStyle='#edfff3';ctx.font='bold 39px system-ui';ctx.fillText(runtime.mode==='forward'?String(runtime.tick):String(208-runtime.tick),cx,cy+39);
 ctx.fillStyle='#88bea8';ctx.font='12px ui-monospace, monospace';ctx.fillText('/ 208 gates',cx,cy+64);
 ctx.fillStyle='#5edca6';ctx.font='11px ui-monospace, monospace';ctx.fillText('−e   [||||]  :  [(((((()))))) ]   +e',cx,cy+98);
}
function floorGrid(target,pair,type){
 const grid=$(target);grid.replaceChildren();const silo=type==='outer'?pair.outer:pair.inner;const [x,y,z,q]=T.decode4(silo);
 for(let cy=0;cy<10;cy++)for(let cx=0;cx<10;cx++){
  const cell=document.createElement('div');cell.className='cell';
  if(cx===0&&cy===0)cell.classList.add('anchor');
  if(cx===x&&cy===y)cell.classList.add(type==='outer'?'hot':'mirrorHot');
  cell.title=`x=${cx},y=${cy}, selected z=${z},quanta=${q}`;grid.appendChild(cell);
 }
 $('address'+(type==='outer'?'Outer':'Inner')).textContent=`${silo}   [x${x},y${y},z${z},~${q}]`;
}
function render(){
 const pos=runtime.tick,reverse=runtime.mode==='backward';const passed=reverse?208-pos:0;
 $('progressText').textContent=`${reverse?'Backward inverse':'Forward expansion'} · ${reverse?passed:pos}/208`;
 $('progressBar').style.width=`${100*(reverse?passed:pos)/208}%`;
 $('metricSteps').textContent=String(reverse?208+passed:pos);
 $('metricFrame').textContent=String(Math.min(16,Math.floor((reverse?passed:pos)/13)+1)).padStart(2,'0');
 $('metricNorm').textContent=runtime.energyProxy.toFixed(7);
 $('metricEvents').textContent=runtime.totalEvents.toLocaleString();
 $('lambdaVal').textContent=$('lambda').value;
 $('ampVal').textContent=(+$('amplitude').value).toFixed(2);
 $('thetaVal').textContent=(+$('theta').value).toFixed(2);
 $('kickVal').textContent=(+$('kick').value).toFixed(2);
 $('recovery').textContent=reverse&&runtime.tick===0?(runtime.recovered()?'RECOVERED ✓':'RESIDUAL ERROR'):(reverse?'Inverse in progress':'Awaiting inverse');
 $('recovery').style.color=runtime.recovered()?'#58faac':'#add2bb';
 $('leftComplex').textContent=fmt(runtime.amplitudes[0]);$('rightComplex').textContent=fmt(runtime.amplitudes[1]);
 $('symbols').textContent=reverse?C.BACKWARD:C.FORWARD;
 $('glyphCurrent').textContent=reverse?C.BACKWARD[passed]??'✓':C.FORWARD[pos]??'✓';
 $('mirrorInfo').textContent=reverse?'MIRRORED; z ↦ (−z mod 10), channels swapped':'NATURAL; (outer,inner) frame';
 floorGrid('outerGrid',T.decodeTensor(runtime.address),'outer');floorGrid('innerGrid',T.decodeTensor(runtime.address),'inner');
 $('seams').replaceChildren();for(let i=0;i<16;i++){
   const tile=document.createElement('div');tile.className='seam'+(Math.floor((reverse?passed:pos)/13)===i?' active':'');
   tile.innerHTML=`<div class="slabel">${String(i+1).padStart(2,'0')} / shared seam</div><code>${C.windows[i]}</code>`;$('seams').appendChild(tile);
 }
 $('forwardOne').disabled=reverse||pos===208;
 $('forwardAll').disabled=reverse||pos===208;
 $('mirrorBtn').disabled=reverse||pos!==208;
 $('backOne').disabled=!reverse||pos===0;
 $('backAll').disabled=!reverse||pos===0;
 $('status').textContent=runtime.recovered()?'PASS: 208 + 208 operations restored the original wave, in mirrored coordinates.':$('status').textContent;
 drawRing();
}
function fmt(z){return `${z.re.toFixed(5)} ${z.im<0?'−':'+'} ${Math.abs(z.im).toFixed(5)}i`;}
function forward(n){if(autoBusy)return;for(let i=0;i<n;i++)if(!runtime.forward())break;render();}
function backward(n){if(autoBusy)return;for(let i=0;i<n;i++)if(!runtime.backward())break;render();}
$('forwardOne').addEventListener('click',()=>forward(1));$('forwardAll').addEventListener('click',()=>forward(208));
$('mirrorBtn').addEventListener('click',()=>{runtime.beginMirroredReverse();$('status').textContent='Mirrored square↔round, inverted the z axis. Applying U† in reverse order.';render();});
$('backOne').addEventListener('click',()=>backward(1));$('backAll').addEventListener('click',()=>backward(208));
$('reset').addEventListener('click',reset);
$('full').addEventListener('click',()=>{
 if(autoBusy)return;reset();for(let i=0;i<208;i++)runtime.forward();runtime.beginMirroredReverse();for(let i=0;i<208;i++)runtime.backward();render();
});
for(const id of ['lambda','amplitude','theta','kick'])$(id).addEventListener('input',()=>{reset();});
$('verify').addEventListener('click',()=>{
 let ok=C.validateSeams().length===16&&C.reverseInvert(C.BACKWARD)===C.FORWARD;
 for(let i=0;i<10000;i++)if(C.reflectZ(C.reflectZ(i))!==i)ok=false;
 const s=new C.Cipher208({params:params(),amplitudes:initial()});
 for(let i=0;i<208;i++)s.forward();s.beginMirroredReverse();for(let i=0;i<208;i++)s.backward();
 ok=ok&&s.recovered();$('status').textContent=ok?'PASS: 16 seams, 10K local inverses, and 416 wave gates validated.':'FAIL: detected a broken cipher invariant.';render();
});
reset();

