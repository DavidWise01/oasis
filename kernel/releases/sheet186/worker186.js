'use strict';
const crypto=require('node:crypto'),fs=require('node:fs');
const T=require('../sheet176/transaction176'),R=require('../sheet173/registry173');
const [wal,keyFile,nonce,mode]=process.argv.slice(2);
const key=crypto.createPrivateKey(fs.readFileSync(keyFile));
const route=R.matrix.find(r=>r.capabilities.includes('fail-closed'));
const claims={route:route.daughter+'|'+route.cortex,op:'fail-closed',generation:1,nonce,expires:Date.now()+60000};
const req={daughter:route.daughter,cortex:route.cortex,op:'fail-closed',input:{securityFailure:false},permit:{claims,signature:crypto.sign(null,Buffer.from(JSON.stringify(claims)),key).toString('base64')}};
try {console.log(JSON.stringify(T.open(wal,crypto.createPublicKey(key)).invoke(req,mode==='prepare'?{fault:'after-prepare'}:{})));}
catch(e){console.error(e.message);process.exitCode=2;}
