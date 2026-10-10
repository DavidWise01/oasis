'use strict';
const M=require('./merkle172'),HEX=/^[a-f0-9]{64}$/;
function verifyExtension({oldRoot,newRoot,oldCount,newCount,records}) {
 if(!Array.isArray(records)||!Number.isSafeInteger(oldCount)||!Number.isSafeInteger(newCount)||oldCount<1||newCount<oldCount||records.length!==newCount||!HEX.test(oldRoot)||!HEX.test(newRoot))return false;
 return M.tree(records.slice(0,oldCount)).root===oldRoot&&M.tree(records).root===newRoot;
}
function applyCursor(state,req){
 if(!state||!req||req.resource!==state.resource||req.generation!==state.generation+1||req.previous!==state.head||req.fromRows!==state.rows||req.toRows<=req.fromRows||req.toRows!==req.records.length)throw Error('CURSOR_FORK');
 if(!verifyExtension({oldRoot:state.root,newRoot:req.root,oldCount:state.rows,newCount:req.toRows,records:req.records}))throw Error('CONSISTENCY');
 return Object.freeze({resource:state.resource,rows:req.toRows,root:req.root,generation:req.generation,head:req.nextHead});
}
module.exports={verifyExtension,applyCursor};
