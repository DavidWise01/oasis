'use strict';
const P=require('./baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const {JournalVerifiedBridge}=require('./baseline151/baseline150/bridge150');
const G=require('./anchor-proof152');
class AnchoredBridge extends JournalVerifiedBridge{
 async complete(txid,receipt,journalProof,anchorProof){
  if(receipt?.body?.txid!==txid)throw Error('WRONG_RECEIPT_TXID');
  const resource=this.resourcePublicKeys[receipt.body.resourceId];
  if(!resource||!P.verify(resource,'S148:RECEIPT',receipt.body,receipt.signature))throw Error('RESOURCE_RECEIPT_UNTRUSTED');
  if(anchorProof?.schema!==G.SCHEMA)throw Error('ANCHOR_PROOF_REQUIRED');
  const head=await this.state();
  if(head.rows.filter(x=>x.response?.body.pendingGrant?.txid===txid).length<2)throw Error('RECEIPT_NO_PENDING_QUORUM');
  return this.run({type:'COMPLETE',txid,receiptHash:P.sha(receipt),receipt,journalProof,anchorProof});
 }
}
module.exports={AnchoredBridge};
