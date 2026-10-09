import {createHash} from 'node:crypto';

export const N = 5;
export const GENESIS_DIGEST = '0'.repeat(64);
const allowed = new Set(['occupied','vacant']);
const sha = s => createHash('sha256').update(s, 'utf8').digest('hex');
export const canonicalState = a => a.join('|');
export const binaryState = a => Array.isArray(a) && a.length === N && a.every(x => allowed.has(x));
export function adjacent(i,j) {
  return Number.isInteger(i) && Number.isInteger(j) && i>=0 && i<N && j>=0 && j<N &&
    i!==j && ((i+1)%N===j || (i+N-1)%N===j);
}
export const isSeam = (i,j) => (i===0 && j===4) || (i===4 && j===0);
export const formatOp = (i,j) => `move:${i}->${j}${isSeam(i,j)?':|||':''}`;
export const parseOp = s => {
  if(typeof s !== 'string') return null;
  const m=/^move:([0-4])->([0-4])(:\\|\\|\\|)?$/.exec(s);
  return m ? {from:Number(m[1]),to:Number(m[2]),seam:Boolean(m[3])} : null;
};
export function legalMove(before,i,j) {
  return binaryState(before) && adjacent(i,j) && before[i]==='occupied' && before[j]==='vacant';
}
export function applyMove(before,i,j) {
  if(!legalMove(before,i,j)) throw Error('ILLEGAL_MOVE');
  const after=[...before]; after[i]='vacant';after[j]='occupied'; return after;
}
export const v1Receipt = (before,operation,after) =>
  sha(`${canonicalState(before)}::${operation}::${canonicalState(after)}`);
export function makeTransition(before,i,j) {
  const after=applyMove(before,i,j);
  const operation=formatOp(i,j);
  return {before:[...before],operation,after,receipt:v1Receipt(before,operation,after)};
}
export function verifyStrict(tx) {
  if(tx===null || typeof tx!=='object' || Array.isArray(tx) ||
     Object.keys(tx).sort().join(',')!=='after,before,operation,receipt' ||
     !binaryState(tx.before) || !binaryState(tx.after) ||
     typeof tx.receipt!=='string' || !/^[a-f0-9]{64}$/.test(tx.receipt)) return false;
  const op=parseOp(tx.operation);
  if(!op || !legalMove(tx.before,op.from,op.to) ||
     op.seam!==isSeam(op.from,op.to) || tx.operation!==formatOp(op.from,op.to)) return false;
  const expected=applyMove(tx.before,op.from,op.to);
  if(!expected.every((x,i)=>x===tx.after[i])) return false;
  return tx.receipt===v1Receipt(tx.before,tx.operation,tx.after);
}

// V2 extends V1 for *event* identity; V1 source remains unchanged.
const digestInput=(sequence,prev,tx)=>JSON.stringify([
  'I13-T2-EVENT-v2',sequence,prev,tx.before,tx.operation,tx.after,tx.receipt
]);
export function appendEvent(sequence,prev,tx) {
  if(!verifyStrict(tx) || !Number.isSafeInteger(sequence) || sequence<0 ||
     typeof prev!=='string' || !/^[a-f0-9]{64}$/.test(prev)) throw Error('BAD_EVENT');
  return {sequence,prev,tx,digest:sha(digestInput(sequence,prev,tx))};
}
export function verifyTrace(events,initial,externalAnchor=null) {
  if(!binaryState(initial) || !Array.isArray(events)) return false;
  let state=[...initial],prev=GENESIS_DIGEST;
  for(let idx=0;idx<events.length;idx++){
    const e=events[idx];
    if(e===null || typeof e!=='object' || Array.isArray(e) ||
       Object.keys(e).sort().join(',')!=='digest,prev,sequence,tx' ||
       e.sequence!==idx || e.prev!==prev || !verifyStrict(e.tx) ||
       !e.tx.before.every((v,j)=>v===state[j]) ||
       e.digest!==sha(digestInput(e.sequence,e.prev,e.tx)))return false;
    prev=e.digest;state=[...e.tx.after];
  }
  return externalAnchor===null || externalAnchor===prev;
}
export function countOccupied(state){return state.filter(v=>v==='occupied').length;}
