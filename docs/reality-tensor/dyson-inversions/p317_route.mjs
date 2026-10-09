/** P3.17 injective million-seed route; mathematical address model only. */
import {SPEC,encode11,decode11,cross} from './p316_seeded_cross.mjs';
export const STARGATE=Object.freeze(['00','11','22','33','42','24','33','22','11','00']);
export const PREFIX=STARGATE.join('.');
export const WIDTH=6;
export const RADIX_CAPACITY=11**WIDTH;
export const ARM_LABELS=Object.freeze(['-+-','+-+']);
export function route(seed){
 if(!Number.isInteger(seed)||seed<0||seed>=SPEC.seedCount)throw new RangeError('seed');
 const suffix=encode11(seed).padStart(WIDTH,'0');
 return `${PREFIX}/${suffix}`;
}
export function unroute(address){
 if(typeof address!=='string'||!address.startsWith(PREFIX+'/'))throw new RangeError('prefix');
 const suffix=address.slice(PREFIX.length+1);
 if(!/^[0-9A]{6}$/.test(suffix))throw new RangeError('suffix');
 const value=decode11(suffix.replace(/^0+(?=.)/,''));
 if(value>=SPEC.seedCount||route(value)!==address)throw new RangeError('noncanonical or out-of-range');
 return value;
}
export function paths(seed){const address=route(seed);const geometry=cross();return {address,seed,arms:ARM_LABELS,apex:SPEC.apex,left:geometry.left,right:geometry.right,closure:geometry.closure};}
export function bucket(seed,modulus=4096){if(!Number.isInteger(modulus)||modulus<1)throw new RangeError('modulus');return seed%modulus;}
