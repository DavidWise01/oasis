import {lstat,unlink} from 'node:fs/promises';
import {createConnection} from 'node:net';
export async function prepareSocket(path,{expectedUid=process.getuid?.(),timeoutMs=350}={}) {
  let item;
  try{item=await lstat(path)}catch(e){if(e.code==='ENOENT')return {ok:true,action:'absent'};return {ok:false,reason:'unreadable-path'};}
  if(!item.isSocket())return {ok:false,reason:'path-not-socket'};
  if(expectedUid!==undefined && item.uid!==expectedUid)return {ok:false,reason:'owner-mismatch'};
  const outcome=await new Promise(resolve=>{
    const sock=createConnection(path);let finished=false;
    const done=result=>{if(finished)return;finished=true;sock.destroy();resolve(result)};
    sock.once('connect',()=>done('active'));
    sock.once('error',e=>done(e.code==='ECONNREFUSED'?'refused':'indeterminate'));
    sock.setTimeout(timeoutMs,()=>done('indeterminate'));
  });
  if(outcome!=='refused')return {ok:false,reason:outcome==='active'?'active-listener':'indeterminate-owner'};
  let current;
  try{current=await lstat(path)}catch{return {ok:false,reason:'changed-during-check'}};
  if(!current.isSocket()||current.ino!==item.ino||current.dev!==item.dev||current.uid!==item.uid)return {ok:false,reason:'changed-during-check'};
  await unlink(path);
  return {ok:true,action:'reclaimed-refused-socket'};
}