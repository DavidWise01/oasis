import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const base=fs.mkdtempSync(path.join(os.tmpdir(),'oasis-gate6-audit-unit-'));
const evidence=path.join(base,'evidence'),receiver=path.join(base,'receiver');
fs.mkdirSync(evidence);fs.mkdirSync(receiver);
const sha=x=>createHash('sha256').update(x).digest('hex');
const hash='a'.repeat(64);
function make(sender,id,prev){const core={v:1,sender,id,frameSha256:hash,prev};return {...core,hash:sha(Buffer.from(JSON.stringify(core)))};}
const r1=make('OASIS_TEST','base','0'.repeat(64)),r2=make('OASIS_TEST','crash_001',r1.hash);
const journal=path.join(receiver,'receipts.jsonl');
const items=[r1,r2];
const writeJournal=rows=>fs.writeFileSync(journal,rows.map(v=>JSON.stringify(v)).join('\n')+'\n');
const client=path.join(evidence,'client-events.jsonl');
const baseline=[{sourceCommit:'FAKE_TEST_COMMIT',frameSha256:hash,eventId:'base',status:'APPLIED',receipt:r1.hash},{sourceCommit:'FAKE_TEST_COMMIT',frameSha256:hash,eventId:'base',status:'DUPLICATE',receipt:r1.hash},{sourceCommit:'FAKE_TEST_COMMIT',frameSha256:hash,eventId:'crash_001',status:'LOST_ACK_EXPECTED'},{sourceCommit:'FAKE_TEST_COMMIT',frameSha256:hash,eventId:'crash_001',status:'DUPLICATE',receipt:r2.hash}];
const writeClient=rows=>fs.writeFileSync(client,rows.map(v=>JSON.stringify(v)).join('\n')+'\n');
function cmd(action,args=[]){return spawnSync(process.execPath,[path.join(here,'gate6.mjs'),action,'--state',base,...args],{encoding:'utf8'});}
let passed=0;const test=(name,fn)=>{fn();passed++;console.log('PASS',String(passed).padStart(2),name)};
try{
 writeJournal(items);writeClient(baseline);
 let result=cmd('inspect');test('valid receipt chain',()=>assert.equal(result.status,0));
 const proof=JSON.parse(fs.readFileSync(path.join(evidence,'receiver-proof.json'),'utf8'));proof.sourceCommit='FAKE_TEST_COMMIT';fs.writeFileSync(path.join(evidence,'receiver-proof.json'),JSON.stringify(proof));
 test('two unique durable entries',()=>assert.equal(proof.entryCount,2));
 test('head equals final record',()=>assert.equal(proof.journalHead,r2.hash));
 result=cmd('finalize',['--event','crash_001','--mode','vm']);test('valid crash-replay evidence accepted in VM scope',()=>assert.equal(result.status,0));
 let final=JSON.parse(fs.readFileSync(path.join(evidence,'FINAL_RESULT.json')));
 test('physical-device certification is not automatic',()=>assert.equal(final.physicalIndependenceVerified,false));
 test('same receipt preserved',()=>assert.equal(final.receipt,r2.hash));
 writeClient(baseline.filter(v=>v.status!=='LOST_ACK_EXPECTED'));
 result=cmd('finalize',['--event','crash_001','--mode','vm']);test('absent crash/ACK loss rejected',()=>assert.notEqual(result.status,0));
 writeClient(baseline.map(x=>x.status==='DUPLICATE'&&x.eventId==='crash_001'?{...x,receipt:'f'.repeat(64)}:x));
 result=cmd('finalize',['--event','crash_001','--mode','vm']);test('mismatched duplicate hash rejected',()=>assert.notEqual(result.status,0));
 writeClient(baseline);
 writeJournal([{...r1,frameSha256:'0'.repeat(64)},r2]);
 result=cmd('inspect');test('modified journal rejected',()=>assert.notEqual(result.status,0));
 writeJournal(items);fs.appendFileSync(journal,'{"incomplete":');
 result=cmd('inspect');test('partial trailing record rejected',()=>assert.notEqual(result.status,0));
 writeJournal([r1,r1]);result=cmd('inspect');test('duplicate journal record rejected',()=>assert.notEqual(result.status,0));
 writeJournal(items);
 result=cmd('finalize',['--event','missing','--mode','physical']);test('unknown event rejected in physical mode',()=>assert.notEqual(result.status,0));
 console.log('EVIDENCE UNIT SUITE',passed,'/',passed,'PASS');
}catch(err){console.error('UNIT TEST FAILED',err);process.exitCode=1}
finally{fs.rmSync(base,{recursive:true,force:true})}