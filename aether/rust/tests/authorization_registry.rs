#![cfg(target_os="linux")]
use aether_evidence::{PublicJwk,durable_ledger::{append,inspect,Event,GENESIS},
 recovery_checkpoint::{self,Checkpoint,SignedCheckpoint,RecoveryPolicy,CHECKPOINT_SCHEMA},
 external_custody::{self,Admission,Packet as CustodyPacket,Policy as CustodyPolicy},
 custody_commit::{self,SignedTransition,TransitionIntent,TransitionPolicy,SCHEMA},
 authorization_registry::{self,SignedAmendment,RevocationAmendment,AmendmentPolicy}};
use base64::{engine::general_purpose::URL_SAFE_NO_PAD,Engine as _};
use p256::ecdsa::{signature::Signer,Signature,SigningKey};
use std::{collections::HashSet,fs,path::PathBuf,sync::atomic::{AtomicUsize,Ordering}};
static NEXT:AtomicUsize=AtomicUsize::new(0);
struct Tmp{root:PathBuf,path:PathBuf}
impl Tmp{
 fn new()->Self{
  let root=std::env::temp_dir().join(format!("aether206-{}-{}",std::process::id(),NEXT.fetch_add(1,Ordering::SeqCst)));
  fs::create_dir_all(&root).unwrap();let path=root.join("ledger.jsonl");Self{root,path}
 }
}
impl Drop for Tmp{fn drop(&mut self){let _=fs::remove_dir_all(&self.root);}}
fn key(n:u8)->SigningKey{SigningKey::from_slice(&[n;32]).unwrap()}
fn jwk(k:&SigningKey)->PublicJwk{
 let point=k.verifying_key().to_encoded_point(false);let bytes=point.as_bytes();
 PublicJwk{kty:"EC".into(),crv:"P-256".into(),x:URL_SAFE_NO_PAD.encode(&bytes[1..33]),y:URL_SAFE_NO_PAD.encode(&bytes[33..65])}
}
fn sign<T:serde::Serialize>(k:&SigningKey,v:&T)->String{
 let sig:Signature=k.sign(&serde_json::to_vec(v).unwrap());hex::encode(sig.to_bytes())
}
fn event(n:u32)->Event{
 Event{event_id:format!("event{n}"),capture_sha256:format!("{n:064x}"),
 challenge_nonce:format!("nonce{n}"),review_id:format!("review{n}"),
 payload_sha256:format!("{:064x}",n+1200)}
}
struct Fixture{
 tmp:Tmp,checkpoint:SignedCheckpoint,recovery:RecoveryPolicy,
 custody:CustodyPacket,custody_policy:CustodyPolicy,
 signed:SignedTransition,policy:TransitionPolicy,
 head:String,count:u64,ev:Event,
}
fn fixture()->Fixture{
 let tmp=Tmp::new();let mut s=inspect(&tmp.path).unwrap();
 for i in 1..=2{s=append(&tmp.path,event(i),&s.head_sha256,s.entries).unwrap();}
 let issuer=key(81);let holder=key(82);let rotation=key(83);
 let ik=jwk(&issuer);let hk=jwk(&holder);let rk=jwk(&rotation);
 let checkpoint_record=Checkpoint{
 schema:CHECKPOINT_SCHEMA.into(),checkpoint_id:"CHECK-206".into(),holder_id:"H206".into(),
 holder_root:"HOLDER-ROOT".into(),holder_operator:"HOLDER-OP".into(),
 holder_administrator:"HOLDER-ADMIN".into(),source_root:"SOURCE-ROOT".into(),
 source_operator:"SOURCE-OP".into(),source_administrator:"SOURCE-ADMIN".into(),
 ledger_id:"LEDGER-206".into(),sequence:2,head_sha256:s.head_sha256.clone(),
 predecessor_checkpoint_sha256:"a".repeat(64),challenge_nonce:"CHECK-NONCE-206".into()};
 let checkpoint=SignedCheckpoint{signature_hex:sign(&holder,&checkpoint_record),record:checkpoint_record};
 let recovery=RecoveryPolicy{
 expected_ledger_id:"LEDGER-206".into(),expected_holder_id:"H206".into(),
 expected_holder_root:"HOLDER-ROOT".into(),
 pinned_holder_key_sha256:recovery_checkpoint::public_key_fingerprint(&hk),
 expected_checkpoint_sha256:recovery_checkpoint::checkpoint_hash(&checkpoint.record),
 expected_predecessor_checkpoint_sha256:"a".repeat(64),
 holder_public_key:hk.clone(),holder_out_of_band_authenticated:true,
 external_checkpoint_custody_verified:true,seen_checkpoint_ids:HashSet::new(),
 seen_challenge_nonces:HashSet::new()};
 let admission=Admission{
 schema:external_custody::SCHEMA.into(),admission_id:"AD206".into(),
 checkpoint_sha256:recovery_checkpoint::checkpoint_hash(&checkpoint.record),
 ledger_id:"LEDGER-206".into(),holder_id:"H206".into(),holder_root:"HOLDER-ROOT".into(),
 holder_operator:"HOLDER-OP".into(),holder_admin:"HOLDER-ADMIN".into(),holder_key:hk.clone(),
 issuer_id:"I206".into(),issuer_root:"ISSUER-ROOT".into(),issuer_operator:"ISSUER-OP".into(),
 issuer_admin:"ISSUER-ADMIN".into(),source_root:"SOURCE-ROOT".into(),
 source_operator:"SOURCE-OP".into(),source_admin:"SOURCE-ADMIN".into(),
 issuer_key_id:"ISSUER-KEY-206".into(),authorization_nonce:"AD-NONCE-206".into(),
 policy_epoch:1,previous_holder_key_sha256:external_custody::fingerprint(&hk),
 rotation_approval_sha256:String::new()};
 let custody=CustodyPacket{
 issuer_signature_hex:sign(&issuer,&admission),
 holder_signature_hex:sign(&holder,&admission),admission,
 rotation:None,rotation_signature_hex:None};
 let custody_policy=CustodyPolicy{
 ledger_id:"LEDGER-206".into(),checkpoint_sha256:recovery_checkpoint::checkpoint_hash(&checkpoint.record),
 holder_id:"H206".into(),issuer_id:"I206".into(),issuer_key_id:"ISSUER-KEY-206".into(),
 pinned_issuer_key_sha256:external_custody::fingerprint(&ik),
 pinned_holder_key_sha256:external_custody::fingerprint(&hk),
 pinned_rotation_key_sha256:external_custody::fingerprint(&rk),
 issuer_key:ik.clone(),rotation_key:rk,
 previous_holder_key_sha256:external_custody::fingerprint(&hk),
 expected_policy_epoch:1,required_nonce:"AD-NONCE-206".into(),
 issuer_externally_authenticated:true,holder_externally_authenticated:true,
 rotation_authority_externally_authenticated:false,
 revoked_key_sha256:HashSet::new(),used_admission_ids:HashSet::new(),
 used_rotation_ids:HashSet::new(),used_nonces:HashSet::new()};
 let ev=event(3);
 let intent=TransitionIntent{
 schema:SCHEMA.into(),authorization_id:"TX206".into(),ledger_id:"LEDGER-206".into(),
 checkpoint_sha256:recovery_checkpoint::checkpoint_hash(&checkpoint.record),
 custody_admission_sha256:external_custody::admission_hash(&custody.admission),
 expected_head_sha256:s.head_sha256.clone(),expected_entries:2,next_sequence:3,
 event_sha256:custody_commit::event_hash(&ev),event_id:ev.event_id.clone(),
 capture_sha256:ev.capture_sha256.clone(),challenge_nonce:ev.challenge_nonce.clone(),
 review_id:ev.review_id.clone(),payload_sha256:ev.payload_sha256.clone(),
 authorization_nonce:"TX-NONCE-206".into(),
 holder_key_sha256:external_custody::fingerprint(&hk),
 issuer_key_sha256:external_custody::fingerprint(&ik)};
 let signed=SignedTransition{issuer_signature_hex:sign(&issuer,&intent),
 holder_signature_hex:sign(&holder,&intent),intent};
 let policy=TransitionPolicy{
 expected_authorization_id:"TX206".into(),expected_authorization_nonce:"TX-NONCE-206".into(),
 expected_intent_sha256:custody_commit::intent_hash(&signed.intent),
 pinned_issuer_key_sha256:external_custody::fingerprint(&ik),
 pinned_holder_key_sha256:external_custody::fingerprint(&hk),
 seen_authorization_ids:HashSet::new(),seen_authorization_nonces:HashSet::new(),
 seen_intent_hashes:HashSet::new()};
 authorization_registry::initialize(&tmp.path,"LEDGER-206",&policy.pinned_issuer_key_sha256,
  &policy.pinned_holder_key_sha256,1).unwrap();
 Fixture{tmp,checkpoint,recovery,custody,custody_policy,signed,policy,
 head:s.head_sha256,count:2,ev}
}
fn run(f:&Fixture)->Result<aether_evidence::durable_ledger::State,String>{
 authorization_registry::append_registered(&f.tmp.path,f.ev.clone(),&f.head,f.count,
 &f.checkpoint,&f.recovery,&f.custody,&f.custody_policy,&f.signed,&f.policy)
}
fn reject<F:FnOnce(&mut Fixture)>(reason:&str,edit:F){
 let mut f=fixture();edit(&mut f);let error=run(&f).unwrap_err();
 assert!(error.contains(reason),"expected {reason}, got {error}");
 assert_eq!(inspect(&f.tmp.path).unwrap().entries,2);
}
#[test]fn signed_transition_commits_with_one_guard(){
 let f=fixture();let state=run(&f).unwrap();
 assert_eq!(state.entries,3);assert_eq!(state.operational_authority,"HOLD");
 assert!(!state.physical_act_allowed);
 assert_eq!(inspect(&f.tmp.path).unwrap().head_sha256,state.head_sha256);
 assert!(!f.tmp.path.with_extension("lock").exists());
}
#[test]fn documentary_signatures_do_not_grant_physical_act(){
 let f=fixture();let r=custody_commit::assess_transition(&f.signed,&f.policy,&f.ev,&f.head,f.count,&f.checkpoint,&f.custody,&f.custody_policy);
 assert!(r.may_commit);assert!(!r.physical_act_allowed);assert_eq!(r.physical_qualification_percent,0);
}
#[test]fn concurrent_lock_blocks_writer(){
 let f=fixture();let guard=aether_evidence::process_liveness::acquire(&f.tmp.path.with_extension("lock")).unwrap();
 assert!(run(&f).unwrap_err().contains("LOCK_UNAVAILABLE_FAIL_CLOSED"));drop(guard);
}
#[test]fn stale_head_blocks(){reject("STALE_REGISTRY_ADMISSION_HEAD",|f|f.head=GENESIS.into());}
#[test]fn stale_sequence_blocks(){reject("STALE_REGISTRY_ADMISSION_HEAD",|f|f.count=1);}
#[test]fn prior_writer_advances_head(){
 let f=fixture();append(&f.tmp.path,event(4),&f.head,f.count).unwrap();
 assert_eq!(run(&f).unwrap_err(),"REGISTRY_LEDGER_DIVERGENCE_HOLD");
}
#[test]fn replaced_event_rejected(){reject("EVENT_NOT_BOUND_TO_AUTHORIZATION",|f|f.ev=event(5));}
#[test]fn altered_intent_event_hash(){reject("EXTERNAL_INTENT_PIN_MISMATCH",|f|f.signed.intent.event_sha256="f".repeat(64));}
#[test]fn changed_next_sequence(){reject("STALE_OR_REORDERED_TRANSITION_HEAD",|f|f.signed.intent.next_sequence=4);}
#[test]fn wrong_ledger_id(){reject("LEDGER_BINDING_MISMATCH",|f|f.signed.intent.ledger_id="OTHER".into());}
#[test]fn mismatched_checkpoint_bind(){reject("CHECKPOINT_OR_CUSTODY_ADMISSION_MISMATCH",|f|f.signed.intent.checkpoint_sha256="f".repeat(64));}
#[test]fn changed_admission_hash(){reject("CHECKPOINT_OR_CUSTODY_ADMISSION_MISMATCH",|f|f.signed.intent.custody_admission_sha256="f".repeat(64));}
#[test]fn forged_transition_issuer(){reject("TRANSITION_ISSUER_SIGNATURE_INVALID",|f|f.signed.issuer_signature_hex="00".repeat(64));}
#[test]fn forged_transition_holder(){reject("TRANSITION_HOLDER_SIGNATURE_INVALID",|f|f.signed.holder_signature_hex="00".repeat(64));}
#[test]fn replay_authorization_id(){let f=fixture();run(&f).unwrap();assert!(run(&f).unwrap_err().contains("STALE_REGISTRY_ADMISSION_HEAD"));}
#[test]fn replay_authorization_nonce(){let f=fixture();run(&f).unwrap();assert!(run(&f).unwrap_err().contains("STALE_REGISTRY_ADMISSION_HEAD"));}
#[test]fn revoked_holder_blocks_commit(){reject("CALLER_REVOCATION_REGISTRY_DIVERGENCE",|f|{f.custody_policy.revoked_key_sha256.insert(f.policy.pinned_holder_key_sha256.clone());});}
#[test]fn revoked_issuer_blocks_commit(){reject("REVOKED_ISSUER_OR_HOLDER",|f|{f.custody_policy.revoked_key_sha256.insert(f.policy.pinned_issuer_key_sha256.clone());});}
#[test]fn reused_custody_admission(){let f=fixture();run(&f).unwrap();assert!(run(&f).unwrap_err().contains("STALE_REGISTRY_ADMISSION_HEAD"));}
#[test]fn unauthenticated_holder_blocks(){reject("EXTERNAL_ORIGIN_UNAUTHENTICATED",|f|f.custody_policy.holder_externally_authenticated=false);}
#[test]fn unauthenticated_checkpoint_blocks(){reject("EXTERNAL_CHECKPOINT_CUSTODY_UNVERIFIED",|f|f.recovery.external_checkpoint_custody_verified=false);}
#[test]fn torn_tail_blocks(){let f=fixture();use std::io::Write;let mut file=fs::OpenOptions::new().append(true).open(&f.tmp.path).unwrap();file.write_all(b"partial").unwrap();assert!(run(&f).unwrap_err().contains("LEDGER_HOLD: TORN_TAIL"));}
#[test]fn reused_event_after_first_commit(){let f=fixture();run(&f).unwrap();assert!(run(&f).is_err());assert_eq!(inspect(&f.tmp.path).unwrap().entries,3);}
#[test]fn lock_orphan_blocks(){let f=fixture();fs::write(f.tmp.path.with_extension("lock"),b"orphan").unwrap();assert!(run(&f).unwrap_err().contains("LOCK_UNAVAILABLE_FAIL_CLOSED"));}

