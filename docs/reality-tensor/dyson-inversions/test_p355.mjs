import assert from 'node:assert/strict';
import {append,checkpoint,verify,items} from './p355_chain.mjs';
let tests=0;const results={};
for(const envelope of ['total','boxy','circle']){
 const all=[...items(envelope,47,42,1440,1024)];
 const full=append([],all);let resumed=[];
 for(let start=0;start<all.length;start+=137)resumed=append(resumed,all.slice(start,start+137),checkpoint(resumed).head);
 const trusted=checkpoint(full);
 assert.deepEqual(checkpoint(resumed),trusted);tests++;
 assert.equal(verify(resumed,trusted).ok,true);tests++;
 const modified=structuredClone(resumed);modified[900].item.root=5;
 assert.equal(verify(modified,trusted).ok,false);tests++;
 const deleted=structuredClone(resumed);deleted.splice(900,1);
 assert.equal(verify(deleted,trusted).ok,false);tests++;
 const truncated=resumed.slice(0,-1);
 assert.equal(verify(truncated,trusted).ok,false);tests++;
 assert.equal(verify(truncated).ok,true);tests++;
 const reordered=structuredClone(resumed);[reordered[10],reordered[11]]=[reordered[11],reordered[10]];
 assert.equal(verify(reordered,trusted).ok,false);tests++;
 results[envelope]={records:resumed.length,head:trusted.head,attacksRejected:4,unanchoredTruncationUndetectable:true};
}
console.log(JSON.stringify({status:'PASS',assertions:tests,results},null,2));
