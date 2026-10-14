/** Run locally on the provisioning computer. NO private keys ship in the release zip.
 * Requires installed OpenSSL to generate signed TLS client/server certs.
 */
import {generateKeyPairSync} from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
const root=path.resolve(process.argv[2]||'./oasis-keys');
for(const folder of ['root-private','server','client'])fs.mkdirSync(path.join(root,folder),{recursive:true,mode:0o700});
function cmd(...args){const out=spawnSync('openssl',args,{encoding:'utf8'});if(out.status!==0)throw Error(`OpenSSL ${args.join(' ')} failed: ${out.stderr||out.error}`)}
const p=(folder,f)=>path.join(root,folder,f);
cmd('genpkey','-algorithm','ED25519','-out',p('root-private','ca.key'));
cmd('req','-x509','-new','-key',p('root-private','ca.key'),'-out',p('root-private','ca.crt'),'-days','365','-subj','/CN=OASIS Private CA');
const names=[['server','oasis.local','subjectAltName=DNS:oasis.local'],['client','oasis-client','extendedKeyUsage=clientAuth']];
for(const [role,cn,ext] of names){
  cmd('genpkey','-algorithm','ED25519','-out',p(role,`${role}.key`));
  cmd('req','-new','-key',p(role,`${role}.key`),'-out',p(role,`${role}.csr`),'-subj',`/CN=${cn}`);
  const extFile=p(role,'extensions.cnf');fs.writeFileSync(extFile,`${role==='server'?'extendedKeyUsage=serverAuth\n':''}${ext}\n`);
  cmd('x509','-req','-in',p(role,`${role}.csr`),'-CA',p('root-private','ca.crt'),'-CAkey',p('root-private','ca.key'),
    '-CAcreateserial','-out',p(role,`${role}.crt`),'-days','90','-extfile',extFile);
  fs.copyFileSync(p('root-private','ca.crt'),p(role,'ca.crt'));
  for(const name of [`${role}.key`])fs.chmodSync(p(role,name),0o600);
  fs.rmSync(p(role,`${role}.csr`));fs.rmSync(extFile);
}
const {privateKey,publicKey}=generateKeyPairSync('ed25519');
fs.writeFileSync(p('client','sender.private.pem'),privateKey.export({type:'pkcs8',format:'pem'}),{mode:0o600});
fs.writeFileSync(p('server','sender.pub.pem'),publicKey.export({type:'spki',format:'pem'}));
for(const name of ['ca.key'])fs.chmodSync(p('root-private',name),0o600);
console.log(`KEYS GENERATED: ${root}\nCopy server/ only to receiver, client/ only to sender. Keep root-private/ OFF both devices.\nNever upload private keys, journal or cert material to GitHub.`);