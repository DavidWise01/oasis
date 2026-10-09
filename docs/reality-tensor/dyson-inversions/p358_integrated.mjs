import {verify as verifyChain, checkpoint} from './p355_chain.mjs';
import {decide} from './p357_quorum.mjs';
/** Verify every chain link, then require signed quorum and trusted ancestry. */
export function acceptVerified(records,stamp,votes,authorized,trusted){
 const chain=verifyChain(records,{length:stamp.length,head:stamp.head});
 if(!chain.ok)return {ok:false,reason:'chain-'+chain.reason};
 const quorum=decide(stamp,votes,authorized,trusted);
 if(!quorum.ok)return {ok:false,reason:quorum.reason};
 if(trusted.length>records.length)return {ok:false,reason:'short-history'};
 const ancestor=checkpoint(records.slice(0,trusted.length));
 if(ancestor.head!==trusted.head)return {ok:false,reason:'non-descendant-fork'};
 return {ok:true,trusted:{context:stamp.context,epoch:stamp.epoch,length:stamp.length,head:stamp.head},votes:quorum.votes};
}