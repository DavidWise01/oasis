/** P3.29: toroidal orientation double-cover; seam at 183 deg by model convention. */
export const SEAM_DEG=183, PERIOD_DEG=360, ORIENTATION_PERIOD_DEG=720;
const mod=(n,m)=>((n%m)+m)%m;
export function state(liftDeg,initialSign=-1){
 if(!Number.isFinite(liftDeg)||![-1,1].includes(initialSign))throw new RangeError('angle/sign');
 const winding=Math.floor((liftDeg-SEAM_DEG)/PERIOD_DEG)+1;
 return {liftDeg,angleDeg:mod(liftDeg,360),winding,sign:Math.abs(winding)%2===0?initialSign:-initialSign};
}
export function traverse(start,delta,initialSign=-1){
 if(!Number.isFinite(delta))throw new RangeError('delta');
 const before=state(start,initialSign),after=state(start+delta,initialSign);
 return {before,after,crossings:Math.abs(after.winding-before.winding),flipped:before.sign!==after.sign};
}
export function outerPoint(deg,R=2,r=1){
 if(!Number.isFinite(R)||!Number.isFinite(r)||!(R>r&&r>0))throw new RangeError('radii');
 const a=mod(deg,360)*Math.PI/180;return [(R+r)*Math.cos(a),(R+r)*Math.sin(a),0];
}
export const audit=()=>({seam:183,at182:state(182),at183:state(183),at184:state(184),oneTurn:traverse(0,360),twoTurns:traverse(0,720)});
