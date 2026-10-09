/** P3.35 reference kinematics: units ly, years; Patricia symbolic clock is separate. */
export const PARAMETERS=Object.freeze({diskRadiusLy:50000,solarRadiusLy:26000,solarPeriodYears:250000000,innerTurnoverLy:12000,patternPeriodYears:320000000,patriciaSlots:1464});
export const BODY=Object.freeze([{id:'sun',radius:26000,phase:0,kind:'matter'},{id:'inner-star',radius:12000,phase:0.4,kind:'matter'},{id:'outer-star',radius:42000,phase:1.1,kind:'matter'},{id:'spiral-reference',radius:35000,phase:0.2,kind:'pattern'}]);
export function angularVelocity(body,p=PARAMETERS){
 const solarOmega=2*Math.PI/p.solarPeriodYears;
 if(body.kind==='pattern')return 2*Math.PI/p.patternPeriodYears;
 // Illustrative flat outer rotation curve + solid-body inner turnover.
 return solarOmega*p.solarRadiusLy/Math.max(body.radius,p.innerTurnoverLy);
}
export function position(body,years,p=PARAMETERS){if(!Number.isFinite(years))throw new RangeError('years');const angle=body.phase+angularVelocity(body,p)*years;return [body.radius*Math.cos(angle),body.radius*Math.sin(angle),0];}
export function phaseOffset(body,years,p=PARAMETERS){return angularVelocity(body,p)*years;}
export function patricia(slot){if(!Number.isSafeInteger(slot)||slot<0||slot>=PARAMETERS.patriciaSlots)throw new RangeError('slot');return {slot,hop:Math.floor(slot/366),subslot:slot%366,orientation:Math.floor(slot/366)%2===0?-1:1,root:[0,0,0]};}
