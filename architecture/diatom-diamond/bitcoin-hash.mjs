/** Optional Bitcoin-inspired transport digests; not encryption or authentication.
 * Deliberately no keys, signatures, wallets, checkpoints or Bitcoin consensus use.
 */
import {createHash} from 'node:crypto';
const sha256 = bytes => createHash('sha256').update(bytes).digest();
export const MODES = Object.freeze(['none','sha256','sha256d','tagged']);
export function digestFrame(frame,mode='none') {
 if(!MODES.includes(mode)) throw new Error('invalid optional hash mode');
 if(mode==='none') return null;
 const bytes=Buffer.from(JSON.stringify(['OBS/v1.4/frame',frame]),'utf8');
 if(mode==='sha256') return sha256(bytes).toString('hex');
 if(mode==='sha256d') return sha256(sha256(bytes)).toString('hex');
 const tag=sha256(Buffer.from('OBS/v1.4/Frame','utf8'));
 return sha256(Buffer.concat([tag,tag,bytes])).toString('hex');
}
export function verifyDigest(frame,record,mode) {
 return digestFrame(frame,mode)===record;
}
