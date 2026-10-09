import assert from 'node:assert/strict';
import {generateKeyPairSync} from 'node:crypto';
import {mkdtemp,rm,copyFile} from 'node:fs/promises';
import {join} from 'node:path';import {tmpdir} from 'node:os';
import {SerializedAuthority} from './p372_authority.mjs';
import {attest,verifyAgainstTrusted,saveTrusted,loadTrusted} from './p373_anchor.mjs';
const {publicKey,privateKey}=generateKeyPairSync('ed25519');
const root=await mkdtemp(join(tmpdir(),'p373-'));let checks=0;const check=v=>{assert.ok(v);checks++;};
const file=join(root,'witness.db'),old=join(root,'old.db'),trustFile=join(root,'external-trusted.json');
try{
 let db=new SerializedAuthority(file);check(db.reserve('w0',1,'a'.repeat(64)).ok);
 const early=attest(db.status(),1,privateKey);check(verifyAgainstTrusted(file,early,publicKey,early).ok);
 db.db.exec("VACUUM INTO '"+old.replaceAll("'","''")+"'");db.close();
 db=new SerializedAuthority(file);check(db.reserve('w0',2,'b'.repeat(64)).ok);
 const latest=attest(db.status(),2,privateKey);db.close();await saveTrusted(trustFile,latest);
 check(verifyAgainstTrusted(file,latest,publicKey,await loadTrusted(trustFile)).ok);
 const tampered={...latest,head:'f'.repeat(64)};check(verifyAgainstTrusted(file,tampered,publicKey,latest).reason==='invalid-signature');
 check(verifyAgainstTrusted(file,early,publicKey,latest).reason==='checkpoint-rollback');
 check(verifyAgainstTrusted(file,latest,publicKey,null).reason==='missing-trusted-watermark');
 await copyFile(old,file);
 check(verifyAgainstTrusted(file,latest,publicKey,latest).reason==='database-mismatch');
 check(verifyAgainstTrusted(file,early,publicKey,latest).reason==='checkpoint-rollback');
 check(verifyAgainstTrusted(file,early,publicKey,early).ok);
 const rogue=generateKeyPairSync('ed25519');check(verifyAgainstTrusted(file,early,rogue.publicKey,early).reason==='invalid-signature');
 console.log(JSON.stringify({status:'PASS_WITH_TRUST_DEPENDENCY',assertions:checks,oldSnapshotRejectedWithLatestTrusted:true,oldSnapshotAcceptedIfTrustRolledBack:true}));
}finally{await rm(root,{recursive:true,force:true});}
