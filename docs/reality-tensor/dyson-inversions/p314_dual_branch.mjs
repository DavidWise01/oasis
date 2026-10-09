/** P3.14 paired forward arms; numerical conventions, not physical transport. */
export const LEFT='-+-',RIGHT='+-+',APEX='/\\';
export const ADDRESS=['00','11','22','33','42','24','33','22','11','00'];
const mul=(a,b)=>[a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]];
const u=t=>[Math.cos(t),Math.sin(t)];
export const norm=s=>s.reduce((v,z)=>v+z[0]**2+z[1]**2,0);
export const initial=()=>[[1,0],[0,0],[0,0]];
function gate(s,g,inverse=false){
 const o=s.map(z=>z.slice()),a=o[0],b=o[g.port],t=Math.sqrt(1-g.eta),r=Math.sqrt(g.eta);
 if(inverse){const x=[t*a[0]+r*b[1],t*a[1]-r*b[0]];o[g.port]=[t*b[0]+r*a[1],t*b[1]-r*a[0]];o[0]=mul(x,u(-g.angle));}
 else{const x=mul(a,u(g.angle));o[0]=[t*x[0]-r*b[1],t*x[1]+r*b[0]];o[g.port]=[t*b[0]-r*x[1],t*b[1]+r*x[0]];}
 return o;
}
export function compile(){return ADDRESS.flatMap((token,i)=>{
 const a=+token[0],b=+token[1],eta=(a+1)*(b+1)/100,angle=(a-b)*Math.PI/12;
 return [{arm:LEFT,step:i,token,port:1,eta,angle:angle-Math.PI/18},
 {arm:RIGHT,step:i,token:token.split('').reverse().join(''),port:2,eta,angle:-angle+Math.PI/18}];
});}
export function forward(s=initial()){return compile().reduce((x,g)=>gate(x,g),s);}
export function inverse(s){return compile().reverse().reduce((x,g)=>gate(x,g,true),s);}
export function audit(){const f=forward(),b=inverse(f),s=initial();return {events:compile().length,channels:f.map(z=>z[0]**2+z[1]**2),norm:norm(f),recovery:Math.max(...b.flatMap((z,i)=>z.map((x,j)=>Math.abs(x-s[i][j]))))};}
