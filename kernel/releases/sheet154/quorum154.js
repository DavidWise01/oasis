'use strict';
const fs=require('node:fs');
const P=require('./baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const {verifyGrant}=require('./baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/proof148');
const {verifyStatic}=require('./baseline153/proof153');
const SCHEMA='oasis.sheet154.intent.v1';
class QuorumFinality{
 constructor({identity,replicas,publicKeys,resourcePub,anchorPub,anchor,authorityKeys}){Object.assign(this,{identity,replicas,publicKeys,resourcePub:fs.readFileSync(resourcePub),anchorPub:fs.readFileSync(anchorPub),anchor,authorityKeys});}
 async ask(id,path,body={}){const x=this.replicas[id];return P.rpc({port:x.port,key:this.identity.key,cert:this.identity.cert,ca:this.identity.ca,serverPin:x.certPin},path,body);}
 async quorum(path,body,phase){const rows=await Promise.all(Object.keys(this.replicas).map(async id=>{try{return{ id, v:await this.ask(id,path,body)};}catch(e){return{id,error:e.message};}}));const good=[];for(const x of rows){const b=x.v?.body;if(b?.nodeId===x.id&&b.phase===phase&&b.intentDigest===P.sha(body.intent)&&P.verify(this.publicKeys[x.id],`S154:${phase==='prepare'?'PREPARE':phase==='anchor'?'ANCHORED':'FINAL'}`,b,x.v.signature))good.push(x.v);}
 if(good.length<2)throw Error('F154_NO_QUORUM_'+phase.toUpperCase()+' '+rows.filter(x=>x.error).map(x=>x.error).join('|'));return good;}
 createIntent({request,grant,receipt,store,prior}){verifyGrant(grant,request,this.authorityKeys);const checkpoint=store.checkpoint(prior),proof={record:store.find(receipt.body.txid).record,inclusion:store.ledger.inclusion(receipt.body.sequence-1)};
 return{schema:SCHEMA,txid:receipt.body.txid,request,grant,receipt,checkpoint,prior,proof};}
 async prepare(intent){return this.quorum('/prepare',{intent},'prepare');}
 async advanceAnchor(intent,votes,proof){if(votes.length<2)throw Error('F154_PREPARE_CERT_REQUIRED');return this.anchorRpc('/advance',{intent,preparedVotes:votes,proof});}
 anchorRpc(path,body={}){return P.rpc({port:this.anchor.port,key:this.identity.key,cert:this.identity.cert,ca:this.identity.ca,serverPin:this.anchor.certPin},path,body);}
 async admit(intent,preparedVotes,snapshot){return this.quorum('/anchored',{intent,preparedVotes,snapshot},'anchor');}
 async finalize(intent,preparedVotes,anchoredVotes,snapshot,completionEvidence){return this.quorum('/final',{intent,preparedVotes,anchoredVotes,snapshot,completionEvidence},'final');}
}
module.exports={QuorumFinality,SCHEMA};
