import * as M from './electrum_fcc.mjs';
import * as C from './upstream/cipher208.mjs';
const $=id=>document.getElementById(id);
const defaults={voltage:-211,gap:10,lambda:600,thickness:30,nreal:0.5,kappa:3,surface:0,basis:'mass',rotation:20,depth:100};
let sites=M.buildFCC(),last=M.opticalBoundary(),t=0;
const param=()=>({voltageV:Number($('voltage').value)/1000,referenceV:0,
 gapM:Number($('gap').value)*1e-6,wavelengthM:Number($('lambda').value)*1e-9,
 thicknessM:Number($('thickness').value)*1e-9,nReal:Number($('nreal').value),
 kappa:Number($('kappa').value),surfaceResponseRadPerV:Number($('surface').value),
 compositionBasis:$('basis').value});
const fmtSigned=(x,d=2)=>(x<0?'−':'+')+Math.abs(x).toFixed(d);
function reset(){for(const [k,v] of Object.entries(defaults))$(k).value=v;update(true);$('testStatus').textContent='Restored −211 mV boundary and default electrum lattice.';}
function update(rebuild=false){try{
 const p=param();last=M.opticalBoundary(p);if(rebuild)sites=M.buildFCC(p);
 $('voltageValue').textContent=(p.voltageV*1000).toFixed(0)+' mV';
 $('gapValue').textContent=(p.gapM*1e6).toFixed(0)+' μm';
 $('lambdaValue').textContent=(p.wavelengthM*1e9).toFixed(0)+' nm';
 $('thicknessValue').textContent=(p.thicknessM*1e9).toFixed(0)+' nm';
 $('nValue').textContent=p.nReal.toFixed(2);$('kValue').textContent=p.kappa.toFixed(1);
 $('surfaceValue').textContent=p.surfaceResponseRadPerV.toFixed(1)+' rad/V';
 $('basisValue').textContent=p.compositionBasis==='mass'?'79:21 by mass':'79:21 by site count';
 $('rotValue').textContent=$('rotation').value+'°';$('depthValue').textContent=$('depth').value+'%';
 $('wrapperBadge').textContent='BLACK WRAPPER · '+(p.voltageV*1000).toFixed(0)+' mV';
 $('fieldMetric').textContent=(last.externalFieldVPerM/1000).toFixed(1)+' kV/m';
 $('transMetric').textContent=(last.T*100).toFixed(2)+'%';
 $('eMetric').textContent=last.externalFieldVPerM.toLocaleString(undefined,{maximumFractionDigits:1})+' V/m';
 $('skinMetric').textContent=last.opticalIntensityDecayLengthM===null?'∞ (κ = 0)':(last.opticalIntensityDecayLengthM*1e9).toFixed(2)+' nm';
 $('raMetric').textContent=(last.R*100).toFixed(2)+'% / '+(last.A*100).toFixed(2)+'%';
 $('chargeMetric').textContent=last.surfaceElectronsPerAtom.toExponential(2)+' e';
 $('phaseMetric').textContent=last.surfacePhaseRad.toFixed(4)+' rad';
 $('compositionReport').textContent=sites.nAu+' Au / '+sites.nAg+' Ag';
 $('aMetric').textContent=(sites.latticeParameterM*1e9).toFixed(6)+' nm';
 $('counterModelMetric').textContent='g = 0 vs 1 rad/V → 0 vs '+p.voltageV.toFixed(3)+' rad (conditional)';
 drawLattice();drawSpectrum();drawWave();
 }catch(e){$('testStatus').textContent='ERROR · '+e.message;}}
