import * as V from './voltage_wrapper.mjs';
import * as C from './cipher208.mjs';
const $=id=>document.getElementById(id);
const c=$('wave'),ctx=c.getContext('2d');
const timeline=$('timeline'),tctx=timeline.getContext('2d');
const params=()=>({depth:+$('depth').value/100,voltageV:V.VOLTAGE_V,dtS:+$('dt').value*1e-15,
 wavelength:+$('wavelength').value,theta:+$('theta').value,barKick:+$('kick').value});
const amplitudes=()=>[{re:+$('amplitude').value,im:0},{re:.35*(+$('amplitude').value),im:.22*(+$('amplitude').value)}];
let runtime;
function sci(v){if(v>1e-4)return(v*1e3).toPrecision(5)+' mm';if(v>1e-7)return(v*1e6).toPrecision(5)+' μm';if(v>1e-10)return(v*1e9).toPrecision(5)+' nm';return v.toExponential(4)+' m';}
const comp=z=>(z.re>=0?'':'−')+Math.abs(z.re).toFixed(3)+(z.im>=0?' + ':' − ')+Math.abs(z.im).toFixed(3)+'i';
const COLOR='#ff962e';
function paint(){
 const w=c.width,h=c.height,mid=h/2;ctx.fillStyle='#000';ctx.fillRect(0,0,w,h);
 // black body as an explicit -211mV voltage boundary, orange oscillation stays within it visually.
 const g=ctx.createLinearGradient(0,0,0,h);g.addColorStop(0,'#271007');g.addColorStop(.5,'#070505');g.addColorStop(1,'#230e06');
 ctx.fillStyle=g;ctx.fillRect(0,0,w,h);
 ctx.strokeStyle='#794321';ctx.lineWidth=1;ctx.strokeRect(10,14,w-20,h-28);
 ctx.strokeStyle='#392116';for(let y=54;y<h-10;y+=50){ctx.beginPath();ctx.moveTo(11,y);ctx.lineTo(w-11,y);ctx.stroke();}
 const p=params(),waves=p.wavelength,depth=p.depth;
 const a=runtime.field[0],b=runtime.field[1],norm=Math.sqrt(runtime.norm);
 const amp=Math.min(122,Math.max(12,112*norm/(1+norm*.25)));
 const phase=Math.atan2(a.im,a.re);
 ctx.lineWidth=3.5;ctx.strokeStyle=COLOR;ctx.shadowColor='#ff8a20';ctx.shadowBlur=16;
 ctx.beginPath();for(let x=15;x<=w-15;x++){
   const t=(x-15)/(w-30);
   // the orange field has an independently controlled waveform and display-depth scale
   const y=mid+amp*(.52*Math.sin(t*14*Math.PI/waves*8+phase)+.27*Math.sin(t*18*Math.PI/waves*8+Math.atan2(b.im,b.re)));
   x===15?ctx.moveTo(x,y):ctx.lineTo(x,y);
 }ctx.stroke();ctx.shadowBlur=0;
 ctx.fillStyle='#ff9b35';ctx.font='bold 12px ui-monospace, monospace';ctx.fillText('−211 mV  |  λ='+waves+' glyphs   |   depth '+Math.round(depth*100)+'%',25,35);
 ctx.fillStyle='#b88f73';ctx.fillText('BLACK POTENTIAL BOUNDARY / ORANGE AMPLITUDE',25,h-21);
 const tw=timeline.width,th=timeline.height;tctx.clearRect(0,0,tw,th);tctx.fillStyle='#0b0706';tctx.fillRect(0,0,tw,th);
 for(let i=0;i<208;i++){const x=i*tw/208,size=Math.max(2,tw/208-1);const present=i<runtime.tick;
  tctx.fillStyle=present?'#ffad47':C.FORWARD[i]==='.'?'#59351f':'#9a5427';tctx.fillRect(x,17,size,C.FORWARD[i]==='.'?32:53);}
 tctx.strokeStyle='#ffe0a2';tctx.beginPath();tctx.moveTo(runtime.tick*tw/208,8);tctx.lineTo(runtime.tick*tw/208,82);tctx.stroke();
}
function render(){
 const p=params();$('depthMetric').textContent=Math.round(p.depth*100)+'%';$('depthLabel').textContent=Math.round(p.depth*100)+'%';
 $('ampLabel').textContent=(+$('amplitude').value).toFixed(2);$('waveLabel').textContent=p.wavelength;
 $('thetaLabel').textContent=p.theta.toFixed(2);$('kickLabel').textContent=p.barKick.toFixed(2);
 $('dtLabel').textContent=(p.dtS/1e-15).toFixed(2);
 $('phase').textContent=Math.abs(V.signedPotentialPhase(0,p)).toFixed(6)+' rad';
 $('reference').textContent=sci(V.basePhotonEquivalentM);$('level').textContent=sci(V.zoomLengthM(p.depth,p));
 $('orders').textContent=(p.depth*V.fullZoomDecades).toFixed(2)+' / '+V.fullZoomDecades.toFixed(2);
 $('tick').textContent=runtime.tick+' / 208';$('direction').textContent=runtime.mode.toUpperCase();
 $('norm').textContent=runtime.norm.toFixed(12);$('portMinus').textContent=comp(runtime.field[0]);$('portPlus').textContent=comp(runtime.field[1]);
 $('progress').style.width=(runtime.tick/208*100)+'%';
 $('error').textContent=runtime.mode==='backward'&&runtime.tick===0?C.distance(runtime.field[0],runtime.seed[1]).toExponential(2):'—';
 $('zero').textContent='PINNED';
 $('forward').disabled=runtime.mode!=='forward'||runtime.tick===208;
 $('forwardAll').disabled=runtime.mode!=='forward'||runtime.tick===208;
 $('flip').disabled=runtime.mode!=='forward'||runtime.tick!==208;
 $('backward').disabled=runtime.mode!=='backward'||runtime.tick===0;
 $('backAll').disabled=runtime.mode!=='backward'||runtime.tick===0;
 for(const x of $('frames').children)x.classList.toggle('current',+x.dataset.frame===Math.min(15,Math.floor(runtime.tick/13)));
 paint();
}
function reset(){runtime=new V.WrappedCipher208({params:params(),amplitudes:amplitudes()});$('status').textContent='Initialized −211 mV wrapped field; forward 208 then mirror/invert 208.';render();}
for(let i=0;i<16;i++){let e=document.createElement('span');e.title='Frame '+(i+1);e.dataset.frame=String(i);$('frames').appendChild(e);}
function act(cb){try{cb();render();}catch(e){$('status').textContent='ERROR: '+e.message;}}
$('forward').onclick=()=>act(()=>{runtime.forward();});
$('forwardAll').onclick=()=>act(()=>{while(runtime.mode==='forward'&&runtime.tick<208)runtime.forward();$('status').textContent='Forward 208 complete. Mirror and invert.';});
$('flip').onclick=()=>act(()=>{runtime.flip();$('status').textContent='Mirrored, upside-down, swapped ports. Inverting 208 voltage-wrapped gates.';});
$('backward').onclick=()=>act(()=>{runtime.backward();if(runtime.recovered())$('status').textContent='PASS: original wave recovered in mirrored coordinates.';});
$('backAll').onclick=()=>act(()=>{while(runtime.mode==='backward'&&runtime.tick>0)runtime.backward();$('status').textContent=runtime.recovered()?'PASS: exact mirrored recovery within float tolerance.':'FAIL: inverse mismatch';});
$('full').onclick=()=>act(()=>{reset();while(runtime.tick<208)runtime.forward();runtime.flip();while(runtime.tick>0)runtime.backward();$('status').textContent=runtime.recovered()?'PASS: full 416-gate −211mV cycle recovered.':'FAIL: full-cycle recovery';});
$('reset').onclick=reset;
$('test').onclick=()=>act(()=>{let emax=0;for(let k=0;k<12;k++){
 const s=new V.WrappedCipher208({params:{...params(),depth:k/11,dtS:(k+1)*1e-16},amplitudes:[{re:1,im:.21},{re:.33,im:-.19}]});
 while(s.tick<208)s.forward();s.flip();while(s.tick>0)s.backward();
 if(!s.recovered())throw Error('Cycle '+k+' failed');emax=Math.max(emax,C.distance(s.field[0],s.seed[1]));}
 $('status').textContent='PASS: 12 complete voltage-wrapped 416-gate cycles, max recovery error '+emax.toExponential(2);});
for(const id of ['depth','amplitude','wavelength','theta','kick','dt'])$(id).addEventListener('input',reset);
reset();
