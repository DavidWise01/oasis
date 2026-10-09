/** P3.41 Continuous frequency addressing, with explicit physical units.
 * The four identities and symbolic 4×360 traversal are independent of frequency.
 */
export const C = 299792458;
export const PRIMES = Object.freeze([
  Object.freeze({name:'jane', color:'pink'}),
  Object.freeze({name:'patricia', color:'purple'}),
  Object.freeze({name:'toph', color:'green'}),
  Object.freeze({name:'icarium', color:'blue'})
]);
export const HOPS=4, STEPS_PER_HOP=360, TOTAL=HOPS*STEPS_PER_HOP;
export const TIERS=Object.freeze(['prime','secondary','tertiary','quaternary','{hz...}']);
export function spectral({hz,amplitude=1,phase=0,speed=C}) {
  if(![hz,amplitude,phase,speed].every(Number.isFinite)||hz<=0||speed<=0||amplitude<0)throw new RangeError('spectral parameters');
  const wavelength=speed/hz;
  if(!Number.isFinite(wavelength)||wavelength<=0)throw new RangeError('unrepresentable wavelength');
  return Object.freeze({hz,wavelengthM:wavelength,amplitude,phaseRad:phase,speedMps:speed,lambdaTimesAmplitudeM:wavelength*amplitude});
}
export function fromWavelength({wavelengthM,amplitude=1,phase=0,speed=C}){
  if(!Number.isFinite(wavelengthM)||wavelengthM<=0)throw new RangeError('wavelength');
  return spectral({hz:speed/wavelengthM,amplitude,phase,speed});
}
export function address(index,primeIndex,wave){
  if(!Number.isInteger(index)||index<0||index>=TOTAL||!Number.isInteger(primeIndex)||primeIndex<0||primeIndex>=PRIMES.length)throw new RangeError('address');
  if(!wave||!Number.isFinite(wave.hz)||wave.hz<=0)throw new RangeError('wave');
  const hop=Math.floor(index/STEPS_PER_HOP),step=index%STEPS_PER_HOP;
  return Object.freeze({root:0,prime:PRIMES[primeIndex],hop,step,sheet:hop%2===0?-1:1,spectral:wave});
}
export function inverseAddress(hop,step){
 if(!Number.isInteger(hop)||hop<0||hop>=HOPS||!Number.isInteger(step)||step<0||step>=STEPS_PER_HOP)throw new RangeError('hop/step');
 return hop*STEPS_PER_HOP+step;
}
export function phaseAt(wave,timeSeconds=0){
 if(!Number.isFinite(timeSeconds))throw new RangeError('time');
 return ((wave.phaseRad+2*Math.PI*wave.hz*timeSeconds)%(2*Math.PI)+2*Math.PI)%(2*Math.PI);
}
