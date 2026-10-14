import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {performance} from 'node:perf_hooks';
import {SOURCE,FIELD_SHELL,CODE,parseField,serializeField,routeIntoOBS,recoverFromOBS,alignment,verifyISO,VERSION} from './astrophage-field-v2.0.mjs';
import {I42,CANONICAL,parse,route,unroute} from './iso-graded-chain-v1.9c.mjs';
import {bindOBS,recoverOBS,packTokens,unpackTokens} from './obs-token-bus-v1.2.mjs';
import {O,B,S,encode,decode,mirror} from './obs-core-v1.1.mjs';
let assertions=0;let negatives=0;let sweeps=0;
function eq(a,b,msg){assert.deepEqual(a,b,msg);assertions++}
function ok(v,msg){assert.ok(v,msg);assertions++}
function reject(fn,msg){assert.throws(fn,undefined,msg);assertions++;negatives++}
const t0=performance.now();
const parsed=parseField(SOURCE);
eq(parsed.version,VERSION);eq(parsed.shell.upper,'UUUU');eq(parsed.shell.lower,'uuuu');eq(parsed.shell.channel,['|','|']);
eq(parsed.inputs.map(x=>x.species),['Na+','Cl-']);eq(parsed.inputs.map(x=>x.tag.wavelengthNm),[589,850]);
eq(parsed.inputs.map(x=>x.tag.visibleLabel),['#FFD42A','#2AE5D3']);
eq(parsed.output.species,'NaCl');eq(parsed.output.children[0].species,'MYCELIUM');
eq(parsed.output.children[0].children[0].species,'CYCAD');
const diatome=parsed.output.children[0].children[0].children[0];
eq(diatome.species,'DIATOME');eq(diatome.codeBinary,'10000001');eq(diatome.codeValue,129);
eq(diatome.children[0],{count:3,symbol:'BEAR'});eq(CODE,'10000001');
eq(parseInt(CODE,2),129);eq(serializeField(parsed),SOURCE);eq(FIELD_SHELL,'-+UUUU | | uuuu -+');
const iso=alignment();eq(iso.iso.originalAddresses,42);eq(iso.iso.directedTransitions,2688);eq(iso.iso.arithmeticValue,729);eq(iso.iso.identityPositions,[0,4]);
eq(iso.iso.distinctGlyphZeroAddresses,['i6:3','i7:4']);eq(iso.obs44.center,'00');eq(iso.obs44.originalIAddressForN,'i4:2');
eq(verifyISO(),2688);
const chain=parse(CANONICAL);eq(chain.identityOccurrences,[0,4]);eq(chain.edges.map(x=>x.depth),[1,2,3,4,5]);
for(const id of I42){for(let from=0;from<8;from++)for(let to=0;to<8;to++){
 const point=route(id.id,from,to);eq(unroute(point),id.id);eq(point.glyph,id.glyph);eq(point.sourceView,from);eq(point.targetView,to);sweeps++;
}}
eq(sweeps,2688);
const isoZero=I42.filter(t=>t.glyph==='0');eq(isoZero.length,2);ok(isoZero[0].id!==isoZero[1].id);
const rows=readFileSync(new URL('./OBS44-address-table.csv',import.meta.url),'utf8').trim().split(/\r?\n/);
eq(rows.length,45);const expectedLetters='nabcdefghijklmopqrstuvwxyz';
for(let i=0;i<44;i++){
 const [address,integer]=rows[i+1].split(',',2);eq(address,String(i).padStart(2,'0'));eq(integer,String(i));
}
ok(rows[1].includes(',n,0'));ok(rows[44].includes(',.0x,43'));
// Frozen code digest is pinned: this test reads, and NEVER modifies, that file.
const floorBytes=readFileSync(new URL('./frozen/dual5-floor-v0.7/dual5.mjs',import.meta.url));
const floorDigest=createHash('sha256').update(floorBytes).digest('hex');
eq(floorDigest,'47d4c89ac8155b9470852e0e23d2c059ad087eedc2b7949632a9431b5792fd4b');
// Verify full EXACT symbolic field through dual OBS coding (including × and →).
const t1=performance.now();const mapped=routeIntoOBS(SOURCE);const t2=performance.now();
eq(recoverFromOBS(mapped),SOURCE);const t3=performance.now();
eq(mapped.packet.sourceLength,mapped.byteLength);ok(mapped.byteLength>200);
eq(mapped.packet.rails.positive.length,mapped.byteLength);eq(mapped.packet.rails.negative.length,mapped.byteLength);
const a=decode(encode(12n,13n,14n));eq(a,{o:12n,b:13n,s:14n});eq(mirror(mirror(a)),a);
// Two independent source transformations need to recover exact same bytes.
const numericTokens=Array.from(new TextEncoder().encode(SOURCE),String);
eq(recoverOBS(bindOBS(numericTokens)),numericTokens);
eq(unpackTokens(packTokens(numericTokens)),numericTokens);
// More than one newline style and whitespace normalization must canonicalize.
for(let i=0;i<100;i++){
 const variant=SOURCE.split(' ').join(i%2===0?'  ':'\t').replaceAll('\n',i%3===0?'\r\n':'\n');
 eq(serializeField(parseField(variant)),SOURCE);
}
// Mutation, truncation, and forgery cases must not be accepted as canonical fields.
const incorrect=[
 SOURCE.replace('589nm','590nm'),SOURCE.replace('850nm','851nm'),SOURCE.replace('#FFD42A','#FFD42B'),
 SOURCE.replace('#2AE5D3','#2AE5D4'),SOURCE.replace('Na+','Na'),SOURCE.replace('Cl-','Cl+'),
 SOURCE.replace('NaCl','NaCI'),SOURCE.replace('MYCELIUM','MYCELLA'),SOURCE.replace('CYCAD','CYCADD'),
 SOURCE.replace('DIATOME','DIATOM'),SOURCE.replace('10000001','10000000'),
 SOURCE.replace('3×BEAR','2×BEAR'),SOURCE.replace('3×BEAR','3xBEAR'),
 SOURCE.replace('UUUU','UUuU'),SOURCE.replace('uuuu','uUUU'),
 SOURCE.replace('-+UUUU','+-UUUU'),SOURCE.replace('| |','|||'),
 SOURCE.replace('→','<-'),SOURCE.slice(0,-1),SOURCE+' TRASH',
 SOURCE.replace('MYCELIUM {','MYCELIUM'), SOURCE.replace('Na+ (589nm','Na+ (58nm'),
 SOURCE.replace('Cl- (IR teal','Cl- (IR cyan'), SOURCE.replace('3×BEAR','3×BARE'),
 ];
