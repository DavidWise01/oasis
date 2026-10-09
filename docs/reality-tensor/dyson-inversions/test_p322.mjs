import assert from 'node:assert/strict';
import {CIPHER,encodeIndex,decodeIndex,forwardOrder,inverseOrder,verify} from './p322_cipher_contract.mjs';
assert.equal(CIPHER.nonRootCount,255);assert.equal(CIPHER.totalCount,256);assert.equal(CIPHER.root,0);
for(let i=0;i<256;i++){assert.equal(decodeIndex(encodeIndex(i)),i);assert.equal(encodeIndex(i).length,2);}
assert.deepEqual(inverseOrder(),forwardOrder().reverse());
assert.deepEqual(verify(),{root:0,nonRoot:255,total:256,distinct:256,roundTrip:true,first:1,last:255});
for(const x of [-1,256,1.5,NaN])assert.throws(()=>encodeIndex(x));
for(const x of ['00a','gg','ff','',1])assert.throws(()=>decodeIndex(x));
console.log(JSON.stringify({status:'PASS',...verify(),legacy208Superseded:true}));
