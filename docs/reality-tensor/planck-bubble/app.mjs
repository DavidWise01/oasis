import * as P from './p36_planck_bubble.mjs';
import * as C from './upstream/cipher208.mjs';
const $=s=>document.getElementById(s);
const formatV=(v,n=3)=>Number.isFinite(v)?v.toExponential(n):String(v);
let cipher=new C.Cipher208();
function state(){return{depth: +$('depth').value/1000,wavelengthNm:+$('lambda').value,
  filmTransmission:+$('film').value/1000};}
function point(p,theta,r){return[p.x+r*Math.cos(theta),p.y+r*Math.sin(theta)];}
function drawBubble(p){
 const cn=$('bubble'),ctx=cn.getContext('2d'),w=cn.width,h=cn.height,c={x:w*.54,y:h*.49};
 ctx.fillStyle='#030405';ctx.fillRect(0,0,w,h);
 for(let y=0;y<h;y+=27){ctx.strokeStyle='#191b1b';ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke();}
 const rOut=185,rGray=136,rWhite=70;
 // Black potential enclosure and matte gray intermediate shell
 const outer=ctx.createRadialGradient(c.x,c.y,0,c.x,c.y,rOut+38);outer.addColorStop(0,'#38393b');outer.addColorStop(.65,'#141413');outer.addColorStop(.85,'#111315');outer.addColorStop(1,'#000');
 ctx.fillStyle=outer;ctx.beginPath();ctx.arc(c.x,c.y,rOut+17,0,Math.PI*2);ctx.fill();
 ctx.strokeStyle='#ff991b';ctx.lineWidth=5;ctx.beginPath();ctx.arc(c.x,c.y,rOut,0,Math.PI*2);ctx.stroke();
 ctx.fillStyle='#5b5b63';ctx.beginPath();ctx.arc(c.x,c.y,rGray,0,Math.PI*2);ctx.fill();
 ctx.fillStyle='#101115';ctx.beginPath();ctx.arc(c.x,c.y,rGray-18,0,Math.PI*2);ctx.fill();
 ctx.strokeStyle='#d6d8df';ctx.lineWidth=3;ctx.beginPath();ctx.arc(c.x,c.y,rWhite+17,0,Math.PI*2);ctx.stroke();
 const core=ctx.createRadialGradient(c.x-15,c.y-20,0,c.x,c.y,rWhite);core.addColorStop(0,'white');core.addColorStop(.2,'#f6f5ee');core.addColorStop(.7,'#9ca8a8');core.addColorStop(1,'#333639');
 ctx.fillStyle=core;ctx.beginPath();ctx.arc(c.x,c.y,rWhite,0,Math.PI*2);ctx.fill();
 // orange oscillating wave penetrates gradually as the display zooms (NOT literal transmission)
 const t=cipher.tick,amp=16;
 ctx.beginPath();for(let x=16;x<w-16;x++){let phase=x/44*(600/p.wavelengthNm)+t*.03;let y=c.y+amp*Math.sin(phase*2*Math.PI)*Math.min(1,1.4-p.depth*.28);if(x===16)ctx.moveTo(x,y);else ctx.lineTo(x,y);}
 ctx.strokeStyle='#ffae32';ctx.lineWidth=2.6;ctx.shadowColor='#e56618';ctx.shadowBlur=12;ctx.stroke();ctx.shadowBlur=0;
 ctx.font='bold 17px ui-monospace, monospace';ctx.fillStyle='#ffc279';ctx.fillText('−e · −211 mV',18,32);ctx.fillStyle='#d1d5dc';ctx.fillText('gray',c.x-22,c.y-rGray+31);ctx.fillStyle='#212124';ctx.fillText('white',c.x-26,c.y+8);
 ctx.fillStyle='#aeb7b3';ctx.font='13px ui-monospace,monospace';ctx.fillText('VISUAL ZOOM ≠ PHYSICAL OPTICAL TRANSPORT',22,h-20);
}
function drawCurve(p){
 const el=$('curve'),ctx=el.getContext('2d'),w=el.width,h=el.height;ctx.fillStyle='#070808';ctx.fillRect(0,0,w,h);
 const left=72,right=w-25,top=26,bottom=h-44;
 for(const ylab of [0,-25,-50,-75,-100,-125]){let yy=top+(0-ylab)/125*(bottom-top);ctx.strokeStyle='#333';ctx.beginPath();ctx.moveTo(left,yy);ctx.lineTo(right,yy);ctx.stroke();ctx.fillStyle='#bdc3be';ctx.font='12px ui-monospace,monospace';ctx.fillText(String(ylab),18,yy+4);}
 ctx.fillStyle='#e6a763';ctx.fillText('log₁₀(T) · idealized',left,15);
 const xs=[],base=10**P.logRadiusM({...p,depth:0}),pl=P.CONSTANTS.planckM;
 for(let i=0;i<=100;i++){const pp={...p,depth:i/100},q=P.theoreticalTransmission(pp);xs.push(q.log10Twhite??null);}
 ctx.strokeStyle='#ff9b2d';ctx.lineWidth=3;ctx.beginPath();let started=false;
 for(let i=0;i<=100;i++){const x=left+(right-left)*i/100;const v=xs[i];if(v===null){started=false;continue;}let y=top+Math.min(1,Math.max(0,-v/125))*(bottom-top);if(!started){ctx.moveTo(x,y);started=true}else ctx.lineTo(x,y);}
 ctx.stroke();const cx=left+(right-left)*p.depth;ctx.strokeStyle='#e8e9ee';ctx.setLineDash([4,5]);ctx.beginPath();ctx.moveTo(cx,top);ctx.lineTo(cx,bottom);ctx.stroke();ctx.setLineDash([]);
 ctx.fillStyle='#b9bfbb';ctx.fillText('initial',left,bottom+21);ctx.fillText('Planck target',right-100,bottom+21);
}
function render(){
 const p=state(),data=P.planckAudit(p);
 $('depthVal').textContent=(100*p.depth).toFixed(1)+'%';$('lambdaVal').textContent=p.wavelengthNm+' nm';$('filmVal').textContent=(100*p.filmTransmission).toFixed(2)+'%';
 $('radius').textContent=formatV(data.radiusM,2)+' m';$('tlog').textContent=data.log10Twhite===undefined?'N/A':data.log10Twhite.toFixed(2);
 $('energyRatio').textContent=formatV(data.energyRatio,2)+'×';$('tick').textContent=(cipher.mode==='backward'?416-cipher.tick:cipher.tick)+' / 416';
 $('core').textContent=data.nearPlanck?'UNKNOWN':'MODEL ONLY';$('depthMeter').style.width=(p.depth*100)+'%';
 const regime=data.domainOK?(data.radiusM<1e-9?'EXTRAPOLATION BELOW NANOMETER':'APPROXIMATION / GEOMETRY DEPENDENT'):'OUTSIDE SMALL-APERTURE APPROXIMATION';
 $('scaleDesc').textContent='Radius = '+formatV(data.radiusM)+' m. '+regime+'. Logical 0 remains fixed.';
 $('readout').textContent='Planck radius: 1.616255 × 10⁻³⁵ m\n'+
 'Optical energy: '+data.opticalEnergyEV.toFixed(5)+' eV\n'+
 'Energy at λ = ℓP (formal): '+formatV(data.energyAtPlanckEV)+' eV\n'+
 'Voltage-derived energy: 0.211 eV per elementary charge\n'+
 'Ideal aperture log₁₀(T), with film: '+(data.log10Twhite===undefined?'out of model range':data.log10Twhite.toFixed(3))+'\n'+
 'Validity at Planck scale: NOT ESTABLISHED';
 drawBubble(p);drawCurve(p);
 $('step').disabled=cipher.mode!=='forward'||cipher.tick>=208;
 $('forward').disabled=cipher.mode!=='forward'||cipher.tick>=208;
 $('flip').disabled=cipher.mode!=='forward'||cipher.tick!==208;
 $('reverse').disabled=cipher.mode!=='backward'||cipher.tick<=0;
}
function reset(){cipher=new C.Cipher208();$('result').textContent='Cipher reset. Zero pinned.';render();}
function go208(){while(cipher.tick<208)cipher.forward();render();}
$('step').onclick=()=>{cipher.forward();render();};
$('forward').onclick=()=>{go208();$('result').textContent='208 forward gates complete.'};
$('flip').onclick=()=>{cipher.beginMirroredReverse();$('result').textContent='Mirrored and inverted. Return path ready.';render();};
$('reverse').onclick=()=>{while(cipher.tick>0)cipher.backward();$('result').textContent=cipher.recovered()?'PASS: 208 inverse gates restored initial amplitudes.':'FAIL: inverse recovery mismatch';render();};
$('full').onclick=()=>{reset();go208();cipher.beginMirroredReverse();while(cipher.tick>0)cipher.backward();$('result').textContent=cipher.recovered()?'PASS: full 416-gate recovery, logical 0 held.':'FAIL';render();};
$('reset').onclick=reset;
for(const id of ['depth','lambda','film'])$(id).addEventListener('input',render);
render();
