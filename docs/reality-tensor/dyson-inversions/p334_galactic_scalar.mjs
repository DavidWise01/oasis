/** P3.34 — scale-normalized Milky Way reference at symbolic scalar 0. */
export const MODEL=Object.freeze({origin:[0,0,0],diskRadiusLy:50000,barHalfLengthLy:10000,haloRadiusLy:100000,solarRadiusLy:26000,solarOrbitYears:250000000,spinorSlotsPerHop:366,spinorHops:4,torusSides:['white','black'],branches:['-+-','+-+']});
export const PERIOD=1464;
export const majorBodies=Object.freeze([{id:'core',kind:'galactic-centre',r:0,phi:0,periodYears:null},{id:'bar-tip',kind:'bar',r:10000,phi:0,periodYears:200000000},{id:'spiral-a',kind:'spiral-reference',r:35000,phi:0.7,periodYears:300000000},{id:'spiral-b',kind:'spiral-reference',r:42000,phi:2.7,periodYears:360000000},{id:'solar-orbit',kind:'solar-orbit',r:26000,phi:0,periodYears:250000000}]);
export const minorBodies=Object.freeze([{id:'sun',kind:'star',r:26000,phi:0,periodYears:250000000},{id:'cloud-proxy',kind:'gas-cloud-reference',r:29000,phi:1.2,periodYears:275000000},{id:'cluster-proxy',kind:'cluster-reference',r:33000,phi:3.1,periodYears:310000000}]);
export function point(b,t=0){if(!Number.isFinite(t))throw new RangeError('time');const a=b.phi+(b.periodYears?2*Math.PI*t/b.periodYears:0);return [b.r*Math.cos(a),b.r*Math.sin(a),0];}
export function spinor(slot){if(!Number.isInteger(slot)||slot<0||slot>=PERIOD)throw new RangeError('slot');const hop=Math.floor(slot/366),offset=slot%366;return {slot,hop,offset,torusAngleRad:2*Math.PI*offset/366,orientation:hop%2===0?-1:1,left:hop%2===0?'-+-':'+-+',right:hop%2===0?'+-+':'-+-'};}
export function scalarState(slot,elapsedYears=0){return {root:[0,0,0],spinor:spinor(slot),major:majorBodies.map(b=>({id:b.id,xyz:point(b,elapsedYears)})),minor:minorBodies.map(b=>({id:b.id,xyz:point(b,elapsedYears)}))};}
export function normalized(b,t=0){return point(b,t).map(v=>v/MODEL.diskRadiusLy);}
