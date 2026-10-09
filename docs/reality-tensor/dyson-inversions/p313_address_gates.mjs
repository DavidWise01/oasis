/** P3.13: test convention for mapping ten address tokens to reversible gates.
 * This is a symbolic unitary scattering map, not a physical transport law.
 */
export const ADDRESS=Object.freeze(['00','11','22','33','42','24','33','22','11','00']);
export const DIMENSIONS=Object.freeze(['-1+','-2+','-3+']);
export const QUADS='AaBbCcDd', TOPOLOGY='{-{d}+{+{d}-}}';
const sq=z=>z[0]*z[0]+z[1]*z[1];
export const norm=s=>s.reduce((v,z)=>v+sq(z),0);
export const initial=()=>[[1,0],[0,0],[0,0]];
const multiply=(a,b)=>[a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]];
function valid(s){if(!Array.isArray(s)||s.length!==3||!s.every(z=>Array.isArray(z)&&z.length===2&&z.every(Number.isFinite)))throw new TypeError('3 complex channels required');}
export function gates(address=ADDRESS){
 if(!Array.isArray(address)||address.length!==10||address.some(x=>typeof x!=='string'||!/^\d{2}$/.test(x)))throw new RangeError('address');
 return address.map((token,step)=>{
  const a=+token[0],b=+token[1],id=1+((a+b+step)%2),eta=((a+1)*(b+1))/100,phase=(a-b)*Math.PI/12;
  if(eta>1)throw new RangeError('coupling');
  return Object.freeze({token,step,id,eta,phase,dimension:DIMENSIONS[step%3],quad:QUADS[step%8]});
 });
}
function apply(s,g,inverse=false){
 valid(s);const v=s.map(z=>z.slice()),a=v[0],b=v[g.id],t=Math.sqrt(1-g.eta),r=Math.sqrt(g.eta),p=[Math.cos(g.phase),Math.sin(g.phase)];
 if(inverse){
  const x=[t*a[0]+r*b[1],t*a[1]-r*b[0]],y=[t*b[0]+r*a[1],t*b[1]-r*a[0]];
  v[0]=multiply(x,[p[0],-p[1]]);v[g.id]=y;
 }else{
  const x=multiply(a,p);
  v[0]=[t*x[0]-r*b[1],t*x[1]+r*b[0]];
  v[g.id]=[t*b[0]-r*x[1],t*b[1]+r*x[0]];
 }
 return v;
}
export function forward(s=initial(),address=ADDRESS){let state=s;for(const g of gates(address))state=apply(state,g);return state;}
export function backward(s,address=ADDRESS){let state=s;for(const g of gates(address).reverse())state=apply(state,g,true);return state;}
export const conjugatePalindrome=a=>a.every((x,i)=>x===a[a.length-1-i].split('').reverse().join(''));
