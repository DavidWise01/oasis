/** P3.40 symbolic color-to-wave continuation; SI quantities explicit. */
export const C=299792458;
export const PRIME=Object.freeze([['jane','pink'],['patricia','purple'],['toph','green'],['icarium','blue']]);
export const TIERS=Object.freeze(['prime','secondary','tertiary','quaternary']);
export const HOPS=4,STEPS=360,TOTAL=HOPS*STEPS;
export function address(index,primeIndex,tierIndex){
 if(!Number.isInteger(index)||index<0||index>=TOTAL)throw new RangeError('index');
 if(!Number.isInteger(primeIndex)||primeIndex<0||primeIndex>=PRIME.length)throw new RangeError('primeIndex');
 if(!Number.isInteger(tierIndex)||tierIndex<0||tierIndex>=TIERS.length)throw new RangeError('tierIndex');
 return {index,hop:Math.floor(index/STEPS),step:index%STEPS,root:0,prime:PRIME[primeIndex][0],color:PRIME[primeIndex][1],tier:TIERS[tierIndex]};
}
export function spectralTail({wavelengthM,amplitude,phaseRad=0,propagationSpeedMps=C}){
 if(!Number.isFinite(wavelengthM)||wavelengthM<=0||!Number.isFinite(amplitude)||amplitude<0||!Number.isFinite(phaseRad)||!Number.isFinite(propagationSpeedMps)||propagationSpeedMps<=0)throw new RangeError('wave parameters');
 const hz=propagationSpeedMps/wavelengthM;
 if(!Number.isFinite(hz)||hz<=0)throw new RangeError('frequency overflow');
 return {namespace:'{hz...}',wavelengthM,amplitude,phaseRad,hz,wavelengthTimesAmplitude:wavelengthM*amplitude,amplitudeUnit:'dimensionless normalized',productUnit:'m',phaseUnit:'rad'};
}
export function sample(wave,timeSeconds,xM=0){
 if(!Number.isFinite(timeSeconds)||!Number.isFinite(xM))throw new RangeError('sample');
 return wave.amplitude*Math.sin(2*Math.PI*(wave.hz*timeSeconds-xM/wave.wavelengthM)+wave.phaseRad);
}
export function invertFrequency(hz,speed=C){if(!Number.isFinite(hz)||hz<=0||!Number.isFinite(speed)||speed<=0)throw new RangeError('hz');return speed/hz;}
