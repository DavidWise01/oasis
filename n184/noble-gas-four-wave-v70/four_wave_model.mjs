/**
 * N184 noble-gas four-wave exploratory overlay.
 * Idealized, linear, scalar field; emission wavelengths are representative NIST lines,
 * not experimentally measured emission amplitudes or a material response model.
 * Source references: https://physics.nist.gov/PhysRefData/Handbook/Tables/heliumtable2.htm
 * https://physics.nist.gov/cgi-bin/ASD/lines1.pl (Ne I 585.24878 nm)
 * https://physics.nist.gov/PhysRefData/Handbook/Tables/argontable2.htm
 * https://physics.nist.gov/PhysRefData/Handbook/Tables/kryptontable2.htm
 * Immutable upstream N184 and OASIS carrier modules are not changed.
 */
export const REFERENCE_NM = 585.24878;
export const GASES = Object.freeze([
  Object.freeze({symbol:'He',name:'Helium',Z:2,nm:587.56148,color:'#ffca79',dir:[0,-1],label:'He I'}),
  Object.freeze({symbol:'Ne',name:'Neon',Z:10,nm:585.24878,color:'#ff6678',dir:[1,0],label:'Ne I'}),
  Object.freeze({symbol:'Ar',name:'Argon',Z:18,nm:696.5431,color:'#88a7ff',dir:[0,1],label:'Ar I'}),
  Object.freeze({symbol:'Kr',name:'Krypton',Z:36,nm:760.15457,color:'#9fe6db',dir:[-1,0],label:'Kr I'})
]);
export const FOURTH_DIRECTION = Object.freeze([-1,0]);
export const MODES = Object.freeze(['cancel','reinforce','krypton']);
export const DEFAULTS = Object.freeze({mode:'cancel',phaseDeg:0,reflectivity:0.3,drive:1});
export function validate(p={}) {
  const out={...DEFAULTS,...p};
  if(!MODES.includes(out.mode))throw new RangeError('mode');
  for(const k of ['phaseDeg','reflectivity','drive'])if(!Number.isFinite(out[k]))throw new RangeError(k);
  if(out.reflectivity<0||out.reflectivity>1||out.drive<0||out.drive>4)throw new RangeError('scale');
  return out;
}
export function frequencyRatio(gas){return REFERENCE_NM/gas.nm;}
export function baseComponent(gasIndex,x,y,t,p=DEFAULTS,direction=null) {
  const v=validate(p),gas=GASES[gasIndex],dir=direction||gas.dir;
  if(!gas||![x,y,t].every(Number.isFinite))throw new RangeError('input');
  const omega=2*Math.PI*frequencyRatio(gas);
  const spatial=3*(dir[0]*x+dir[1]*y); // x,y measured in synthetic spatial cycles
  return (v.drive/3)*(1-v.reflectivity)*Math.cos(omega*(t-spatial));
}
export function fieldAt(x,y,t,params={}) {
  const p=validate(params);
  const incoming=[0,1,2].map(i=>baseComponent(i,x,y,t,p));
  const firstThree=incoming.reduce((a,b)=>a+b,0);
  const extra=p.phaseDeg*Math.PI/180;
  let fourth=0;
  if(p.mode==='krypton') {
    const kr=GASES[3],phase=2*Math.PI*frequencyRatio(kr)*(t-3*(FOURTH_DIRECTION[0]*x+FOURTH_DIRECTION[1]*y));
    fourth=(p.drive/3)*(1-p.reflectivity)*Math.cos(phase+extra);
  } else {
    const sign=p.mode==='cancel'?-1:1;
    // Engineered fourth channel is a THREE-FREQUENCY waveform, NOT krypton emission.
    fourth=sign*[0,1,2].reduce((sum,i)=>{
      const gas=GASES[i],phase=2*Math.PI*frequencyRatio(gas)*(t-3*(FOURTH_DIRECTION[0]*x+FOURTH_DIRECTION[1]*y));
      return sum+(p.drive/3)*(1-p.reflectivity)*Math.cos(phase+extra);
    },0);
  }
  return {incoming,firstThree,fourth,total:firstThree+fourth};
}
export function monitor(params={},samples=768,cycles=12) {
  const p=validate(params);
  if(!Number.isInteger(samples)||samples<8||samples>30000||!Number.isFinite(cycles)||cycles<=0)throw new RangeError('sampling');
  const dt=cycles/samples;
  let sumSq=0,peak=0,sumPolSq=0,x=0,velocity=0;
  const resonance=2*Math.PI, damping=0.16;
  const history=[];
  // Semi-implicit Euler on dimensionless illustrative polarization coordinate.
  // Small-step integration; this is not an Ice IX material-parameter prediction.
  for(let k=0;k<samples;k++){
    const t=k*dt,e=fieldAt(0,0,t,p),forcing=e.total;
    const acc=resonance*resonance*(forcing-x)-2*damping*resonance*velocity;
    velocity+=dt*acc; x+=dt*velocity;
    sumSq+=forcing*forcing;peak=Math.max(peak,Math.abs(forcing));
    sumPolSq+=x*x;
    history.push({t,firstThree:e.firstThree,fourth:e.fourth,total:e.total,polarization:x});
  }
  return {rms:Math.sqrt(sumSq/samples),peak,polarizationRms:Math.sqrt(sumPolSq/samples),history};
}
