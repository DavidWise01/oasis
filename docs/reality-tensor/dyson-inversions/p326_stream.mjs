/** ROOT0 P3.26 streamed Stargate; no materialized gate arrays. */
export const ROOT=0,APEX='/\\',ARMS=['-+-','+-+'];
export function shape(even,odd,evenSide='left'){
 if(!Number.isSafeInteger(even)||!Number.isSafeInteger(odd)||even<2||odd<1||even%2!==0||odd%2!==1||!Number.isSafeInteger(even+odd))throw new RangeError('parity/size');
 if(!['left','right'].includes(evenSide))throw new RangeError('orientation');
 const left=evenSide==='left'?even:odd,right=evenSide==='left'?odd:even;
 return Object.freeze({left,right,total:left+right,root:ROOT});
}
export function at(g,k){
 if(!Number.isSafeInteger(k)||k<1||k>g.total)throw new RangeError('stage');
 const paired=2*Math.min(g.left,g.right),side=k<=paired?(k-1)%2:g.left>g.right?0:1;
 return {index:k,side,port:side+1,arm:ARMS[side],theta:Math.PI*((k%11)+1)/64,phase:(k%17-8)*Math.PI/127};
}
export const norm=s=>s.reduce((v,z)=>v+z[0]**2+z[1]**2,0);
const mul=(a,b)=>[a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]];
function gate(state,g,inverse){
 const o=state.map(z=>z.slice()),a=o[0],b=o[g.port],t=Math.cos(g.theta),r=Math.sin(g.theta),p=[Math.cos(g.phase),Math.sin(g.phase)];
 if(inverse){const x=[t*a[0]+r*b[1],t*a[1]-r*b[0]];o[g.port]=[t*b[0]+r*a[1],t*b[1]-r*a[0]];o[0]=mul(x,[p[0],-p[1]]);}
 else{const x=mul(a,p);o[0]=[t*x[0]-r*b[1],t*x[1]+r*b[0]];o[g.port]=[t*b[0]-r*x[1],t*b[1]+r*x[0]];}return o;
}
export function execute(state,g,inverse=false){
 if(!Array.isArray(state)||state.length!==3||!state.every(z=>Array.isArray(z)&&z.length===2&&z.every(Number.isFinite)))throw new TypeError('complex ports');
 let cur=state.map(z=>z.slice());for(let k=inverse?g.total:1;inverse?k>=1:k<=g.total;inverse?k--:k++)cur=gate(cur,at(g,k),inverse);return cur;
}
