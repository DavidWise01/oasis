//! AETHER-214-RS: cross-host receipt equivocation and declared-controller analysis.
//! Signed hosts are documentary witnesses, not proof of independent custody.
//! Conflicting claims are preserved, never resolved by vote or a timestamp.
use crate::{sha256_hex,PublicJwk};
use crate::custody_ancestry::{SourceAncestry,WitnessPin};
use p256::ecdsa::{signature::Verifier,Signature};
use serde::{Serialize,Deserialize};
use std::collections::{BTreeMap,BTreeSet};
pub const SCHEMA:&str="AETHER-214/host-receipt-v1";
#[derive(Clone,Debug,Serialize,Deserialize)]
pub struct HostReceipt{
 pub schema:String,pub receipt_id:String,pub witness_id:String,
 pub corpus_id:String,pub ledger_id:String,pub sequence:u64,
 pub head_sha256:String,pub predecessor_sha256:String,
 pub registry_sha256:String,pub registry_epoch:u64,
 pub witness_root:String,pub witness_operator:String,
 pub witness_administrator:String,pub witness_host:String,
 pub key_sha256:String,pub claimed_timestamp:String,
}
#[derive(Clone,Debug,Serialize,Deserialize)]
pub struct SignedHostReceipt{pub record:HostReceipt,pub signature_hex:String}
#[derive(Clone,Debug,Serialize,Deserialize)]
pub struct Policy{
 pub expected_corpus_id:String,pub expected_ledger_id:String,
 pub source:SourceAncestry,pub witnesses:Vec<WitnessPin>,
 pub required_witnesses:usize,
}
#[derive(Clone,Debug,Serialize,Deserialize)]
pub struct Conflict{
 pub kind:String,pub sequence:u64,
 pub receipt_ids:Vec<String>,pub distinct_claims:Vec<String>,
}
#[derive(Clone,Debug,Serialize,Deserialize)]
pub struct Decision{
 pub verdict:String,pub reasons:Vec<String>,pub conflicts:Vec<Conflict>,
 pub valid_signatures:usize,pub declared_distinct_hosts:usize,
 pub independently_authenticated_external_witnesses:u64,
 pub may_choose_history:bool,pub may_recover:bool,
 pub physical_qualification_percent:u8,pub operational_authority:String,
 pub physical_act_allowed:bool,
}
pub fn canonical<T:Serialize>(x:&T)->Vec<u8>{serde_json::to_vec(x).unwrap_or_default()}
pub fn hash<T:Serialize>(x:&T)->String{sha256_hex(&canonical(x))}
fn hex64(s:&str)->bool{s.len()==64&&s.bytes().all(|x|x.is_ascii_hexdigit())}
fn verify(packet:&SignedHostReceipt,key:&PublicJwk)->bool{
 let Ok(k)=crate::verifying_key(key)else{return false};
 let Ok(bytes)=hex::decode(&packet.signature_hex)else{return false};
 let Ok(sig)=Signature::from_slice(&bytes)else{return false};
 k.verify(&canonical(&packet.record),&sig).is_ok()
}
pub fn assess(receipts:&[SignedHostReceipt],policy:&Policy)->Decision{
 let mut faults=BTreeSet::new();
 let mut fail=|s:&str|{faults.insert(s.to_string());};
 if receipts.len()!=3||policy.witnesses.len()!=3||policy.required_witnesses!=3{
  fail("THREE_WITNESS_ENVELOPE_REQUIRED");
 }
 if policy.source.corpus_id!=policy.expected_corpus_id||
 policy.source.controlling_root.is_empty()||
 policy.source.operator_id.is_empty()||policy.source.administrator_id.is_empty(){
  fail("SOURCE_ANCESTRY_INVALID");
 }
 let mut witness_ids=BTreeSet::new();let mut receipt_ids=BTreeSet::new();
 let mut roots=BTreeSet::new();let mut operators=BTreeSet::new();
 let mut admins=BTreeSet::new();let mut hosts=BTreeSet::new();
 let mut keys=BTreeSet::new();let mut valid=0;
 let pin_by_id:BTreeMap<&str,&WitnessPin>=policy.witnesses.iter()
  .map(|p|(p.witness_id.as_str(),p)).collect();
 if pin_by_id.len()!=policy.witnesses.len(){fail("DUPLICATE_PINNED_WITNESS");}
 for packet in receipts{
  let r=&packet.record;
  if r.schema!=SCHEMA||r.receipt_id.trim().is_empty()||
   r.witness_id.trim().is_empty()||r.sequence==0||
   !hex64(&r.head_sha256)||!hex64(&r.predecessor_sha256)||
   !hex64(&r.registry_sha256)||r.registry_epoch==0{
   fail("RECEIPT_FIELDS_INVALID");
  }
  if r.corpus_id!=policy.expected_corpus_id||r.ledger_id!=policy.expected_ledger_id{
   fail("SOURCE_OR_LEDGER_BINDING_MISMATCH");
  }
  if !receipt_ids.insert(r.receipt_id.as_str())||
   !witness_ids.insert(r.witness_id.as_str()){
   fail("DUPLICATE_RECEIPT_OR_WITNESS");
  }
  if r.witness_root.is_empty()||r.witness_operator.is_empty()||
   r.witness_administrator.is_empty()||r.witness_host.is_empty(){
   fail("WITNESS_ANCESTRY_MISSING");
  }
  if r.witness_root==policy.source.controlling_root||
   r.witness_operator==policy.source.operator_id||
   r.witness_administrator==policy.source.administrator_id{
   fail("OWNED_SOURCE_MIRROR_OR_SHARED_CONTROL");
  }
  roots.insert(r.witness_root.as_str());
  operators.insert(r.witness_operator.as_str());
  admins.insert(r.witness_administrator.as_str());
  hosts.insert(r.witness_host.as_str());
  keys.insert(r.key_sha256.as_str());
  match pin_by_id.get(r.witness_id.as_str()){
   Some(pin)=>{
    if pin.expected_root!=r.witness_root||
     !hex64(&pin.public_key_sha256)||
     pin.public_key_sha256!=hash(&pin.public_key)||
     pin.public_key_sha256!=r.key_sha256{
     fail("HOST_KEY_OR_ROOT_PIN_MISMATCH");
    }
    if !pin.independently_enrolled||!pin.independent_receipt_retention_verified{
     fail("EXTERNAL_HOST_CUSTODY_UNVERIFIED");
    }
    if verify(packet,&pin.public_key){valid+=1;}else{fail("HOST_SIGNATURE_INVALID");}
   },
   None=>fail("UNRECOGNIZED_WITNESS"),
  }
 }
 if roots.len()!=3||operators.len()!=3||admins.len()!=3||
  hosts.len()!=3||keys.len()!=3{
  fail("SHARED_WITNESS_CONTROL_ANCESTRY");
 }
 // Compare every pair, not only adjacent input positions. Retain all claims.
 let mut conflicts=Vec::new();
 for i in 0..receipts.len(){
  for j in i+1..receipts.len(){
   let a=&receipts[i].record;let b=&receipts[j].record;
   if a.ledger_id==b.ledger_id&&a.sequence==b.sequence{
    let mut kinds=Vec::new();
    if a.head_sha256!=b.head_sha256{kinds.push("SAME_SEQUENCE_DIFFERENT_HEAD");}
    if a.predecessor_sha256!=b.predecessor_sha256{kinds.push("SAME_SEQUENCE_DIFFERENT_PREDECESSOR");}
    if a.registry_sha256!=b.registry_sha256||
       a.registry_epoch!=b.registry_epoch{kinds.push("SAME_SEQUENCE_DIFFERENT_REGISTRY");}
    for kind in kinds{
     conflicts.push(Conflict{kind:kind.into(),sequence:a.sequence,
      receipt_ids:vec![a.receipt_id.clone(),b.receipt_id.clone()],
      distinct_claims:vec![hash(a),hash(b)]});
    }
   }else if a.ledger_id==b.ledger_id&&
      a.sequence.abs_diff(b.sequence)==1{
    let (older,newer)=if a.sequence<b.sequence{(a,b)}else{(b,a)};
    if newer.predecessor_sha256!=older.head_sha256{
     conflicts.push(Conflict{kind:"ADJACENT_SEQUENCE_FORK".into(),
      sequence:newer.sequence,receipt_ids:vec![older.receipt_id.clone(),newer.receipt_id.clone()],
      distinct_claims:vec![older.head_sha256.clone(),newer.predecessor_sha256.clone()]});
    }
    if newer.registry_epoch<older.registry_epoch{
     conflicts.push(Conflict{kind:"REGISTRY_EPOCH_REWIND".into(),
      sequence:newer.sequence,receipt_ids:vec![older.receipt_id.clone(),newer.receipt_id.clone()],
      distinct_claims:vec![older.registry_epoch.to_string(),newer.registry_epoch.to_string()]});
    }
   }
  }
 }
 conflicts.sort_by(|a,b|(&a.sequence,&a.kind,&a.receipt_ids).cmp(&(&b.sequence,&b.kind,&b.receipt_ids)));
 if !conflicts.is_empty(){fail("CROSS_HOST_EQUIVOCATION_UNRESOLVED");}
 let reasons=faults.into_iter().collect::<Vec<_>>();
 Decision{
  verdict:if reasons.is_empty(){"DOCUMENTARY_CROSS_HOST_CLAIMS_CONSISTENT"}
  else{"REJECT"}.into(),reasons,conflicts,
  valid_signatures:valid,declared_distinct_hosts:hosts.len(),
  independently_authenticated_external_witnesses:0,
  may_choose_history:false,may_recover:false,physical_qualification_percent:0,
  operational_authority:"HOLD".into(),physical_act_allowed:false,
 }
}
