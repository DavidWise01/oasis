// OASIS N184 v9.6: 5 inherited HSV operants + 2 signed receipt operants (-,+).
// - / + bookkeep a symbolic token transfer; no physics or cryptography is claimed.
import {OPERANTS} from '../elemental-hon-color-operants-v94/hon_core.mjs';
import {GATES,TIERS,PROGRAMS,transferAt} from '../hon-boundary-transfer-v95/boundary_core.mjs';

export const SIGNS=Object.freeze([
  Object.freeze({glyph:'-',id:'debit',role:'source',delta:-1}),
  Object.freeze({glyph:'+',id:'credit',role:'destination',delta:1})
]);
export const ALL_OPERANTS=Object.freeze([
 ...OPERANTS.map(o=>Object.freeze({id:o.id,name:o.name,kind:'color'})),
 ...SIGNS.map(o=>Object.freeze({id:o.glyph,name:o.id,kind:'transfer',delta:o.delta}))
]);
export const FRAME_SCHEMA='oasis/n184/signed-root-frame/v96';
export const LEDGER_SCHEMA='oasis/n184/signed-root-ledger/v96';
const freeze=x=>Object.freeze(x);
const MODES=Object.freeze([
 'valid','missing-debit','missing-credit','reverse','duplicate-debit',
 'duplicate-credit','wrong-source','wrong-destination','wrong-root',
 'wrong-attempt','wrong-tier','change-program','bad-key','lid-forgery'
]);
export const FAULT_MODES=MODES;
function canonicalKey({attemptId,from,to,tier,program,sourceIdentity,gateId,sourceChecksum}){
 return JSON.stringify([attemptId,from,to,tier,program,sourceIdentity,gateId,sourceChecksum]);
}
function attemptOk(s){return typeof s==='string'&&s.length>0&&s.length<=80&&/^[A-Za-z0-9:_-]+$/.test(s)}
export function buildSignedFrame(from,tier='S',program=[],attemptId='attempt-001'){
 if(!attemptOk(attemptId))throw new RangeError('Attempt ID required, maximum 80 safe characters');
 const t=transferAt(from,tier,program);
 const key=canonicalKey({attemptId,from,to:t.to,tier,program:[...program],
  sourceIdentity:t.ticket.sourceIdentity,gateId:t.gate.id,sourceChecksum:t.ticket.checksum});
 const marks=t.state==='CLOSED'?[]:[
  freeze({symbol:'-',delta:-1,role:'source',root:t.origin.rootSymbol,
   address:from,attemptId,key}),
  freeze({symbol:'+',delta:+1,role:'destination',root:t.targetBase.rootSymbol,
   address:t.to,attemptId,key})
 ];
 return freeze({schema:FRAME_SCHEMA,attemptId,gateId:t.gate.id,
  from,to:t.to,tier,program:freeze([...program]),sourceIdentity:t.ticket.sourceIdentity,
  sourceChecksum:t.ticket.checksum,key,marks:freeze(marks)});
}
export function mutateFrame(frame,mode){
 if(!MODES.includes(mode))throw new RangeError('Unregistered fault mode '+mode);
 if(!frame||frame.schema!==FRAME_SCHEMA)throw new TypeError('Signed frame expected');
 const m=frame.marks.map(x=>({...x}));
 const f={...frame,program:[...frame.program],marks:m};
 if(mode==='valid')return frame;
 if(mode==='missing-debit')f.marks=m.filter(x=>x.symbol!== '-');
 if(mode==='missing-credit')f.marks=m.filter(x=>x.symbol!== '+');
 if(mode==='reverse')f.marks=m.toReversed();
 if(mode==='duplicate-debit')f.marks=m.length?[m[0],m[0],m[1]]:[{symbol:'-',role:'source',delta:-1,address:366,root:'N'}];
 if(mode==='duplicate-credit')f.marks=m.length?[m[0],m[1],m[1]]:[{symbol:'+',role:'destination',delta:1,address:367,root:'N'}];
 if(mode==='wrong-source'&&m.length)f.marks=[{...m[0],address:121},m[1]];
 if(mode==='wrong-destination'&&m.length)f.marks=[m[0],{...m[1],address:367}];
 if(mode==='wrong-root'&&m.length)f.marks=[m[0],{...m[1],root:'N'===m[1].root?'H':'N'}];
 if(mode==='wrong-attempt'&&m.length)f.marks=[m[0],{...m[1],attemptId:frame.attemptId+'x'}];
 if(mode==='wrong-tier')f.tier=frame.tier==='W'?'M':'W';
 if(mode==='change-program')f.program=frame.program.length?frame.program.toReversed().concat('gravity'):['gravity'];
 if(mode==='bad-key')f.key=frame.key+'x';
 if(mode==='lid-forgery')f.marks=[{symbol:'-',delta:-1,role:'source',root:'N',address:366,attemptId:frame.attemptId,key:frame.key},
 {symbol:'+',delta:1,role:'destination',root:'H',address:1,attemptId:frame.attemptId,key:frame.key}];
 f.program=freeze(f.program);f.marks=freeze(f.marks.map(x=>freeze(x)));
 return freeze(f);
}
export function createLedger(){
 return freeze({schema:LEDGER_SCHEMA,
  attempts:freeze([]),receipts:freeze([]),
  balances:freeze({H:0,O:0,N:0}),
  totalNet:0});
}
function assertLedger(l){
 if(!l||l.schema!==LEDGER_SCHEMA||!Array.isArray(l.attempts)||!Array.isArray(l.receipts)||
  !l.balances||!['H','O','N'].every(x=>Number.isInteger(l.balances[x]))||
  !Number.isInteger(l.totalNet))
 throw new TypeError('Valid signed immutable ledger required');
}
function verdict(status,ledger,frame,info={}){
 return freeze({status,accepted:status==='ACCEPT',ledger,
  attemptId:frame?.attemptId??null,...info});
}
export function submitFrame(ledger,frame){
 assertLedger(ledger);
 if(!frame||frame.schema!==FRAME_SCHEMA||!attemptOk(frame.attemptId))
  return verdict('REJECT_SCHEMA',ledger,frame);
 // Attempt uniqueness applies globally: replay of a prior committed attempt is forbidden,
 // even if the caller changes its gate, source, strengths, marks or program.
 if(ledger.attempts.includes(frame.attemptId))
  return verdict('REJECT_REPLAY',ledger,frame);
 let t,expected;
 try{
  if(!Array.isArray(frame.program))throw new Error('Invalid action list');
  t=transferAt(frame.from,frame.tier,frame.program);
  expected=buildSignedFrame(frame.from,frame.tier,frame.program,frame.attemptId);
 }catch{
  return verdict('REJECT_FRAME',ledger,frame);
 }
 if(frame.from===366){
  // A valid lid frame MUST have no direction marks, credit address or wrap.
  const validSeal=JSON.stringify(frame)===JSON.stringify(expected);
  return verdict(validSeal?'CLOSED':'REJECT_CLOSED',ledger,frame,
   {gate:'N-LID',balanced:false,notes:'The terminal lid does not debit or credit any root.'});
 }
 // Recompute all trusted source-side details, and compare the entire serialized
 // event packet, not only the zero-sum of the signed marks.
 if(JSON.stringify(frame)!==JSON.stringify(expected))
  return verdict('REJECT_MISMATCH',ledger,frame);
 if(frame.marks.length!==2||
   frame.marks[0].symbol!=='-'||frame.marks[1].symbol!=='+'||
   frame.marks[0].delta!==-1||frame.marks[1].delta!==1||
   frame.marks[0].delta+frame.marks[1].delta!==0)
  return verdict('REJECT_PAIR',ledger,frame);
 if(!t.valid||t.to!==frame.from+1)
  return verdict('REJECT_GATE',ledger,frame);
 const balances={...ledger.balances};
 balances[t.origin.rootSymbol]-=1;
 balances[t.targetBase.rootSymbol]+=1;
 const receipt=freeze({
  attemptId:frame.attemptId,gate:t.gate.id,source:t.origin.rootSymbol,
  destination:t.targetBase.rootSymbol,from:frame.from,to:frame.to,
  strength:frame.tier,program:freeze([...frame.program]),
  sourceIdentity:t.ticket.sourceIdentity,transferKey:frame.key,
  debit:-1,credit:+1,net:0,
  sourceDisplayHex:t.outgoing.hex,targetDisplayHex:t.incoming.hex,
  displayHueJumpDegrees:t.displayJump.absoluteWrappedHueDeltaDegrees,
  sourcePinned:true,kind:'symbolic-bookkeeping-only'
 });
 const next=freeze({schema:LEDGER_SCHEMA,
  attempts:freeze([...ledger.attempts,frame.attemptId]),
  receipts:freeze([...ledger.receipts,receipt]),
  balances:freeze(balances),totalNet:ledger.totalNet});
 return verdict('ACCEPT',next,frame,{gate:t.gate.id,balanced:true,receipt,
  colors:{source:t.outgoing.hex,target:t.incoming.hex},
  message:'One - source debit + one + destination credit; root net balance remains zero.'});
}
export function surveySigned(){
 const cases=GATES.flatMap(g=>TIERS.flatMap(tier=>PROGRAMS.map((p,index)=>{
  const attempt='survey-'+g.id+'-'+tier+'-'+index;
  const f=buildSignedFrame(g.from,tier,p.actions,attempt);
  const r=submitFrame(createLedger(),f);
  return freeze({gate:g.id,tier,program:p.actions,status:r.status,
   accepted:r.accepted,balanced:r.balanced===true});
 })));
 const good=cases.filter(x=>x.status==='ACCEPT').length,
  closed=cases.filter(x=>x.status==='CLOSED').length;
 return freeze({schema:'oasis/n184/hon-signed-survey/v96',
  cases:cases.length,accepted:good,closed,rejected:cases.length-good-closed,
  source370Untouched:true,operatorCount:ALL_OPERANTS.length,
  first:cases[0],last:cases.at(-1)});
}
