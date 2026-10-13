// Extract the exact compiled wasm32 module embedded in the offline app.
import fs from 'node:fs';
import {createHash} from 'node:crypto';
const html=fs.readFileSync(new URL('./index.html',import.meta.url),'utf8');
const b64=html.match(/const WASM_BASE64="([^"]+)"/)?.[1];
const pinned=html.match(/const WASM_SHA256="([a-f0-9]{64})"/)?.[1];
if(!b64||!pinned)throw Error('Embedded WASM not found');
const bytes=Buffer.from(b64,'base64');
const digest=createHash('sha256').update(bytes).digest('hex');
if(digest!==pinned)throw Error('WASM digest mismatch');
if(!WebAssembly.validate(bytes))throw Error('Invalid embedded wasm');
fs.writeFileSync(new URL('./ket_cellular.wasm',import.meta.url),bytes);
console.log('Extracted verified',bytes.length,'bytes, sha256',digest);
