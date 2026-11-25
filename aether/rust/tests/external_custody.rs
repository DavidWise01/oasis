use aether_evidence::external_custody::*;
use aether_evidence::PublicJwk;
use base64::{engine::general_purpose::URL_SAFE_NO_PAD,Engine as _};
use p256::ecdsa::{signature::Signer,Signature,SigningKey};
use std::collections::HashSet;
fn key(seed:u8)->SigningKey{SigningKey::from_slice(&[seed;32]).unwrap()}
fn jwk(k:&SigningKey)->PublicJwk{
 let point=k.verifying_key().to_encoded_point(false);let p=point.as_bytes();
 PublicJwk{kty:"EC".into(),crv:"P-256".into(),x:URL_SAFE_NO_PAD.encode(&p[1..33]),
 y:URL_SAFE_NO_PAD.encode(&p[33..65])}
}
fn signed<T:serde::Serialize>(key:&SigningKey,x:&T)->String{
 let sig:Signature=key.sign(&canonical(x));hex::encode(sig.to_bytes())
}
fn fixture()->(Packet,Policy){
 let issuer=key(71);let holder=key(72);let rotation=key(73);let holder_jwk=jwk(&holder);
 let a=Admission{schema:SCHEMA.into(),admission_id:"AD205".into(),checkpoint_sha256:"a".repeat(64),
 ledger_id:"LED205".into(),holder_id:"HOLDER205".into(),holder_root:"RH".into(),
 holder_operator:"OH".into(),holder_admin:"AH".into(),holder_key:holder_jwk.clone(),
 issuer_id:"ISSUER205".into(),issuer_root:"RI".into(),issuer_operator:"OI".into(),
 issuer_admin:"AI".into(),source_root:"RS".into(),source_operator:"OS".into(),
 source_admin:"AS".into(),issuer_key_id:"ISSUER-KEY205".into(),
 authorization_nonce:"N205".into(),policy_epoch:1,
 previous_holder_key_sha256:fingerprint(&holder_jwk),rotation_approval_sha256:"".into()};
 let packet=Packet{issuer_signature_hex:signed(&issuer,&a),
 holder_signature_hex:signed(&holder,&a),admission:a,rotation:None,rotation_signature_hex:None};
 let policy=Policy{ledger_id:"LED205".into(),checkpoint_sha256:"a".repeat(64),
 holder_id:"HOLDER205".into(),issuer_id:"ISSUER205".into(),issuer_key_id:"ISSUER-KEY205".into(),
 pinned_issuer_key_sha256:fingerprint(&jwk(&issuer)),
 pinned_holder_key_sha256:fingerprint(&holder_jwk),
 pinned_rotation_key_sha256:fingerprint(&jwk(&rotation)),
 issuer_key:jwk(&issuer),rotation_key:jwk(&rotation),
 previous_holder_key_sha256:fingerprint(&holder_jwk),expected_policy_epoch:1,
 required_nonce:"N205".into(),issuer_externally_authenticated:false,
 holder_externally_authenticated:false,rotation_authority_externally_authenticated:false,
 revoked_key_sha256:HashSet::new(),used_admission_ids:HashSet::new(),
 used_rotation_ids:HashSet::new(),used_nonces:HashSet::new()};
 (packet,policy)
}
fn fail<F:FnOnce(&mut Packet,&mut Policy)>(reason:&str,f:F){
 let(mut packet,mut policy)=fixture();f(&mut packet,&mut policy);
 let d=assess(&packet,&policy);
 assert!(d.reasons.iter().any(|v|v==reason),"expected {reason} found {:?}",d.reasons);
 assert_eq!(d.verdict,"REJECT");assert!(d.proposed_admission_id.is_none());
 assert!(!d.physical_act_allowed);assert_eq!(d.operational_authority,"HOLD");
}
fn re_sign(p:&mut Packet){p.issuer_signature_hex=signed(&key(71),&p.admission);p.holder_signature_hex=signed(&key(72),&p.admission);}
fn rotate(p:&mut Packet,policy:&mut Policy){
 let previous=policy.previous_holder_key_sha256.clone();
 let new_holder=key(74);let new_jwk=jwk(&new_holder);
 let new_hash=fingerprint(&new_jwk);
 p.admission.holder_key=new_jwk;p.admission.previous_holder_key_sha256=previous.clone();
 policy.pinned_holder_key_sha256=new_hash.clone();
 let r=RotationApproval{schema:"AETHER-205/rotation-v1".into(),approval_id:"ROT205".into(),
 admission_id:"AD205".into(),old_holder_key_sha256:previous,new_holder_key_sha256:new_hash,
 approving_root:"RR".into(),approving_operator:"OR".into(),approving_admin:"AR".into(),
 approval_nonce:"RN205".into(),epoch:1};
 p.admission.rotation_approval_sha256=rotation_hash(&r);
 p.holder_signature_hex=signed(&new_holder,&p.admission);
 p.issuer_signature_hex=signed(&key(71),&p.admission);
 p.rotation_signature_hex=Some(signed(&key(73),&r));p.rotation=Some(r);
}
#[test]fn baseline_valid_synthetic_crypto_stays_hold(){
 let(p,q)=fixture();let d=assess(&p,&q);
 assert!(d.issuer_signature_valid&&d.holder_signature_valid);
 assert_eq!(d.physical_qualification_percent,0);assert!(!d.physical_act_allowed);
}
#[test]fn asserted_external_roots_never_grant_act(){
 let(p,mut q)=fixture();q.issuer_externally_authenticated=true;q.holder_externally_authenticated=true;
 let d=assess(&p,&q);assert_eq!(d.verdict,"DOCUMENTARY_CUSTODY_ADMISSION_ONLY");
 assert!(!d.physical_act_allowed);assert_eq!(d.operational_authority,"HOLD");
}
#[test]fn admission_json_roundtrip(){let(p,_)=fixture();let b=serde_json::to_vec(&p).unwrap();let copy:Packet=serde_json::from_slice(&b).unwrap();assert_eq!(admission_hash(&p.admission),admission_hash(&copy.admission));}
#[test]fn wrong_schema(){fail("ADMISSION_SCHEMA_INVALID",|p,_|p.admission.schema="OTHER".into());}
#[test]fn wrong_nonce(){fail("ADMISSION_NONCE_OR_ID_INVALID",|p,_|p.admission.authorization_nonce="OLD".into());}
#[test]fn wrong_checkpoint(){fail("EXTERNAL_CHECKPOINT_BINDING_MISMATCH",|p,_|p.admission.checkpoint_sha256="b".repeat(64));}
#[test]fn substituted_ledger(){fail("EXTERNAL_CHECKPOINT_BINDING_MISMATCH",|p,_|p.admission.ledger_id="OTHER".into());}
#[test]fn substituted_holder(){fail("ISSUER_OR_HOLDER_IDENTITY_MISMATCH",|p,_|p.admission.holder_id="OTHER".into());}
#[test]fn substituted_issuer(){fail("ISSUER_OR_HOLDER_IDENTITY_MISMATCH",|p,_|p.admission.issuer_id="OTHER".into());}
#[test]fn epoch_rollback(){fail("POLICY_EPOCH_MISMATCH",|p,_|p.admission.policy_epoch=0);}
#[test]fn empty_root(){fail("MISSING_ANCESTRY",|p,_|p.admission.source_root.clear());}
#[test]fn self_issued_root(){fail("SHARED_OR_SELF_ISSUED_ANCESTRY",|p,_|p.admission.holder_root="RI".into());}
#[test]fn same_issuer_and_source(){fail("SHARED_OR_SELF_ISSUED_ANCESTRY",|p,_|p.admission.issuer_root="RS".into());}
#[test]fn shared_operator(){fail("SHARED_OR_SELF_ISSUED_ANCESTRY",|p,_|p.admission.holder_operator="OS".into());}
#[test]fn shared_administrator(){fail("SHARED_OR_SELF_ISSUED_ANCESTRY",|p,_|p.admission.issuer_admin="AS".into());}
#[test]fn forged_issuer_pin(){fail("ISSUER_PIN_MISMATCH",|_,q|q.pinned_issuer_key_sha256="b".repeat(64));}
#[test]fn forged_holder_pin(){fail("HOLDER_PIN_MISMATCH",|_,q|q.pinned_holder_key_sha256="b".repeat(64));}
#[test]fn revoked_issuer(){fail("REVOKED_ISSUER_OR_HOLDER",|_,q|{q.revoked_key_sha256.insert(q.pinned_issuer_key_sha256.clone());});}
#[test]fn revoked_holder(){fail("REVOKED_ISSUER_OR_HOLDER",|_,q|{q.revoked_key_sha256.insert(q.pinned_holder_key_sha256.clone());});}
#[test]fn replayed_admission(){fail("REPLAYED_ADMISSION",|p,q|{q.used_admission_ids.insert(p.admission.admission_id.clone());});}
#[test]fn replayed_nonce(){fail("REPLAYED_ADMISSION",|p,q|{q.used_nonces.insert(p.admission.authorization_nonce.clone());});}
#[test]fn issuer_signature_forged(){fail("ISSUER_SIGNATURE_INVALID",|p,_|p.issuer_signature_hex="00".repeat(64));}
#[test]fn holder_signature_forged(){fail("HOLDER_POSSESSION_SIGNATURE_INVALID",|p,_|p.holder_signature_hex="00".repeat(64));}
#[test]fn missing_external_origin(){fail("EXTERNAL_ORIGIN_UNAUTHENTICATED",|_,_|{});}
#[test]fn rotation_without_approval(){fail("UNAPPROVED_HOLDER_KEY_ROTATION",|p,q|{let k=key(74);p.admission.holder_key=jwk(&k);q.pinned_holder_key_sha256=fingerprint(&jwk(&k));});}
#[test]fn independently_signed_rotation_documentary_only(){
 let(mut p,mut q)=fixture();rotate(&mut p,&mut q);
 q.issuer_externally_authenticated=true;q.holder_externally_authenticated=true;
 q.rotation_authority_externally_authenticated=true;
 let d=assess(&p,&q);assert_eq!(d.verdict,"DOCUMENTARY_CUSTODY_ADMISSION_ONLY","{:?}",d.reasons);
 assert!(d.rotation_signature_valid);assert!(!d.physical_act_allowed);
}
#[test]fn forged_rotation_signature(){fail("ROTATION_APPROVAL_SIGNATURE_INVALID",|p,q|{rotate(p,q);p.rotation_signature_hex=Some("00".repeat(64));});}
#[test]fn shared_rotation_root(){fail("ROTATION_APPROVER_NOT_INDEPENDENT",|p,q|{rotate(p,q);p.rotation.as_mut().unwrap().approving_root="RH".into();});}
#[test]fn changed_rotation_digest(){fail("ROTATION_BINDING_INVALID",|p,q|{rotate(p,q);p.admission.rotation_approval_sha256="f".repeat(64);});}
#[test]fn revoked_rotation_key(){fail("REVOKED_ROTATION_AUTHORITY",|p,q|{rotate(p,q);q.revoked_key_sha256.insert(q.pinned_rotation_key_sha256.clone());});}
#[test]fn replayed_rotation(){fail("REPLAYED_ROTATION_APPROVAL",|p,q|{rotate(p,q);q.used_rotation_ids.insert("ROT205".into());});}
#[test]fn absent_rotation_external_auth(){fail("ROTATION_AUTHORITY_UNAUTHENTICATED",|p,q|{rotate(p,q);});}
#[test]fn rotation_pin_substitution(){fail("ROTATION_ROOT_PIN_MISMATCH",|p,q|{rotate(p,q);q.pinned_rotation_key_sha256="f".repeat(64);});}
