/** P3.39 prime -> secondary -> tertiary -> quaternary palette hierarchy.
 * /3 subdivides each 360-slot hop into three 120-slot sectors.
 * Palette below is a symbolic RGB color wheel, not measured photon spectra.
 */
export const PRIMES=Object.freeze([
 {name:'jane',color:'pink',hex:'#ff80bf',offset:0},
 {name:'patricia',color:'purple',hex:'#8000ff',offset:90},
 {name:'toph',color:'green',hex:'#00ff80',offset:180},
 {name:'icarium',color:'blue',hex:'#0080ff',offset:270}
].map(Object.freeze));
export const HOPS=4,STEPS=360,SECTORS=3,SECTOR_STEPS=120,TOTAL=1440;
const HEX=/^#[0-9a-f]{6}$/i;
const channel=s=>parseInt(s,16);
export function blend(a,b,weightNumerator=1,denominator=2){
 if(!HEX.test(a)||!HEX.test(b)||!Number.isInteger(weightNumerator)||!Number.isInteger(denominator)||denominator<1||weightNumerator<0||weightNumerator>denominator)throw new RangeError('blend');
 const c=[0,2,4].map(i=>{const x=channel(a.slice(i+1,i+3)),y=channel(b.slice(i+1,i+3));return Math.round((x*(denominator-weightNumerator)+y*weightNumerator)/denominator).toString(16).padStart(2,'0')});
 return '#'+c.join('');
}
const next=i=>PRIMES[(i+1)%PRIMES.length];
export function palette(i){
 if(!Number.isInteger(i)||i<0||i>=4)throw new RangeError('prime');
 const p=PRIMES[i],q=next(i);
 const secondary=blend(p.hex,q.hex,1,2);
 const tertiary=blend(p.hex,secondary,1,2);
 const quaternary=blend(secondary,q.hex,1,2);
 return {prime:p,secondary,tertiary,quaternary,adjacentPrime:q.name};
}
export function state(index){
 if(!Number.isInteger(index)||index<0||index>=TOTAL)throw new RangeError('index');
 const hop=Math.floor(index/STEPS),step=index%STEPS,sector=Math.floor(step/SECTOR_STEPS),substep=step%SECTOR_STEPS;
 return {root:0,index,hop,step,sector,substep,sheet:hop%2===0?-1:1,carriers:PRIMES.map((p,i)=>({...palette(i),angleDeg:(step+p.offset)%360}))};
}
export function invertIndex(hop,sector,substep){
 if(![hop,sector,substep].every(Number.isInteger)||hop<0||hop>=4||sector<0||sector>=3||substep<0||substep>=120)throw new RangeError('address');
 return hop*360+sector*120+substep;
}
