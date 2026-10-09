/** P3.33 Patricia symbolic spinor: gravity/time half-events make one frame.
 * This is a discrete bookkeeping model, not the standard photon spin law.
 */
export const PRIMITIVE='{{ -+- : +-+ }}';
export const HALF_UNITS=Object.freeze({gravity:-1,time:1,denominator:2});
export function frame(n=0){if(!Number.isSafeInteger(n)||n<0)throw new RangeError('frame');return {frame:n,root:0,phase:n%2,branches:n%2?['+-+','-+-']:['-+-','+-+']};}
export function compose(s=frame()){
 if(!s||!Number.isSafeInteger(s.frame)||s.frame<0||JSON.stringify(s)!==JSON.stringify(frame(s.frame)))throw new TypeError('canonical frame state');
 const gravity=-1,time=1;
 if(gravity+time!==0||Math.abs(gravity)+Math.abs(time)!==2)throw Error('half-unit invariant');
 return {next:frame(s.frame+1),events:[{type:'g',halfUnits:gravity},{type:'t',halfUnits:time}],signedNumerator:0,completedFrameNumerator:2,denominator:2};
}
export function inverse(result){if(!result?.next||!Array.isArray(result.events)||JSON.stringify(result.events)!==JSON.stringify([{type:'g',halfUnits:-1},{type:'t',halfUnits:1}])||result.next.frame<1||JSON.stringify(result.next)!==JSON.stringify(frame(result.next.frame)))throw new TypeError('invalid frame record');return frame(result.next.frame-1);}
