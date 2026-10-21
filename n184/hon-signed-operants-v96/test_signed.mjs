import assert from 'node:assert/strict';
import fs from 'node:fs';
import {OPERANTS,ROOTS,SOURCE_TAIL} from '../elemental-hon-color-operants-v94/hon_core.mjs';
import {GATES,TIERS,PROGRAMS,transferAt} from '../hon-boundary-transfer-v95/boundary_core.mjs';
import {CUBIT,compileCubit} from '../analytical-cubit-color-bands-v93/cubit_core.mjs';
import {SIGNS,ALL_OPERANTS,FAULT_MODES,FRAME_SCHEMA,LEDGER_SCHEMA,
 buildSignedFrame,mutateFrame,createLedger,submitFrame,surveySigned} from './signed_core.mjs';
const spec=JSON.parse(fs.readFileSync(new URL('./spec.json',import.meta.url),'utf8'));
const checks={};function check(n,fn){fn();checks[n]=true}
const zero=createLedger(),H=buildSignedFrame(122,'M',['gravity'],'A1'),
 O=buildSignedFrame(244,'S',['compression'],'A2'),
 N=buildSignedFrame(366,'W',[],'A3');
const accepted=submitFrame(zero,H);
check('v96 schema',()=>assert.equal(spec.schema,'oasis/n184/hon-signed-operants/v96'));
check('two signed - +',()=>assert.deepEqual(SIGNS.map(x=>x.glyph),['-','+']));
check('two signed values -1 +1',()=>assert.deepEqual(SIGNS.map(x=>x.delta),[-1,1]));
check('signed pair total zero',()=>assert.equal(SIGNS.reduce((n,x)=>n+x.delta,0),0));
check('five color operants inherited',()=>assert.deepEqual(ALL_OPERANTS.slice(0,5).map(x=>x.name),OPERANTS.map(x=>x.name)));
check('all seven operants',()=>assert.equal(ALL_OPERANTS.length,7));
check('new pair not color operators',()=>assert.deepEqual(ALL_OPERANTS.slice(5).map(x=>x.kind),['transfer','transfer']));
check('literal -+ order',()=>assert.equal(SIGNS.map(x=>x.glyph).join(''),'-+'));
check('minus source role',()=>assert.equal(SIGNS[0].role,'source'));
check('plus target role',()=>assert.equal(SIGNS[1].role,'destination'));
check('three 122-root spans unchanged',()=>assert.deepEqual(ROOTS.map(x=>[x.start,x.end]),[[1,122],[123,244],[245,366]]));
check('370 tail unchanged',()=>assert.deepEqual(SOURCE_TAIL,[367,368,369,370]));
check('actual atomic numbers unchanged',()=>assert.deepEqual(ROOTS.map(x=>x.atomicNumber),[1,8,7]));
check('cubit seven packet lengths unchanged',()=>assert.deepEqual([...compileCubit().packetLengths],[2,4,2,2,5,2,1]));
check('original 18 cubit positions exact',()=>assert.equal(CUBIT,'{|12|}{|3456|}{|78|}{|910|}{|1112131415||}{|1617|}{|18|}'));
check('H/O gate',()=>assert.deepEqual([H.from,H.to],[122,123]));
check('O/N gate',()=>assert.deepEqual([O.from,O.to],[244,245]));
check('N lid gate',()=>assert.deepEqual([N.from,N.to],[366,null]));
check('two event marks',()=>assert.equal(H.marks.length,2));
check('mark order',()=>assert.deepEqual(H.marks.map(x=>x.symbol),['-','+']));
check('mark values',()=>assert.deepEqual(H.marks.map(x=>x.delta),[-1,1]));
check('debit at source 122',()=>assert.equal(H.marks[0].address,122));
check('credit at target 123',()=>assert.equal(H.marks[1].address,123));
check('minus H root',()=>assert.equal(H.marks[0].root,'H'));
check('plus O root',()=>assert.equal(H.marks[1].root,'O'));
check('first event same attempt',()=>assert.equal(H.marks[0].attemptId,H.attemptId));
check('second event same attempt',()=>assert.equal(H.marks[1].attemptId,H.attemptId));
check('both events same transfer key',()=>assert.equal(H.marks[0].key,H.marks[1].key));
check('source identity exact',()=>assert.equal(H.sourceIdentity,'rootH:a122:sM'));
check('frame frozen',()=>assert.equal(Object.isFrozen(H),true));
check('event objects frozen',()=>assert.ok(H.marks.every(Object.isFrozen)));
check('marks array frozen',()=>assert.equal(Object.isFrozen(H.marks),true));
check('ledger schema',()=>assert.equal(zero.schema,LEDGER_SCHEMA));
check('frame schema',()=>assert.equal(H.schema,FRAME_SCHEMA));
check('starting balances zero',()=>assert.deepEqual(zero.balances,{H:0,O:0,N:0}));
check('starting attempts empty',()=>assert.deepEqual(zero.attempts,[]));
check('initial ledger frozen',()=>assert.ok(Object.isFrozen(zero)));
check('initial balances frozen',()=>assert.ok(Object.isFrozen(zero.balances)));
check('H to O accepted',()=>assert.equal(accepted.status,'ACCEPT'));
check('accepted true',()=>assert.equal(accepted.accepted,true));
check('pair marked balanced',()=>assert.equal(accepted.balanced,true));
check('H/O balances -1 +1',()=>assert.deepEqual(accepted.ledger.balances,{H:-1,O:1,N:0}));
check('H/O net ledger zero',()=>assert.equal(Object.values(accepted.ledger.balances).reduce((a,b)=>a+b,0),0));
check('receipt count 1',()=>assert.equal(accepted.ledger.receipts.length,1));
check('receipt net zero',()=>assert.equal(accepted.receipt.net,0));
check('receipt sign pair',()=>assert.deepEqual([accepted.receipt.debit,accepted.receipt.credit],[-1,1]));
check('receipt pinned to source',()=>assert.equal(accepted.receipt.sourceIdentity,H.sourceIdentity));
check('receipt holds ordered color program',()=>assert.deepEqual(accepted.receipt.program,['gravity']));
check('original ledger not mutated',()=>assert.deepEqual(zero.balances,{H:0,O:0,N:0}));
check('original receipt history untouched',()=>assert.equal(zero.receipts.length,0));
check('committed attempt consumed once',()=>assert.deepEqual(accepted.ledger.attempts,['A1']));
check('replayed frame rejected',()=>assert.equal(submitFrame(accepted.ledger,H).status,'REJECT_REPLAY'));
check('replay leaves ledger identity same',()=>assert.equal(submitFrame(accepted.ledger,H).ledger,accepted.ledger));
check('reused attempt with new HSV program rejected',()=>assert.equal(submitFrame(accepted.ledger,buildSignedFrame(122,'M',['explosion'],'A1')).status,'REJECT_REPLAY'));
check('reused attempt with different gate rejected',()=>assert.equal(submitFrame(accepted.ledger,buildSignedFrame(244,'M',[],'A1')).status,'REJECT_REPLAY'));
check('reused attempt with different tier rejected',()=>assert.equal(submitFrame(accepted.ledger,buildSignedFrame(122,'W',[],'A1')).status,'REJECT_REPLAY'));
const second=submitFrame(accepted.ledger,O);
check('O to N accepted',()=>assert.equal(second.status,'ACCEPT'));
check('root balances after two transfers',()=>assert.deepEqual(second.ledger.balances,{H:-1,O:0,N:1}));
check('two receipts committed',()=>assert.equal(second.ledger.receipts.length,2));
check('two transfer net zero',()=>assert.equal(second.ledger.totalNet,0));
check('root ledger balances sum zero',()=>assert.equal(Object.values(second.ledger.balances).reduce((a,b)=>a+b,0),0));
check('lid explicitly closed',()=>assert.equal(submitFrame(second.ledger,N).status,'CLOSED'));
check('lid makes zero new receipts',()=>assert.equal(submitFrame(second.ledger,N).ledger,second.ledger));
check('lid has no signed events',()=>assert.deepEqual(N.marks,[]));
check('lid has no tail destination',()=>assert.equal(N.to,null));
check('lid cannot wrap to address 1',()=>assert.notEqual(N.to,1));
check('lid forged transfer pair rejected',()=>assert.equal(submitFrame(zero,mutateFrame(N,'lid-forgery')).status,'REJECT_CLOSED'));
check('forged lid does not alter ledger',()=>assert.equal(submitFrame(zero,mutateFrame(N,'lid-forgery')).ledger,zero));
check('five legacy HSV operators can run',()=>assert.equal(buildSignedFrame(122,'S',OPERANTS.map(x=>x.id),'all-five').program.length,5));
check('six legacy HSV operators cannot run',()=>assert.throws(()=>buildSignedFrame(122,'S',['gravity','gravity','gravity','gravity','gravity','gravity'],'invalid')));
check('minus not mistaken for HSV op',()=>assert.throws(()=>buildSignedFrame(122,'S',['-'],'invalid')));
check('plus not mistaken for HSV op',()=>assert.throws(()=>buildSignedFrame(122,'S',['+'],'invalid')));
check('not a gate 121 rejected',()=>assert.throws(()=>buildSignedFrame(121,'S',[],'invalid')));
check('370 source tail cannot be gate',()=>assert.throws(()=>buildSignedFrame(367,'S',[],'invalid')));
check('empty attempt rejected',()=>assert.throws(()=>buildSignedFrame(122,'S',[],'')));
check('oversized attempt rejected',()=>assert.throws(()=>buildSignedFrame(122,'S',[],'x'.repeat(81))));
check('unsafe attempt rejected',()=>assert.throws(()=>buildSignedFrame(122,'S',[],'!unsafe')));
check('noninteger ledger balance rejected',()=>assert.throws(()=>submitFrame({...zero,balances:{H:1.2,O:0,N:0}},H)));
check('malformed ledger rejected',()=>assert.throws(()=>submitFrame({schema:'wrong'},H)));
check('malformed frame rejected without changes',()=>assert.equal(submitFrame(zero,{}).status,'REJECT_SCHEMA'));
const faulty=FAULT_MODES.filter(x=>x!=='valid'&&x!=='lid-forgery');
for(const mode of faulty){
 check('malformed '+mode+' rejected with zero writes',()=>{
  const v=submitFrame(zero,mutateFrame(H,mode));
  assert.equal(v.accepted,false,mode);assert.equal(v.ledger,zero,mode);
 });
}
check('valid unaltered frame accepted',()=>assert.equal(submitFrame(zero,mutateFrame(H,'valid')).status,'ACCEPT'));
check('fresh fully coherent forged frame not cryptographically authenticated',()=>assert.equal(submitFrame(zero,buildSignedFrame(122,'W',['explosion'],'new-well-formed')).accepted,true));
check('receipt keeps numeric display discontinuity',()=>assert.ok(Number.isFinite(accepted.receipt.displayHueJumpDegrees)));
check('receipt scope explicitly symbolic',()=>assert.equal(accepted.receipt.kind,'symbolic-bookkeeping-only'));
check('fixed campaign 54',()=>assert.equal(surveySigned().cases,54));
check('fixed campaign 36 accepted',()=>assert.equal(surveySigned().accepted,36));
check('fixed campaign 18 lids closed',()=>assert.equal(surveySigned().closed,18));
check('fixed campaign zero unexpected failures',()=>assert.equal(surveySigned().rejected,0));
check('campaign sees 7 operants',()=>assert.equal(surveySigned().operatorCount,7));
check('strength letters W M S',()=>assert.deepEqual(TIERS,['W','M','S']));
check('three gate links not altered',()=>assert.deepEqual(GATES.map(x=>[x.from,x.to]),[[122,123],[244,245],[366,null]]));
check('six color program choices 0 plus 5',()=>assert.equal(PROGRAMS.length,6));
check('two serial gate receipts balanced for each tier',()=>{
 for(const tier of TIERS){
  let ledger=createLedger();
  ledger=submitFrame(ledger,buildSignedFrame(122,tier,[],'t-'+tier+'-0')).ledger;
  ledger=submitFrame(ledger,buildSignedFrame(244,tier,[],'t-'+tier+'-1')).ledger;
  assert.deepEqual(ledger.balances,{H:-1,O:0,N:1});
  assert.equal(Object.values(ledger.balances).reduce((a,b)=>a+b,0),0);
 }
});
check('color data source remains v9.5',()=>assert.equal(transferAt(122,'M',['gravity']).ticket.sourceIdentity,H.sourceIdentity));
check('v95 N lid remains closed',()=>assert.equal(transferAt(366).state,'CLOSED'));
check('source370 separate and unchanged',()=>assert.equal(spec.inherited.unchangedSource370Tail.at(-1),370));
check('v9.5 upstream frozen',()=>assert.ok(spec.caveats.some(x=>x.includes('v9.5 source remain frozen'))));
check('Ada and toroidal years same',()=>assert.deepEqual(spec.inherited.historicalYears,[1832,1970]));
check('6/80/240 symbolism intact',()=>assert.deepEqual(spec.inherited.ring,[6,80,240]));
check('real CERN toroids unchanged',()=>assert.deepEqual(spec.inherited.cemRealTorusCounts,{A:0,B:3,C:0,D:0}));
check('viewer uses signed code and replay controls',()=>{
 const html=fs.readFileSync(new URL('./index.html',import.meta.url),'utf8');
 for(const needle of ['signed_core.mjs','debit','credit','REJECT_REPLAY','366'])assert.ok(html.includes(needle),needle);
});
console.log(JSON.stringify({result:'PASS',passed:Object.keys(checks).length,failed:0,
  operants:ALL_OPERANTS.map(x=>x.id),survey:surveySigned(),
  balancedRootBalancesAfterTwo:second.ledger.balances},null,2));