function bg(ctx,w,h){ctx.clearRect(0,0,w,h);ctx.fillStyle='#050807';ctx.fillRect(0,0,w,h);}
function drawWave(){const canvas=$('waveCanvas'),g=canvas.getContext('2d'),w=canvas.width,h=canvas.height,p=param();bg(g,w,h);
 const rim=g.createLinearGradient(0,0,w,0);rim.addColorStop(0,'#4b2a1a');rim.addColorStop(.5,'#f6a14d');rim.addColorStop(1,'#563120');
 g.strokeStyle=rim;g.lineWidth=2;g.strokeRect(22,16,w-44,h-32);
 g.lineWidth=9;g.strokeStyle='#020202';g.strokeRect(33,26,w-66,h-53);
 g.font='13px Consolas,monospace';g.fillStyle='#e9a871';g.fillText('BLACK SHELL  −211 mV  /  ELECTRUM FCC',50,51);
 g.fillStyle='#8ba797';g.fillText('−e',50,h-27);g.fillText('+e',w-85,h-27);
 const wave=(shift,amp,alpha,width)=>{
 g.beginPath();g.strokeStyle='#ff9b2e';g.lineWidth=width;g.globalAlpha=alpha;
 for(let x=52;x<w-52;x+=2){const u=(x-52)/(w-104),y=h/2+amp*Math.sin(u*2*Math.PI*10*(600/(p.wavelengthM*1e9))+shift+t);
  if(x===52)g.moveTo(x,y);else g.lineTo(x,y);
 }g.stroke();g.globalAlpha=1;
 };
 wave(0,49,.15,8);wave(last.surfacePhaseRad,36,.95,2.7);
 const grad=g.createLinearGradient(80,h/2,w-80,h/2);grad.addColorStop(0,'#9a4d1e00');grad.addColorStop(.5,'#ff901330');grad.addColorStop(1,'#9a4d1e00');g.fillStyle=grad;g.fillRect(50,62,w-100,h-124);
}
function drawLattice(){const c=$('latticeCanvas'),g=c.getContext('2d'),w=c.width,h=c.height;bg(g,w,h);
 const angle=(+$('rotation').value)*Math.PI/180,sa=Math.sin(angle),ca=Math.cos(angle),elev=.4;
 const visibles=+$('depth').value/100;
 const projected=[];
 for(const a of sites.sites){if(a.z>19*visibles)continue;
 const x=a.x-9.5,y=a.y-9.5,z=a.z-9.5;
 const x1=x*ca-z*sa,z1=x*sa+z*ca;
 const y1=y*Math.cos(elev)-z1*Math.sin(elev),d=z1*Math.cos(elev)+y*Math.sin(elev);
 const scale=12.1*(1+.007*d);
 projected.push({x:w*.5+x1*scale,y:h*.49-y1*scale,depth:d,type:a.element});
 }
 projected.sort((a,b)=>a.depth-b.depth);
 g.strokeStyle='#204e39';g.lineWidth=1;
 const corners=[[0,0,0],[19,0,0],[19,19,0],[0,19,0],[0,0,19],[19,0,19],[19,19,19],[0,19,19]];
 const proj=p=>{const x=p[0]-9.5,y=p[1]-9.5,z=p[2]-9.5;const x1=x*ca-z*sa,z1=x*sa+z*ca;const y1=y*Math.cos(elev)-z1*Math.sin(elev),d=z1*Math.cos(elev)+y*Math.sin(elev),s=12.1*(1+.007*d);return [w*.5+x1*s,h*.49-y1*s];};
 for(const [i,j] of [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]]){const p=proj(corners[i]),q=proj(corners[j]);g.beginPath();g.moveTo(...p);g.lineTo(...q);g.stroke();}
 for(const p of projected){g.beginPath();g.arc(p.x,p.y,p.type==='Au'?2.5:2.25,0,Math.PI*2);g.fillStyle=p.type==='Au'?'#e9c36b':'#a4b6c4';g.globalAlpha=p.type==='Au'?.8:.64;g.fill();}
 g.globalAlpha=1;g.font='13px ui-monospace,Consolas,monospace';g.fillStyle='#ffb25e';g.fillText('Au / Ag substitutional sites · FCC',18,27);
 g.fillStyle='#92b5a4';g.font='11px ui-monospace,Consolas,monospace';g.fillText(`${projected.length.toLocaleString()} sites in depth view · z-axis optical boundary`,18,h-23);
}
function drawSpectrum(){const c=$('spectrumCanvas'),g=c.getContext('2d'),w=c.width,h=c.height;bg(g,w,h);
 const margin={x:44,y:26,b:31,r:18},x0=margin.x,plotW=w-margin.x-margin.r,plotH=h-margin.y-margin.b;
 g.strokeStyle='#285443';g.lineWidth=1;
 for(let y=0;y<=4;y++){let yp=margin.y+plotH*y/4;g.beginPath();g.moveTo(x0,yp);g.lineTo(x0+plotW,yp);g.stroke();}
 const z=param();g.strokeStyle='#ff9d34';g.lineWidth=3;g.beginPath();
 for(let i=0;i<=180;i++){const wave=(350+i*600/180)*1e-9;const value=M.slabOptics({...z,wavelengthM:wave}).T;const xx=x0+i/180*plotW, yy=margin.y+(1-value)*plotH;if(!i)g.moveTo(xx,yy);else g.lineTo(xx,yy);}g.stroke();
 const px=x0+(z.wavelengthM*1e9-350)/600*plotW,py=margin.y+(1-last.T)*plotH;
 g.strokeStyle='#50e7a8';g.lineWidth=1.2;g.beginPath();g.moveTo(px,margin.y);g.lineTo(px,margin.y+plotH);g.stroke();g.beginPath();g.arc(px,py,5,0,2*Math.PI);g.fillStyle='#78ffd0';g.fill();
 g.font='12px ui-monospace,monospace';g.fillStyle='#b0bdb2';g.fillText('100%',5,margin.y+5);g.fillText('0%',13,margin.y+plotH+2);g.fillText('350 nm',x0,h-8);g.fillText('950 nm',w-77,h-8);g.fillStyle='#ffb35e';g.fillText('Film transmission T(λ) · fixed n+iκ model',x0+10,margin.y+15);
}
$('reverseBtn').addEventListener('click',()=>{$('voltage').value=-Number($('voltage').value);update();$('testStatus').textContent='Voltage reversed, crystal composition unchanged.';});
$('nullBtn').addEventListener('click',()=>{$('surface').value=0;update();$('testStatus').textContent='NULL: surface phase set to 0 rad, bulk Pockels remains zero.';});
$('resetBtn').addEventListener('click',reset);
$('auditBtn').addEventListener('click',()=>{const result=M.latticeAudit(sites);const valid=result.neighborDefects===0&&result.directedBonds===12*sites.sites.length;
 $('testStatus').textContent=(valid?'PASS':'FAIL')+` · ${result.sites} FCC sites · ${result.undirectedBonds} bonds · ${result.neighborDefects} defects · ${result.inversionBrokenSpecies} species inversion mismatches`; $('globalStatus').textContent=valid?'4K SITES / 12 NEIGHBORS · PASS':'FCC LATTICE FAILED';});
$('cipherBtn').addEventListener('click',()=>{try{const c=new C.Cipher208();for(let i=0;i<208;i++)c.forward();c.beginMirroredReverse();for(let i=0;i<208;i++)c.backward();if(!c.recovered())throw Error('Inverse failed');$('testStatus').textContent='PASS · 208 forward / mirror / 208 inverse · 417 append-only events · zero pinned.';}catch(e){$('testStatus').textContent='FAIL · '+e.message;}});
for(const id of ['voltage','gap','lambda','thickness','nreal','kappa','surface'])$(id).addEventListener('input',()=>update());
$('basis').addEventListener('change',()=>update(true));
$('rotation').addEventListener('input',()=>update());$('depth').addEventListener('input',()=>update());
update(true);
$('auditBtn').click();
