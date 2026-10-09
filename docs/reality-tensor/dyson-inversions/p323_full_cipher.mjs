/** ROOT0 P3.23: generated reversible demonstration, 255 operations + root zero. */
export const ROOT=0,COUNT=255,TOTAL=256,ARMS=Object.freeze(['-+-','+-+']),APEX='/\\',ORIGIN='0vwxyz';
export const initial=()=>[[1,0],[0,0],[0,0]];
export const norm=s=>s.reduce((n,z)=>n+z[0]**2+z[1]**2,0);
const mul=(a,b)=>[a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]];
const rot=(z,p)=>mul(z,[Math.cos(p),Math.sin(p)]);
export const stages=()=>Array.from({length:COUNT},(_,i)=>{const index=i+1;return {index,arm:ARMS[i%2],port:1+i%2,theta:Math.PI*((index%11)+1)/64,phase:(index%17-8)*Math.PI/127};});
export function gate(state,g,inverse=false){
 if(!Array.isArray(state)||state.length!==3||!state.every(z=>Array.isArray(z)&&z.length===2&&z.every(Number.isFinite)))throw new TypeError('three complex ports');
 const s=state.map(z=>z.slice()),t=Math.cos(g.theta),r=Math.sin(g.theta),a=s[0],b=s[g.port];
 if(inverse){const z=[t*a[0]+r*b[1],t*a[1]-r*b[0]];s[g.port]=[t*b[0]+r*a[1],t*b[1]-r*a[0]];s[0]=rot(z,-g.phase);}
 else{const z=rot(a,g.phase);s[0]=[t*z[0]-r*b[1],t*z[1]+r*b[0]];s[g.port]=[t*b[0]-r*z[1],t*b[1]+r*z[0]];}
 return s;
}
export const forward=(state=initial())=>stages().reduce((s,g)=>gate(s,g),state);
export const backward=state=>stages().reverse().reduce((s,g)=>gate(s,g,true),state);
export function audit(){const source=initial(),out=forward(source),back=backward(out);return {root:ROOT,stages:COUNT,total:TOTAL,norm:norm(out),channels:out.map(z=>z[0]**2+z[1]**2),error:Math.max(...source.flatMap((z,i)=>z.map((v,j)=>Math.abs(v-back[i][j]))))};}
