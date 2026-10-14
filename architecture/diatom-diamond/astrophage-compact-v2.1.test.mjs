import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {encodeDualBytes,decodeDualBytes,encodeField,decodeField,compileMaps,crc32,properties,MAX_BYTES,HEADER_BYTES} from './astrophage-compact-v2.1.mjs';
import {SOURCE,routeIntoOBS,recoverFromOBS,parseField,verifyISO} from './astrophage-field-v2.0.mjs';
import {packTokens,transform} from './obs-token-bus-v1.2.mjs';
import {mirror,O,B,S} from './obs-core-v1.1.mjs';
let checks=0;const ok=(x)=>{assert.ok(x);checks++},eq=(x,y)=>{assert.deepEqual(x,y);checks++},throws=(f)=>{assert.throws(f);checks++};
const floor=readFileSync(new URL('./frozen/dual5-floor-v0.7/dual5.mjs',import.meta.url));
eq(createHash('sha256').update(floor).digest('hex'),'47d4c89ac8155b9470852e0e23d2c059ad087eedc2b7949632a9431b5792fd4b');
eq(verifyISO(),2688);
const compact=encodeField(SOURCE),legacy=routeIntoOBS(SOURCE);
eq(decodeField(compact),SOURCE);eq(recoverFromOBS(legacy),SOURCE);
const original=new TextEncoder().encode(SOURCE),len=original.length;
eq(compact.length,16+len*2);
const plus=transform(Array.from(original,x=>String(x)),false);
const minus=transform(Array.from(original,x=>String(x)).reverse(),true).reverse();
const wirePositive=compact.subarray(HEADER_BYTES,HEADER_BYTES+len);
const wireNegative=compact.subarray(HEADER_BYTES+len,HEADER_BYTES+2*len);
eq([...wirePositive].map(String),plus);eq([...wireNegative].map(String),minus);
eq(legacy.packet.rails.positive,packTokens(plus));
// Virtual negative OBS coordinates must reconstruct exact legacy physical wire cells.
for(let i=0;i<len;i++){
 const p=packTokens([String(wireNegative[i])])[0];const m=mirror({o:BigInt(p.o),b:BigInt(p.b),s:BigInt(p.s)});
 eq(legacy.packet.rails.negative[i],{o:m.o.toString(),b:m.b.toString(),s:m.s.toString()});
}
eq(properties().opsPerRail,60);
let seed=0xFEEDBEEF;const rnd=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed;};
for(let i=0;i<2000;i++){
 const n=i<260?i:rnd()%513,bytes=Uint8Array.from({length:n},()=>rnd()&255);
 const wire=encodeDualBytes(bytes);eq([...decodeDualBytes(wire)],[...bytes]);eq(wire.length,16+2*n);
 if(i<192){const {positive,negative}=compileMaps(n);const permPlus=transform([...bytes].map(String),false);const permMinus=transform([...bytes].map(String).reverse(),true).reverse();
  eq([...positive].map(j=>bytes[j].toString()),permPlus);eq([...negative].map(j=>bytes[j].toString()),permMinus);}
}
for(const n of [513,1024,4096,16384,65536]){const bytes=Uint8Array.from({length:n},()=>rnd()&255);eq([...decodeDualBytes(encodeDualBytes(bytes))],[...bytes]);}
for(const offset of [0,4,5,6,7,8,11,12,14,Math.floor(compact.length/2),compact.length-1]){
 const bad=Buffer.from(compact);bad[offset]^=1;throws(()=>decodeField(bad));
}
const missing=compact.subarray(0,-1);throws(()=>decodeField(missing));
const extra=Buffer.concat([compact,Buffer.from([0])]);throws(()=>decodeField(extra));
const badHdr=Buffer.from(compact);badHdr.writeUInt32BE(MAX_BYTES+1,8);throws(()=>decodeField(badHdr));
throws(()=>encodeDualBytes(Uint8Array.from({length:MAX_BYTES+1},()=>0)));
throws(()=>encodeDualBytes(['0']));throws(()=>decodeDualBytes(Buffer.alloc(7)));throws(()=>decodeField(Buffer.alloc(16)));
throws(()=>encodeField(SOURCE.replace('10000001','10000011')));
const validButDifferent=Buffer.from(compact),maps=compileMaps(len);
for(let i=0;i<len;i++)if(maps.positive[i]===0)validButDifferent[12+i]^=1;
for(let i=0;i<len;i++)if(maps.negative[i]===0)validButDifferent[12+len+i]^=1;
validButDifferent.writeUInt32BE(crc32(validButDifferent.subarray(0,-4)),validButDifferent.length-4);
// A CRC cannot authenticate: logically coherent alteration of both rails still passes generic byte recovery.
ok(!decodeDualBytes(validButDifferent).equals(Buffer.from(original)));
throws(()=>decodeField(validButDifferent)); // grammar catches field mutation
const result={status:'PASS',version:'ASTROPHAGE/compact-v2.1',assertions:checks,isoRoutes:2688,randomizedRoundTrips:2000,fullSizeMaxBytes:MAX_BYTES,legacyWireBytes:Buffer.byteLength(JSON.stringify(legacy)),compactWireBytes:compact.length,canonicalFieldBytes:len,negativeRailExactParity:true,floorPinned:true};
console.log(JSON.stringify(result,null,2));
