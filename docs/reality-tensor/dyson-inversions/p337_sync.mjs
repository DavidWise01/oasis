/** P3.37: opt-in years-per-symbolic-step scale. Not physical photon time. */
import {spinor,unspinor,bodies} from './p336_patricia_360.mjs';
import {position,angularVelocity} from './p335_galactic_motion.mjs';
export const SPEC=Object.freeze({model:'Patricia',root:0,stepsPerHop:360,hops:4,total:1440,calendarModel:'Greg separate',defaultYearsPerStep:0});
export function scale(yearsPerStep=0){if(!Number.isFinite(yearsPerStep)||yearsPerStep<0)throw new RangeError('yearsPerStep');return Object.freeze({yearsPerStep,unit:'years/symbolic step',assumed:true});}
export function at(index,config=scale(),epochYears=0){const spin=spinor(index);if(!Number.isFinite(epochYears))throw new RangeError('epochYears');const years=epochYears+index*config.yearsPerStep;return {root:[0,0,0],spinor:spin,elapsedYears:years,bodies:bodies().map(b=>({id:b.id,kind:b.kind,xyz:position(b,years)}))};}
export function reverseCoordinate(b,fromYears,toYears){if(!Number.isFinite(fromYears)||!Number.isFinite(toYears))throw new RangeError('time');const xyz=position(b,fromYears),a=angularVelocity(b)*(toYears-fromYears),c=Math.cos(a),s=Math.sin(a);return [c*xyz[0]-s*xyz[1],s*xyz[0]+c*xyz[1],xyz[2]];}
export function recoverIndex(hop,step){return unspinor(hop,step);}
