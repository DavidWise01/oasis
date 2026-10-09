/** P3.32 Patricia photon primitive. Distinct from Greg's calendar clock.
 * {{ -+- : +-+ }} is a two-branch symbolic carrier with a pinned root.
 * No claim that a physical photon has internal Möbius clocks.
 */
export const PATRICIA=Object.freeze({name:'Patricia',carrier:'photon',literal:'{{ -+- : +-+ }}',root:0,left:'-+-',right:'+-+',calendarBound:false});
export const flip=s=>{if(s==='-+-')return '+-+';if(s==='+-+')return '-+-';throw new RangeError('unknown branch');};
export const pair=()=>Object.freeze([PATRICIA.left,PATRICIA.right]);
export function state(tick=0){if(!Number.isSafeInteger(tick)||tick<0)throw new RangeError('tick');const parity=tick%2;return {tick,root:0,left:parity?PATRICIA.right:PATRICIA.left,right:parity?PATRICIA.left:PATRICIA.right};}
export function forward(s){if(!s||!Number.isSafeInteger(s.tick)||s.tick<0)throw new TypeError('state');const expected=state(s.tick);if(s.left!==expected.left||s.right!==expected.right||s.root!==0)throw new RangeError('invalid state');return state(s.tick+1);}
export function backward(s){if(!s||!Number.isSafeInteger(s.tick)||s.tick<1)throw new RangeError('cannot inverse past root');const expected=state(s.tick);if(s.left!==expected.left||s.right!==expected.right||s.root!==0)throw new RangeError('invalid state');return state(s.tick-1);}
export function roundTrip(ticks){if(!Number.isSafeInteger(ticks)||ticks<0)throw new RangeError('ticks');let cur=state();for(let i=0;i<ticks;i++)cur=forward(cur);for(let i=0;i<ticks;i++)cur=backward(cur);return cur;}
