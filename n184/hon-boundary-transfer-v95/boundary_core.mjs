// OASIS v9.5: fixed 3 gate, 5 operant boundary simulator.
// All operations act on symbolic HSV display swatches; no physical conservation law claimed.
import {ROOTS,OPERANTS,addressColor,operateColor,ROOT_CAPACITY,SOURCE_TAIL,cubitToHON} from '../elemental-hon-color-operants-v94/hon_core.mjs';
export const GATES=Object.freeze([
 Object.freeze({id:'H-O',name:'Hydrogen → Oxygen',from:122,to:123,fromRoot:'H',toRoot:'O',siteFrom:6,siteTo:7}),
 Object.freeze({id:'O-N',name:'Oxygen → Nitrogen',from:244,to:245,fromRoot:'O',toRoot:'N',siteFrom:12,siteTo:13}),
 Object.freeze({id:'N-LID',name:'Nitrogen lid · sealed',from:366,to:null,fromRoot:'N',toRoot:null,siteFrom:18,siteTo:null})
]);
export const TIERS=Object.freeze(['W','M','S']);
export const PROGRAMS=Object.freeze([
 Object.freeze({name:'No operant',actions:Object.freeze([])}),
 ...OPERANTS.map(op=>Object.freeze({name:op.name,actions:Object.freeze([op.id])}))
]);
const ALLOWED=new Set(OPERANTS.map(x=>x.id));
const frozen=x=>Object.freeze(x);
export function gateAt(address){
 if(!Number.isInteger(address))throw new RangeError('Gate source must be an integer');
 const gate=GATES.find(x=>x.from===address);
 if(!gate)throw new RangeError('Only 122, 244 and 366 are explicit root gates; interior/tail addresses cannot jump');
 return gate;
}
export function validateProgram(program){
 if(!Array.isArray(program)||program.length>5||program.some(x=>!ALLOWED.has(x)))
  throw new RangeError('Program must be 0–5 declared operants in execution order');
 return frozen([...program]);
}
function rgb(hex){
 if(typeof hex!=='string'||!/^#[A-F0-9]{6}$/i.test(hex))throw new Error('RGB hex expected');
 return [1,3,5].map(i=>parseInt(hex.slice(i,i+2),16));
}
export function colorDiscontinuity(from,to){
 if(!from||!to)return null;
 const d=((to.hue-from.hue+540)%360)-180;
 const A=rgb(from.hex),B=rgb(to.hex);
 return frozen({
  absoluteWrappedHueDeltaDegrees:Math.abs(d),
  signedWrappedHueDeltaDegrees:d,
  saturationDelta:to.saturation-from.saturation,
  valueDelta:to.value-from.value,
  rgbChannelDelta:frozen(B.map((x,i)=>x-A[i])),
  rgbEuclideanDistance:Math.hypot(...B.map((x,i)=>x-A[i])),
  scope:'screen RGB / HSV display difference only, not photon or energy conservation'
 });
}
export function transferAt(from,strength='S',operatorIds=[]){
 const gate=gateAt(from),program=validateProgram(operatorIds);
 if(!TIERS.includes(strength))throw new RangeError('Only W/M/S source tiers');
 const origin=addressColor(from,strength),outgoing=operateColor(origin,program);
 const closed=gate.to===null;
 // The display is explicitly reprojected into the new root. The previous
 // hue is not copied across an unrelated symbolic root as if conserved.
 const targetBase=closed?null:addressColor(gate.to,strength),
  incoming=closed?null:operateColor(targetBase,program);
 if(!closed&&gate.to!==from+1)throw new Error('Only adjacent address transitions are valid');
 if(!closed&&(origin.rootSymbol!==gate.fromRoot||targetBase.rootSymbol!==gate.toRoot))
  throw new Error('Root transition identity mismatch');
 const ticket=frozen({
  sourceIdentity:origin.identityKey,
  sourceAddress:from,sourceRoot:origin.rootSymbol,
  sourceAtomicNumber:origin.atomicNumber,
  strength,operatorProgram:program,
  gateId:gate.id,
  // Source identity is never replaced with a target identity: the destination
  // is a new presentation, with traceable origin and own native identity.
  destinationAddress:gate.to,
  destinationRoot:gate.toRoot,
  checksum:'symbolic-order:'+from+':'+strength+':'+program.join('>')
 });
 const provenance=frozen({
  sourceUnmodified:origin.address===from&&origin.strength===strength,
  destinationNative:closed?true:(targetBase.address===gate.to&&targetBase.rootSymbol===gate.toRoot),
  no370TailEntry:closed?true:!SOURCE_TAIL.includes(gate.to),
  noWrap:closed?true:gate.to===from+1,
  operatorOrderPreserved:outgoing.appliedOperants.join('|')===program.join('|') &&
   (closed||incoming.appliedOperants.join('|')===program.join('|')),
  strengthLabelPreserved:closed?true:(origin.strength===targetBase.strength),
  unchangedElementalRoot:origin.rootSymbol===gate.fromRoot,
  terminalLidClosed:closed?from===ROOT_CAPACITY:true
 });
 return frozen({
  schema:'oasis/n184/hon-boundary-transfer-result/v95',
  gate,from,to:gate.to,state:closed?'CLOSED':'TRANSFERRED',
  ticket,origin,outgoing,targetBase,incoming,
  displayJump:colorDiscontinuity(outgoing,incoming),provenance,
  valid:Object.values(provenance).every(Boolean),
  physicalConservationClaim:false
 });
}
export function surveyAllBoundaries(){
 const results=GATES.flatMap(gate=>TIERS.flatMap(tier=>
  PROGRAMS.map(p=>transferAt(gate.from,tier,p.actions))));
 return frozen({
  schema:'oasis/n184/hon-boundary-survey/v95',
  cases:results.length,transfers:results.filter(x=>x.state==='TRANSFERRED').length,
  closures:results.filter(x=>x.state==='CLOSED').length,
  invalid:results.filter(x=>!x.valid).map(x=>x.ticket.checksum),
  perGate:frozen(GATES.map(g=>frozen({
   gate:g.id,cases:results.filter(x=>x.from===g.from).length,
   transfers:results.filter(x=>x.from===g.from&&x.state==='TRANSFERRED').length,
   closures:results.filter(x=>x.from===g.from&&x.state==='CLOSED').length
  }))),
  examples:frozen(results.filter(x=>x.ticket.strength==='S'&&x.ticket.operatorProgram.length===0))
 });
}
export function cubitGateAudit(){
 const mapped=[6,7,12,13,15,18].map(cubitToHON);
 const identity={HO:frozen([mapped[0],mapped[1]]),ON:frozen([mapped[2],mapped[3]]),
  doublePipe:mapped[4],lid:mapped[5]};
 const linked=frozen(GATES.map(g=>frozen({
  gate:g.id,fromSite:g.siteFrom,toSite:g.siteTo,fromAddress:g.from,toAddress:g.to,
  sourcePacket:cubitToHON(g.siteFrom).originalPacket,
  destinationPacket:g.siteTo?cubitToHON(g.siteTo).originalPacket:null,
  sourceStrength:cubitToHON(g.siteFrom).strength,
  destinationStrength:g.siteTo?cubitToHON(g.siteTo).strength:null
 })));
 return frozen({
  schema:'oasis/n184/cubit-boundary-bridge/v95',
  cubit:'{|12|}{|3456|}{|78|}{|910|}{|1112131415||}{|1617|}{|18|}',
  sites:mapped,links:linked,
  fifthPacketSeam:{position:15,address:293,root:'N',isRootTransition:false},
  terminal:{position:18,address:366,root:'N',state:'CLOSED'},
  sourceRoots:[...ROOTS.map(r=>r.symbol)],
  mapped
 });
}
