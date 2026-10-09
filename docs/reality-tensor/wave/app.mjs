import {GLYPH,MOTIF,parseCarrier,WaveTensor,phaseAt,abs2,complex,gate,ZERO_COMPLEX} from './wave_kernel.mjs';
import {decodeTensor,decode4,encodeTensor} from './tensor_kernel.mjs';
(()=>{
const $=id=>document.getElementById(id);
const RGBA='rgba(80,255,168,';
let sim,initialEnergy=0,energyTrace=[],busy=false;
const runDiv=$('runs'),motifChars=[...MOTIF];
let start=0;
for(const run of parseCarrier(GLYPH).runs){
 const e=document.createElement('span');e.className='run';e.textContent=run.token.repeat(run.count);e.dataset.start=String(start);e.dataset.end=String(start+run.count);runDiv.append(e);start+=run.count;
}
function log(msg){const area=$('history');area.textContent=(new Date()).toLocaleTimeString()+' · '+msg+'\n'+area.textContent.slice(0,2300)}
function fail(err){$('message').textContent='ERROR · '+err.message;log('FAIL '+err.message)}
function cfg(){return {wavelength:+$('wavelength').value,theta:+$('coupling').value*Math.PI/180,barKick:+$('kick').value*Math.PI/180,pruneEpsilon:1e-14}}
function syncLabels(){$('wlValue').textContent=$('wavelength').value+' dot steps';$('ampValue').textContent=(+$('amplitude').value).toFixed(2);$('thetaValue').textContent=$('coupling').value+'°';$('kickValue').textContent=$('kick').value+'°'}
function fillCanvas(id){const can=$(id),ctx=can.getContext('2d');ctx.clearRect(0,0,can.width,can.height);ctx.fillStyle='#06170e';ctx.fillRect(0,0,can.width,can.height);return {can,ctx};}
function drawWave(){
 const {can,ctx}=fillCanvas('waveCanvas');const p=cfg(),A=+$('amplitude').value;
 const H=can.height,W=can.width;
 ctx.strokeStyle='#244f3b';ctx.lineWidth=1;
 for(let j=0;j<9;j++){const y=H*j/8;ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}
 ctx.strokeStyle='#56ffaf';ctx.lineWidth=2.3;ctx.beginPath();
 for(let j=0;j<=360;j++){const x=j*W/360,modelSample=Math.floor(j/360*64);
 const ang=phaseAt(modelSample,p.wavelength,p.barKick),y=H/2-(A/2.1)*Math.cos(ang)*(H*.44);
 if(j===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
 }ctx.stroke();
 const glyphStep=sim?sim.tick%14:0;const cursor=glyphStep/14*W;
 ctx.strokeStyle='#e8ca81';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(cursor,0);ctx.lineTo(cursor,H);ctx.stroke();
 const phase=phaseAt(sim?sim.tick:0,p.wavelength,p.barKick);
 $('phase').textContent='φ = '+((phase*180/Math.PI)%360).toFixed(1)+'°';
 for(const e of runDiv.children)e.classList.toggle('active',glyphStep>=+e.dataset.start&&glyphStep<+e.dataset.end);
}
function drawGrid(id,idx){const {can,ctx}=fillCanvas(id);let matrix=new Float64Array(100),top=0;
 if(sim)for(const [tensor,z] of sim.amplitudes){const adr=decodeTensor(tensor),coords=decode4(idx===0?adr.outer:adr.inner),key=coords[0]*10+coords[1];matrix[key]+=abs2(z);top=Math.max(top,matrix[key]);}
 const W=can.width,H=can.height,w=W/10,h=H/10;
 for(let i=0;i<10;i++)for(let j=0;j<10;j++){
 const v=matrix[i*10+j],level=top?Math.sqrt(v/top):0;
 ctx.fillStyle=`rgba(69,255,160,${.045+.9*level})`;ctx.fillRect(j*w+.6,i*h+.6,w-1.2,h-1.2);
 if(level>.3){ctx.fillStyle='#071b13';ctx.font='12px ui-monospace';ctx.textAlign='center';ctx.fillText(v.toFixed(2),j*w+w/2,i*h+h/2+4)}
 }
 ctx.strokeStyle='#306746';ctx.lineWidth=1;ctx.strokeRect(0,0,W,H);
}
function drawEnergy(){const {can,ctx}=fillCanvas('normCanvas'),W=can.width,H=can.height;
 ctx.strokeStyle='#274834';ctx.beginPath();ctx.moveTo(0,H/2);ctx.lineTo(W,H/2);ctx.stroke();
 ctx.strokeStyle='#56ffaf';ctx.lineWidth=2.6;ctx.beginPath();
 const seq=energyTrace.slice(-90),baseline=initialEnergy||1;
 seq.forEach((a,i)=>{const x=seq.length<2?0:i*W/(seq.length-1),relative=(a-baseline)/baseline,y=H/2-Math.max(-1,Math.min(1,relative*1e11))*H*.4;if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y)});
 ctx.stroke();ctx.font='12px ui-monospace';ctx.fillStyle='#81b998';ctx.fillText('norm drift × 10¹¹',12,20);}
function render(){syncLabels();drawWave();drawGrid('outerCanvas',0);drawGrid('innerCanvas',1);drawEnergy();if(!sim)return;
 $('tick').textContent=String(sim.tick);$('occupancy').textContent=sim.occupied.toLocaleString();$('energy').textContent='∑|ψ|² = '+sim.energyProxy.toFixed(9);
 $('events').textContent=sim.eventCount.toLocaleString()+' events · append-only';$('zero').textContent=sim.amplitudes.has(0)?'ANCHOR BREACH':'Complex[0] · PINNED';
 $('reverse').disabled=sim.tick===0;$('forward').disabled=sim.occupied>40000;$('cycle').disabled=sim.occupied>2000;
}
function init(){
 try{const opts=cfg(),o=+$('outer').value,i=+$('inner').value,A=+$('amplitude').value;
 if(!Number.isSafeInteger(o)||!Number.isSafeInteger(i)||o<0||i<0||o>9999||i>9999)throw new RangeError('Silo addresses must be integers 0..9999');
 const w=new WaveTensor(opts);w.seed({outer:o,inner:i},A);
 sim=w;initialEnergy=w.energyProxy;energyTrace=[initialEnergy];$('message').textContent='Ready: λ='+opts.wavelength+', amplitude='+A+', θ='+$('coupling').value+'°';
 $('pair').textContent='Tensor '+encodeTensor({outer:o,inner:i}).toLocaleString()+' · square '+o+' ↔ round '+i;
 log('Initialized '+o+'↔'+i+', energy='+initialEnergy);render();
 }catch(e){fail(e)}
}
async function forward(steps=1){if(busy)return;busy=true;
 try{for(let j=0;j<steps;j++){
  if(sim.occupied>40000)throw new RangeError('Safety cap 40,000 active amplitudes; reverse or reinitialize');
  const ev=sim.forward();energyTrace.push(ev.afterNorm);
  if(j%3===0){render();await new Promise(done=>requestAnimationFrame(done));}
 }
 log('Forward '+steps+' · tick '+sim.tick+' · active '+sim.occupied);
 $('message').textContent='Unitary model advanced '+steps+' tick(s)';
 }catch(e){fail(e)}finally{busy=false;render()}}
function reverse(){if(busy)return;try{const ev=sim.reverse();if(ev){energyTrace.push(ev.afterNorm);log('Compensating reverse · tick '+sim.tick)}render()}catch(e){fail(e)}}
function verify(){try{
 const g=parseCarrier(GLYPH);if(g.dots!==8||g.bars!==6)throw Error('Carrier mismatch');
 let max=0;for(let j=0;j<1000;j++){
 const ang=j*.019,phi=phaseAt(j,8,Math.PI/2),a=complex(Math.sin(j),Math.cos(j)),b=complex(Math.cos(j*.2),Math.sin(j*.2));
 const [a1,b1]=gate(a,b,ang,phi),[a2,b2]=gate(a1,b1,-ang,phi);
 max=Math.max(max,Math.hypot(a2.re-a.re,a2.im-a.im),Math.hypot(b2.re-b.re,b2.im-b.im));
 if(max>1e-11)throw Error('Inverse drift '+max);
 }
 if(sim.amplitudes.has(0))throw Error('Complex[0] moved');
 $('status').textContent='PASS · 1,000 gate inverses';log('Numerical gate test PASS; max drift '+max.toExponential(2));
 }catch(e){$('status').textContent='FAIL';fail(e)}}
 $('reset').onclick=init;$('forward').onclick=()=>forward(1);$('reverse').onclick=reverse;$('cycle').onclick=()=>forward(14);$('verify').onclick=verify;
 for(const id of ['wavelength','amplitude','coupling','kick'])$(id).addEventListener('input',()=>{syncLabels();drawWave();$('message').textContent='Changing a control updates preview. Initialize to apply it to the runtime.'});
 init();verify();
})();
