import {CrashWitness} from './p361_crash.mjs';
import {createPrivateKey,createPublicKey} from 'node:crypto';
import {readFile} from 'node:fs/promises';
const [dir,keyFile,head,epoch='12']=process.argv.slice(2);
const privateKey=createPrivateKey(await readFile(keyFile,'utf8'));
const witness=new CrashWitness(dir,new Map([['w0',createPublicKey(privateKey)]]));
const cp={context:'oasis/main',epoch:Number(epoch),length:1440,head:head.repeat(64)};
const result=await witness.vote('w0',cp,privateKey);
process.stdout.write(JSON.stringify({ok:!!result.ok,duplicate:!!result.duplicate,reason:result.reason??null})+'\n');
