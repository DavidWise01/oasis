'use strict';
/* N184 Blueprint Lab: VISUAL-ONLY math. No kernel or runtime changes. */
window.N184Geometry=(()=>{
const TAU=Math.PI*2;
const vertices=Array.from({length:16},(_,i)=>[0,1,2,3].map(k=>(i&(1<<k))?1:-1));
const edges=[];for(let i=0;i<16;i++)for(let k=0;k<4;k++){let j=i^(1<<k);if(i<j)edges.push([i,j])}
const planes=['XY','XZ','XW','YZ','YW','ZW'],axes={X:0,Y:1,Z:2,W:3};
function rotate4(point,angles){let p=point.slice();for(let i=0;i<6;i++){let a=(angles[i]||0)*Math.PI/180,k=axes[planes[i][0]],j=axes[planes[i][1]],u=p[k],v=p[j];p[k]=u*Math.cos(a)-v*Math.sin(a);p[j]=u*Math.sin(a)+v*Math.cos(a)}return p}
function projected4(p,angles,mode,dist){let q=rotate4(p,angles),factor=mode==='perspective'?dist/(dist-q[3]):1;return{x:q[0]*factor,y:q[1]*factor,z:q[2]*factor,w:q[3],q4:q}}
const scene=[];function segment(a,b,color,width=1.2,name='',four=null){scene.push({a,b,color,width,name,four})}
function frame(r,color,open=false,label=''){let v=[];for(let x of [-1,1])for(let y of [-1,1])for(let z of [-1,1])v.push([r*x,r*y,r*z]);for(let i=0;i<8;i++)for(let j=i+1;j<8;j++){let d=v[i].reduce((sum,x,k)=>sum+(x!==v[j][k]?1:0),0);if(d===1&&!(open&&v[i][1]<0&&v[j][1]<0))segment(v[i],v[j],color,1.4,label)}}
function toroid(R,r,col,name,ex=0){const major=84,minor=12;const P=(u,v)=>[(R+r*Math.cos(v))*Math.cos(u)+ex,r*Math.sin(v),(R+r*Math.cos(v))*Math.sin(u)];for(let j=0;j<minor;j++){let v=j*TAU/minor;for(let i=0;i<major;i++)segment(P(i*TAU/major,v),P((i+1)*TAU/major,v),col,.72,name)}for(let i=0;i<major;i+=7){let u=i*TAU/major;for(let j=0;j<minor;j++)segment(P(u,j*TAU/minor),P(u,(j+1)*TAU/minor),col,.6,name)}}
function linePoints(R,r,a){const n=72,p=[];for(let i=0;i<=n;i++){let t=i*TAU/n+a;p.push([(R+r*Math.cos(0))*Math.cos(t),0,(R+r*Math.cos(0))*Math.sin(t)])}return p}
function makeScene(opt){scene.length=0;const l=opt.layers,e=opt.explode||0;
if(l.outer){let pp=vertices.map(v=>projected4(v.map(x=>x*1.26),opt.angles,opt.projection,opt.distance));for(let [a,b]of edges){let A=pp[a],B=pp[b];segment([A.x,A.y,A.z],[B.x,B.y,B.z],'#79dfff',1.55,'tesseract',[vertices[a],vertices[b]])}}
if(l.inner)frame(1.08,'#d0ebfc',true,'inner hypercube');
if(l.box)frame(.44,'#c5b4f6',false,'closed box');
if(l.strong)toroid(.96,.10,'#4a9cff','strong toroid',e*.93);
if(l.medium)toroid(.72,.095,'#6bebb0','medium toroid',e*.51);
if(l.weak)toroid(.48,.085,'#ffbf71','weak toroid',e*.18);
if(l.core){segment([-.24,.36,0],[.24,-.36,0],'#fafaff',3,'X core');segment([-.36,.24,0],[.36,-.24,0],'#f7d1a2',3,'X core')}
if(l.gate){let v=[[-2,-.13,-.13],[-2,-.13,.13],[-2,.13,-.13],[-2,.13,.13],[-.44,-.13,-.13],[-.44,-.13,.13],[-.44,.13,-.13],[-.44,.13,.13]];for(let j=0;j<4;j++)segment(v[j],v[j+4],'#fff0c8',1.8,'gateway');for(let b of [0,4]){for(let [u,w]of [[0,1],[0,2],[3,1],[3,2]])segment(v[b+u],v[b+w],'#fff0c8',1.2,'gateway')}}
if(l.wiring){const pts=[[-2.2,0,0],[-1.75,0,0],[-1.1,.15,0],[-.25,.24,0],[0,0,0],[.95,.13,0],[1.43,.1,0],[2,0,0]];for(let i=0;i<pts.length-1;i++)segment(pts[i],pts[i+1],i>3?'#82eac7':'#f9ca8f',2.5,'packet wiring')}
return scene}
function sliceSegment(seg,axis,pos,thick){if(!axis||axis==='off')return [seg];let index=axes[axis],from=seg.four?seg.four[0][index]:index===3?0:seg.a[index],to=seg.four?seg.four[1][index]:index===3?0:seg.b[index],low=pos-thick/2,high=pos+thick/2,delta=to-from;
if(Math.abs(delta)<1e-10)return from>=low&&from<=high?[seg]:[];
let u=(low-from)/delta,v=(high-from)/delta,start=Math.max(0,Math.min(u,v)),end=Math.min(1,Math.max(u,v));if(start>end)return[];
let lerp=(a,b,t)=>a.map((x,i)=>x+(b[i]-x)*t);return [{...seg,a:lerp(seg.a,seg.b,start),b:lerp(seg.a,seg.b,end),color:'#d6ffff',width:Math.max(1.5,seg.width)}]}
function clip(scene,axis,pos,thick){return scene.flatMap(s=>sliceSegment(s,axis,pos,thick))}
function toScreen(p,w,h,yaw,pitch,zoom=1){let cy=Math.cos(yaw),sy=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch),x=p[0]*cy+p[2]*sy,z=-p[0]*sy+p[2]*cy,y=p[1]*cp-z*sp,k=Math.min(w,h)*.22*zoom;return [w/2+x*k,h/2-y*k,z]}
function transformAddress(address,nibble){let row=Math.floor(address/40),col=address%40;return {address:((row+7)%60)*40+((col+13)%40),nibble:(((nibble&3)<<2)|((nibble>>2)&3))^9}}
function inverseAddress(address,nibble){let row=Math.floor(address/40),col=address%40;return {address:((row+53)%60)*40+((col+27)%40),nibble:((((nibble^9)&3)<<2)|(((nibble^9)>>2)&3))}}
function validate(){if(vertices.length!==16||edges.length!==32)throw Error('tesseract topology failed');let set=new Set;for(let a=0;a<2400;a++)for(let n=0;n<16;n++){let t=transformAddress(a,n),r=inverseAddress(t.address,t.nibble),key=t.address*16+t.nibble;if(r.address!==a||r.nibble!==n||set.has(key))throw Error('mapping collision');set.add(key)}return{vertices:vertices.length,edges:edges.length,uniquePairs:set.size}}
return{vertices,edges,planes,projected4,makeScene,clip,toScreen,transformAddress,inverseAddress,validate};
})();