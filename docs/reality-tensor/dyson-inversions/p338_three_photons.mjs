/** P3.38 four concurrent symbolic carriers, scalar 0. */
export const LITERAL='{{jane::pink::patricia::purple::toph::green::icarium::blue::}}';
export const PHOTONS=Object.freeze([{name:'jane',color:'pink',offset:0},{name:'patricia',color:'purple',offset:90},{name:'toph',color:'green',offset:180},{name:'icarium',color:'blue',offset:270}].map(Object.freeze));
export const HOPS=4,STEPS_PER_HOP=360,TOTAL=1440,ROOT=0;
export function state(index){
 if(!Number.isInteger(index)||index<0||index>=TOTAL)throw new RangeError('index');
 const hop=Math.floor(index/STEPS_PER_HOP),step=index%STEPS_PER_HOP;
 return {index,hop,step,root:ROOT,carriers:PHOTONS.map(p=>({name:p.name,color:p.color,angleDeg:(step+p.offset)%360,sheet:hop%2===0?-1:1}))};
}
export function indexOf(hop,step){if(!Number.isInteger(hop)||hop<0||hop>=HOPS||!Number.isInteger(step)||step<0||step>=STEPS_PER_HOP)throw new RangeError('hop/step');return hop*STEPS_PER_HOP+step;}
export function advance(index,delta=1){if(!Number.isSafeInteger(delta))throw new RangeError('delta');return ((index+delta)%TOTAL+TOTAL)%TOTAL;}
export function audit(index){const s=state(index);return {state:s,anglesSeparated:s.carriers.every((a,i)=>s.carriers.every((b,j)=>i===j||((b.angleDeg-a.angleDeg+360)%360===((PHOTONS[j].offset-PHOTONS[i].offset+360)%360))),rootPinned:s.root===0};}
