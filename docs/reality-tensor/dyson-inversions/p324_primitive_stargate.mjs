/** P3.24 variable-size Stargate primitive: opposite parity arms, pinned root. */
export const ROOT=0,APEX='/\\',ARMS=Object.freeze(['-+-','+-+']);
export function shape(even=128,odd=127,evenSide='left'){
 if(!Number.isSafeInteger(even)||!Number.isSafeInteger(odd)||even<2||odd<1||even%2!==0||odd%2!==1||even+odd>100000)throw new RangeError('positive even/odd arms required, maximum total 100000');
 if(!['left','right'].includes(evenSide))throw new RangeError('evenSide');
 return Object.freeze({root:ROOT,apex:APEX,left:evenSide==='left'?even:odd,right:evenSide==='left'?odd:even,nonRoot:even+odd,total:even+odd+1});
}
export function stages(config=shape()){
 const counts=[config.left,config.right],steps=[];let index=0;
 // Interleave while both sides active, then finish the longer side.
 for(let local=0;local<Math.max(...counts);local++)for(let side=0;side<2;side++)if(local<counts[side]){
  index++;steps.push({index,side,arm:ARMS[side],port:side+1,theta:Math.PI*((index%11)+1)/64,phase:(index%17-8)*Math.PI/127});
 }
 return steps;
}
export const initial=()=>[[1,0],[0,0],[0,0]];
export const norm=s=>s.reduce((n,z)=>n+z[0]*z[0]+z[1]*z[1],0);
const mul=(a,b)=>[a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]];
function gate(state,g,inverse=false){
 if(!Array.isArray(state)||state.length!==3||!state.every(z=>Array.isArray(z)&&z.length===2&&z.every(Number.isFinite)))throw new TypeError('three complex ports');
 const v=state.map(z=>z.slice()),a=v[0],b=v[g.port],t=Math.cos(g.theta),r=Math.sin(g.theta),p=[Math.cos(g.phase),Math.sin(g.phase)];
 if(inverse){const x=[t*a[0]+r*b[1],t*a[1]-r*b[0]];v[g.port]=[t*b[0]+r*a[1],t*b[1]-r*a[0]];v[0]=mul(x,[p[0],-p[1]]);}
 else{const x=mul(a,p);v[0]=[t*x[0]-r*b[1],t*x[1]+r*b[0]];v[g.port]=[t*b[0]-r*x[1],t*b[1]+r*x[0]];}return v;
}
export function forward(state=initial(),config=shape()){return stages(config).reduce((s,g)=>gate(s,g),state);}
export function backward(state,config=shape()){return stages(config).reverse().reduce((s,g)=>gate(s,g,true),state);}
export function audit(config=shape()){const x=initial(),f=forward(x,config),b=backward(f,config);return {config,norm:norm(f),recovery:Math.max(...x.flatMap((z,i)=>z.map((v,k)=>Math.abs(v-b[i][k]))))};}