fn revocation(f:&Fixture)->(SignedAmendment,AmendmentPolicy){
 let key=key(84);let public=jwk(&key);
 let a=RevocationAmendment{schema:"AETHER-207/revocation-v1".into(),
  amendment_id:"AMEND207".into(),ledger_id:"LEDGER-206".into(),
  ledger_head_sha256:f.head.clone(),prior_epoch:1,next_epoch:2,
  authority_root:"EXTERNAL-REVOCATION-ROOT".into(),
  authority_operator:"EXTERNAL-REVOCATION-OP".into(),
  authority_admin:"EXTERNAL-REVOCATION-ADMIN".into(),
  issuer_root:"ISSUER-ROOT".into(),issuer_operator:"ISSUER-OP".into(),
  issuer_admin:"ISSUER-ADMIN".into(),holder_root:"HOLDER-ROOT".into(),
  holder_operator:"HOLDER-OP".into(),holder_admin:"HOLDER-ADMIN".into(),
  newly_revoked_key_sha256:vec!["e".repeat(64)]};
 let signature_hex=sign(&key,&a);
 let packet=SignedAmendment{amendment:a,signature_hex};
 let policy=AmendmentPolicy{
  pinned_authority_key_sha256:external_custody::fingerprint(&public),
  authority_key:public,authority_root_authenticated_out_of_band:true};
 (packet,policy)
}
#[test]fn registry_inspection_at_genesis_anchor(){
 let f=fixture();let r=authorization_registry::inspect(&f.tmp.path).unwrap();
 assert_eq!(r.ledger_entries,2);assert_eq!(r.registry_epoch,1);
 assert_eq!(r.ledger_head_sha256,f.head);assert!(!r.physical_act_allowed);
}
#[test]fn registry_persisted_through_restart_simulation(){
 let f=fixture();let result=run(&f).unwrap();
 let readback=authorization_registry::inspect(&f.tmp.path).unwrap();
 assert_eq!(readback.ledger_entries,3);assert_eq!(readback.ledger_head_sha256,result.head_sha256);
 assert!(!readback.physical_act_allowed);
}
#[test]fn duplicate_registry_creation_refused(){
 let f=fixture();
 assert!(authorization_registry::initialize(&f.tmp.path,"LEDGER-206",
  &f.policy.pinned_issuer_key_sha256,&f.policy.pinned_holder_key_sha256,1)
  .unwrap_err().contains("REGISTRY_ALREADY_EXISTS_OR_PENDING"));
}
#[test]fn missing_registry_refused(){
 let f=fixture();fs::remove_file(authorization_registry::registry_path(&f.tmp.path)).unwrap();
 assert!(run(&f).unwrap_err().contains("REGISTRY_MISSING_OR_UNREADABLE"));
}
#[test]fn corrupted_registry_refused(){
 let f=fixture();fs::write(authorization_registry::registry_path(&f.tmp.path),b"bad-json").unwrap();
 assert_eq!(run(&f).unwrap_err(),"REGISTRY_CORRUPT_JSON");
}
#[test]fn stale_registry_head_refused(){
 let f=fixture();let path=authorization_registry::registry_path(&f.tmp.path);
 let mut data:serde_json::Value=serde_json::from_slice(&fs::read(&path).unwrap()).unwrap();
 data["ledger_head_sha256"]=serde_json::json!("f".repeat(64));
 fs::write(&path,serde_json::to_vec(&data).unwrap()).unwrap();
 assert_eq!(run(&f).unwrap_err(),"REGISTRY_LEDGER_DIVERGENCE_HOLD");
}
#[test]fn rolled_back_registry_entries_refused(){
 let f=fixture();let path=authorization_registry::registry_path(&f.tmp.path);
 let mut data:serde_json::Value=serde_json::from_slice(&fs::read(&path).unwrap()).unwrap();
 data["ledger_entries"]=serde_json::json!(1u64);
 fs::write(&path,serde_json::to_vec(&data).unwrap()).unwrap();
 assert_eq!(run(&f).unwrap_err(),"REGISTRY_LEDGER_DIVERGENCE_HOLD");
}
#[test]fn pending_transaction_file_blocks_append(){
 let f=fixture();let path=f.tmp.path.with_extension("registry.pending");
 fs::write(&path,b"interrupted").unwrap();
 assert_eq!(run(&f).unwrap_err(),"REGISTRY_PENDING_TRANSACTION_HOLD");
}
#[test]fn altered_epoch_refused(){
 let f=fixture();let path=authorization_registry::registry_path(&f.tmp.path);
 let mut data:serde_json::Value=serde_json::from_slice(&fs::read(&path).unwrap()).unwrap();
 data["revocation_epoch"]=serde_json::json!(7u64);
 fs::write(&path,serde_json::to_vec(&data).unwrap()).unwrap();
 assert_eq!(run(&f).unwrap_err(),"REGISTRY_EPOCH_MISMATCH");
}
#[test]fn altered_holder_pin_refused(){
 let f=fixture();let path=authorization_registry::registry_path(&f.tmp.path);
 let mut data:serde_json::Value=serde_json::from_slice(&fs::read(&path).unwrap()).unwrap();
 data["pinned_holder_key_sha256"]=serde_json::json!("f".repeat(64));
 fs::write(&path,serde_json::to_vec(&data).unwrap()).unwrap();
 assert_eq!(run(&f).unwrap_err(),"REGISTRY_PIN_MISMATCH");
}
#[test]fn signed_revocation_changes_persistent_epoch(){
 let f=fixture();let(a,p)=revocation(&f);
 let s=authorization_registry::apply_signed_revocation(&f.tmp.path,&a,&p).unwrap();
 assert_eq!(s.registry_epoch,2);
 assert_eq!(authorization_registry::inspect(&f.tmp.path).unwrap().registry_epoch,2);
 assert_eq!(run(&f).unwrap_err(),"REGISTRY_EPOCH_MISMATCH");
}
#[test]fn repeated_signed_revocation_amendment_refused(){
 let f=fixture();let(a,p)=revocation(&f);
 authorization_registry::apply_signed_revocation(&f.tmp.path,&a,&p).unwrap();
 assert_eq!(authorization_registry::apply_signed_revocation(&f.tmp.path,&a,&p).unwrap_err(),
  "REVOCATION_EPOCH_OR_HEAD_MISMATCH");
}
#[test]fn invalid_revocation_signature_refused(){
 let f=fixture();let(mut a,p)=revocation(&f);a.signature_hex="00".repeat(64);
 assert_eq!(authorization_registry::apply_signed_revocation(&f.tmp.path,&a,&p).unwrap_err(),
  "REVOCATION_SIGNATURE_INVALID");
}
#[test]fn independent_revocation_pin_required(){
 let f=fixture();let(a,mut p)=revocation(&f);p.pinned_authority_key_sha256="f".repeat(64);
 assert_eq!(authorization_registry::apply_signed_revocation(&f.tmp.path,&a,&p).unwrap_err(),
  "REVOCATION_AUTHORITY_KEY_PIN_MISMATCH");
}
#[test]fn revocation_root_shared_with_holder_refused(){
 let f=fixture();let(mut a,p)=revocation(&f);a.amendment.authority_root="HOLDER-ROOT".into();
 assert_eq!(authorization_registry::apply_signed_revocation(&f.tmp.path,&a,&p).unwrap_err(),
  "REVOCATION_AUTHORITY_NOT_SEPARATE");
}
#[test]fn revocation_requires_out_of_band_origin(){
 let f=fixture();let(a,mut p)=revocation(&f);p.authority_root_authenticated_out_of_band=false;
 assert_eq!(authorization_registry::apply_signed_revocation(&f.tmp.path,&a,&p).unwrap_err(),
  "REVOCATION_AUTHORITY_EXTERNAL_ORIGIN_UNAUTHENTICATED");
}
#[test]fn no_unsigned_revocation_toggle(){
 assert_eq!(authorization_registry::stage_revocation_unsupported().unwrap_err(),
 "REVOCATION_AMENDMENT_REQUIRES_INDEPENDENT_SIGNED_AUTHORITY");
}
