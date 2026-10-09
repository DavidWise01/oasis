/** P3.51 exact structural envelope, separate from carrier and rotation indices. */
import {encode,decode,cell,inverseMotion} from './p350_prim_lattice.mjs';
export const TOTAL_SEQUENCE=Object.freeze([60,24,12,2,1,1,0,0]);
export const RADICES=Object.freeze(TOTAL_SEQUENCE.slice(0,6));
export const ROOT_SENTINELS=Object.freeze([0,0]);
export const ADDRESS_CAPACITY=RADICES.reduce((a,b)=>a*b,1);
export const SIGNED_CHANNELS=48,SPINOR_STEPS=1440;
export function addressOf(digits){if(!Array.isArray(digits)||digits.length!==8||digits[6]!==0||digits[7]!==0||digits.slice(0,6).some((d,i)=>!Number.isInteger(d)||d<0||d>=RADICES[i]))throw new RangeError('digits');return digits.slice(0,6).reduce((a,d,i)=>a*RADICES[i]+d,0);}
export function digitsOf(index){if(!Number.isSafeInteger(index)||index<0||index>=ADDRESS_CAPACITY)throw new RangeError('index');const out=new Array(6);for(let i=5;i>=0;i--){out[i]=index%RADICES[i];index=Math.floor(index/RADICES[i]);}return [...out,0,0];}
export function frame(depth,structureIndex,channelIndex,spinorIndex){const digits=digitsOf(structureIndex);const channel=decode(channelIndex);if(!Number.isInteger(spinorIndex)||spinorIndex<0||spinorIndex>=SPINOR_STEPS)throw new RangeError('spinor');const hop=Math.floor(spinorIndex/360),step=spinorIndex%360;return {root:0,digits,structureIndex,channelIndex,channel,spinorIndex,carrier:cell(depth,channelIndex,hop,step),whiteBlack:hop%2===0?'white':'black'};}
export function recover(f){return {structureIndex:addressOf(f.digits),channelIndex:encode(f.channel.prime,f.channel.axis,f.channel.sign),spinorIndex:inverseMotion(f.carrier.hop,f.carrier.step)};}
