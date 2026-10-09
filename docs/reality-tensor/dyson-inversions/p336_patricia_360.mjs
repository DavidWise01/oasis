/** P3.36 Patricia has 4x360 spinor slots; Greg retains 4x366 independently. */
import {BODY,angularVelocity,position} from './p335_galactic_motion.mjs';
export const PATRICIA=Object.freeze({root:0,hops:4,stepsPerHop:360,total:1440,arms:['-+-','+-+'],torus:['white','black']});
export function spinor(index){if(!Number.isInteger(index)||index<0||index>=PATRICIA.total)throw new RangeError('index');const hop=Math.floor(index/360),step=index%360;return {index,hop,step,angleDeg:step,orientation:hop%2===0?-1:1,root:0};}
export function unspinor(hop,step){if(!Number.isInteger(hop)||hop<0||hop>=4||!Number.isInteger(step)||step<0||step>=360)throw new RangeError('hop/step');return hop*360+step;}
export function stateAt(body,years){return position(body,years);}
export function reverseBody(body,years){const omega=angularVelocity(body),p=position(body,years),c=Math.cos(-omega*years),s=Math.sin(-omega*years);return [c*p[0]-s*p[1],s*p[0]+c*p[1],p[2]];}
export function bodies(){return BODY;}
