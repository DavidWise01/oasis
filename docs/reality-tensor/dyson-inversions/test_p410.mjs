import assert from 'node:assert/strict';
import {mkdtemp,rm,copyFile,unlink} from 'node:fs/promises';
import {join} from 'node:path';import {tmpdir} from 'node:os';
import {generateKeyPairSync} from 'node:crypto';import {performance} from 'node:perf_hooks';
import {GenesisAuthority,genesisGrant,validateGrant,BLOCKADE} from './p410_genesis.mjs';
const start=performance.now();let checks=0;const eq=(a,b)=>{assert.deepEqual(a,b);checks++},ok=v=>{assert.ok(v);checks++};
const dir=await mkdtemp(join(tmpdir(),'p410-')),file=join(dir,'authority.db'),snapshot=join(dir,'old.db');
const kp=generateKeyPairSync('ed25519'),rogue=generateKeyPairSync('ed25519');let db;
try{
 eq(BLOCKADE,'{-{+{%}+}-}');
 db=new GenesisAuthority(file,kp.publicKey,'oasis/main');eq(db.status().reason,'authority-missing:recovery-required');eq(db.advance(1,'a'.repeat(64)).ok,false);db.close();
 const grant=genesisGrant(kp.privateKey,'oasis/main');ok(validateGrant(grant,kp.publicKey,'oasis/main'));eq(validateGrant(grant,rogue.publicKey,'oasis/main'),false);eq(validateGrant({...grant,nonce:'tampered'},kp.publicKey,'oasis/main'),false);
 assert.throws(()=>GenesisAuthority.provision(file,kp.publicKey,'oasis/main',{...grant,nonce:'fake'}));checks++;
 db=GenesisAuthority.provision(file,kp.publicKey,'oasis/main',grant);ok(db.status().ok);eq(db.status().epoch,0);
 assert.throws(()=>GenesisAuthority.provision(file,kp.publicKey,'oasis/main',grant));checks++;
 ok(db.advance(1,'a'.repeat(64)).ok);eq(db.advance(1,'a'.repeat(64)).reason,'nonconsecutive-or-replayed-epoch');
 db.db.exec(`VACUUM INTO '${snapshot.replaceAll("'","''")}'`);
 const interrupted=db.advance(2,'b'.repeat(64),{failBeforeCommit:true});eq(interrupted.ok,false);eq(db.status().epoch,1);
 ok(db.advance(2,'b'.repeat(64)).ok);eq(db.status().epoch,2);db.close();
 db=new GenesisAuthority(file,kp.publicKey,'oasis/main');eq(db.status().epoch,2);db.close();
 await copyFile(snapshot,file);db=new GenesisAuthority(file,kp.publicKey,'oasis/main');eq(db.status().epoch,1);
 db.close();await unlink(file);
 db=new GenesisAuthority(file,kp.publicKey,'oasis/main');eq(db.status().reason,'authority-missing:recovery-required');eq(db.advance(3,'c'.repeat(64)).ok,false);db.close();
 ok(validateGrant(grant,kp.publicKey,'oasis/main'));
 console.log(JSON.stringify({status:'PASS_WITH_EXTERNAL_ANTIROLLBACK_GAP',assertions:checks,elapsedMs:performance.now()-start,genesisSeparatelyAuthorized:true,missingStoreFailClosed:true,coherentRollbackLocallyUndetected:true}));
}finally{db?.close();await rm(dir,{recursive:true,force:true});}