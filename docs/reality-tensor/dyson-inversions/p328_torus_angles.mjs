/** P3.28 outer-torus angular geometry; 183 degrees is NOT exponent -183. */
export const MARKER_DEG=183, NEXT_DEG=184, PERIOD_DEG=360;
export const radians=deg=>deg*Math.PI/180;
export const normalize=deg=>{if(!Number.isFinite(deg))throw new RangeError('angle');return ((deg%360)+360)%360;};
export function outerPoint(deg,R=2,r=1){
 if(![deg,R,r].every(Number.isFinite)||R<=r||r<=0)throw new RangeError('R > r > 0');
 const phi=radians(normalize(deg));return [(R+r)*Math.cos(phi),(R+r)*Math.sin(phi),0];
}
export function step(deg,delta){return normalize(deg+delta);}
export function distanceDeg(a,b){const d=normalize(b-a);return Math.min(d,360-d);}
export function audit(){const p=outerPoint(MARKER_DEG),q=outerPoint(NEXT_DEG);return {angle:MARKER_DEG,next:NEXT_DEG,offsetBeyondHalfTurn:3,remainingToFullTurn:177,points:[p,q],chord:Math.hypot(q[0]-p[0],q[1]-p[1]),closureAt184:false,restore:step(step(183,1),-1)===183};}
