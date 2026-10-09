/** P3.22 corrected full cipher count: one root + 255 non-root positions. */
export const CIPHER = Object.freeze({root:0, nonRootCount:255, totalCount:256, firstNonRoot:1, lastNonRoot:255, legacyCount:208, legacyStatus:'superseded-count-only'});
export function encodeIndex(index){if(!Number.isInteger(index)||index<0||index>=CIPHER.totalCount)throw new RangeError('cipher position');return index.toString(16).toUpperCase().padStart(2,'0');}
export function decodeIndex(text){if(typeof text!=='string'||!/^[0-9A-F]{2}$/.test(text))throw new RangeError('canonical hex index');return parseInt(text,16);}
export function forwardOrder(){return Array.from({length:CIPHER.nonRootCount},(_,i)=>i+1);}
export function inverseOrder(){return forwardOrder().reverse();}
export function verify(){const f=forwardOrder(),b=inverseOrder();return {root:CIPHER.root,nonRoot:f.length,total:f.length+1,distinct:new Set([CIPHER.root,...f]).size,roundTrip:f.every((v,i)=>v===b[b.length-1-i]),first:f[0],last:f.at(-1)};}
