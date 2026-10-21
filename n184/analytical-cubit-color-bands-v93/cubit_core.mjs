// OASIS N184 v9.3 — strict lossless seven-packet, eighteen-site analytical cubit.
// The 7 ROYGBIV-style display bands and W/M/S lanes are symbolic; no physical
// particle, force, wavelength, or CERN detector measurement is asserted.
import {STR,hueAt,swatch,hueCount} from '../generational-color-lattice-v91/color_core.mjs';
import {createColorRecord,observeAll,evaluateQuorum,injectReportFaults} from '../quad-spectral-witness-v92/witness_core.mjs';

export const CUBIT= '{|12|}{|3456|}{|78|}{|910|}{|1112131415||}{|1617|}{|18|}';
export const BAND_NAMES=Object.freeze(['Red','Orange','Yellow','Green','Blue','Indigo','Violet']);
export const BAND_CONFIG=Object.freeze([
 Object.freeze({id:'A',name:'Red',start:1,end:2,gen:0,index:0}),
 Object.freeze({id:'B',name:'Orange',start:3,end:6,gen:2,index:0}),
 Object.freeze({id:'C',name:'Yellow',start:7,end:8,gen:1,index:0}),
 Object.freeze({id:'D',name:'Green',start:9,end:10,gen:0,index:1}),
 Object.freeze({id:'E',name:'Blue',start:11,end:15,gen:0,index:2,dualEnd:true}),
 Object.freeze({id:'F',name:'Indigo',start:16,end:17,gen:3,index:8}),
 Object.freeze({id:'G',name:'Violet',start:18,end:18,gen:2,index:4})
]);
export const PACKET_LENGTHS=Object.freeze(BAND_CONFIG.map(b=>b.end-b.start+1));
export const SEAM_POSITION=15;
export const MICROSTEPS=240;
export const SECTORS=6;
export function strengthForPosition(n){
 if(!Number.isInteger(n)||n<1||n>18)throw RangeError('Position must be integer in 1..18');
 return STR[(n-1)%3].key;
}
export function parseCubit(raw=CUBIT){
 if(typeof raw!=='string')throw TypeError('Cubit must be literal string');
 const packets=[],regex=/\{\|([0-9]+)(\|{1,2})\}/g;
 let offset=0,idx=1,found;
 while((found=regex.exec(raw))!==null){
  if(found.index!==offset)throw Error('Unparsed content or delimiter at byte '+offset);
  if(packets.length>=BAND_CONFIG.length)throw Error('Too many cubit packets');
  const ref=BAND_CONFIG[packets.length],nums=Array.from({length:ref.end-ref.start+1},(_,i)=>ref.start+i);
  const encoded=nums.join('');
  if(found[1]!==encoded)throw Error('Packet '+(packets.length+1)+' must encode '+encoded+', got '+found[1]);
  const endPipes=ref.dualEnd?'||':'|';
  if(found[2]!==endPipes)throw Error('Packet '+(packets.length+1)+' incorrect closing ports');
  if(nums[0]!==idx)throw Error('Nonmonotonic cubit ordinal');
  packets.push(Object.freeze({number:packets.length+1,bandId:ref.id,bandName:ref.name,
   numbers:Object.freeze(nums),start:ref.start,end:ref.end,
   endPipes:found[2],dualSeam:!!ref.dualEnd,lexeme:found[0]}));
  idx=ref.end+1;offset=regex.lastIndex;
 }
 if(packets.length!==7||offset!==raw.length||idx!==19)
  throw Error('Expected seven consecutive packets, exactly positions 1..18');
 if(raw!==CUBIT)throw Error('Noncanonical cubit literal');
 return Object.freeze(packets);
}
export function serializePackets(packets){
 if(!Array.isArray(packets)||packets.length!==7)throw TypeError('Seven packets required');
 return packets.map(p=>'{|'+p.numbers.join('')+p.endPipes+'}').join('');
}
export function slotAt(n){
 const strength=strengthForPosition(n),band=BAND_CONFIG.find(x=>n>=x.start&&n<=x.end);
 const record=createColorRecord(band.gen,band.index,strength),s=record.value;
 const tick=Math.floor((n-1)*MICROSTEPS/18);
 return Object.freeze({position:n,bandIndex:BAND_CONFIG.indexOf(band)+1,
  bandId:band.id,bandName:band.name,bandStart:band.start,bandEnd:band.end,
  localIndex:n-band.start,slotsInBand:band.end-band.start+1,
  hueGeneration:band.gen,hueIndex:band.index,hueDegrees:s.hueDegrees,
  strength,strengthName:s.strengthName,amplitude:s.amplitude,
  displayHex:s.displayHex,sourceRegistryAddress:s.registryAddress,
  sourceRegistryOrbit:s.registryOrbit,sourcePreviewHex:s.registryPreviewHex,
  dualSeamAfter:n===SEAM_POSITION,
  terminal:n===18,
  tick,phaseStep:Math.floor(tick/3),sector:Math.floor(tick/40),
  tickExactNumerator:(n-1)*MICROSTEPS,tickExactDenominator:18,
  // Source color can repeat: position remains a unique part of cubit identity.
  slotKey:'n'+n+'|'+record.identityKey,
  colorRecord:record});
}
export function compileCubit(raw=CUBIT){
 const packets=parseCubit(raw);
 const slots=Object.freeze(Array.from({length:18},(_,i)=>slotAt(i+1)));
 const totalWMS=Object.freeze(Object.fromEntries(STR.map(s=>[s.key,slots.filter(x=>x.strength===s.key).length])));
 return Object.freeze({schema:'oasis/n184/compiled-analytical-cubit/v93',
  canonical:raw,packets,slots,packetLengths:PACKET_LENGTHS,
  slotsCount:slots.length,packetCount:packets.length,source370Readonly:true,
  seam:{after:15,packet:5,ports:2},terminal:{position:18,packet:7},
  totalWMS,quantization:'floor((position-1)*240/18) is only a diagram address, not a physical clock'});
}
export function observeSlot(n,reportFault='none'){
 const slot=slotAt(n),cleanReports=observeAll(slot.colorRecord);
 const reports=injectReportFaults(cleanReports,reportFault);
 const quorum=evaluateQuorum(reports);
 // Pinned-source comparison is a DIFFERENT check from quorum and rejects coherent
 // software vote fabrication only if the trusted canonical source is available.
 const sourceMatches=quorum.consensus&&quorum.majorityKey===slot.colorRecord.identityKey;
 return Object.freeze({slot,reports,quorum,sourceMatches,reportFault,
  acceptedWithPinnedSource:quorum.consensus&&sourceMatches,
  diagnostic:'3/4 software derived reports are not independently sourced detector observations'});
}
export function compileWitnesses(raw=CUBIT){
 const cubit=compileCubit(raw),cases=cubit.slots.map(s=>observeSlot(s.position,'none'));
 const failed=cases.filter(x=>!x.acceptedWithPinnedSource||x.reports.some(r=>!r.valid));
 return Object.freeze({schema:'oasis/n184/cubit-color-witness-audit/v93',
  canonical:cubit.canonical,packetLengths:[...cubit.packetLengths],
  count:cubit.slotsCount,caseCount:cases.length,softwareWitnessReports:cases.length*4,
  fullAgree:cases.length-failed.length,failed:failed.map(x=>x.slot.position),
  strengthCounts:cubit.totalWMS,
  sourceAddressesByBand:BAND_CONFIG.map(b=>slotAt(b.start).sourceRegistryAddress)});
}