for(const bad of incorrect)reject(()=>parseField(bad),'reject noncanonical ASTROPHAGE input');
const mut=structuredClone(parsed);mut.output.children[0].children[0].children[0].children[0].count=4;
reject(()=>serializeField(mut),'reject modified AST');
const garbage=structuredClone(mapped);garbage.packet.rails.positive[0].s='0';reject(()=>recoverFromOBS(garbage),'reject corrupt OBS payload');
const wronglen=structuredClone(mapped);wronglen.byteLength+=1;reject(()=>recoverFromOBS(wronglen),'reject wrong byte length');
const wrongversion=structuredClone(mapped);wrongversion.version='fake';reject(()=>recoverFromOBS(wrongversion),'reject wrong envelope version');
const wrongcode=structuredClone(mapped);wrongcode.packet.rails.negative[0].o='0';reject(()=>recoverFromOBS(wrongcode),'reject modified mirror rail');
const wrongorder=structuredClone(mapped);wrongorder.packet.rails.positive.reverse();reject(()=>recoverFromOBS(wrongorder),'reject reordered rail');
const seconds=(performance.now()-t0)/1000;
console.log(JSON.stringify({status:'PASS',version:VERSION,assertions,negativeCases:negatives,viewTransitions:sweeps,
 fieldBytes:mapped.byteLength,obsCellsPerRail:mapped.packet.rails.positive.length,
 seconds:Math.round(seconds*1000)/1000,encodeMs:Math.round((t2-t1)*100)/100,recoverMs:Math.round((t3-t2)*100)/100,
 floorSourceSHA256:floorDigest,originalCoreUnchanged:true,physicalEntanglementDemonstrated:false},null,2));