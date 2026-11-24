// AETHER-171 documentary-only structural gate. Never call with client booleans as trust.
export function adjudicate(packet, policy={}) {
  const reasons=[];
  const fail=()=>({status:"REJECT",reasons:[...new Set(reasons)],operational_authority:"HOLD",physical_qualification_percent:0,physical_act_allowed:false});
  if (!packet || !Array.isArray(packet.chain) || packet.chain.length!==3) return {status:"REJECT",reasons:["CHAIN_NOT_THREE_CERTIFICATES"],operational_authority:"HOLD",physical_qualification_percent:0,physical_act_allowed:false};
  const [leaf,intermediate,root]=packet.chain;
  const certs=[leaf,intermediate,root];
  for(let i=0;i<certs.length;i++){
    const c=certs[i];
    if(!c || typeof c!=="object"){reasons.push("MALFORMED_CERT_"+i);continue;}
    for(const k of ["subject","issuer","serial","not_before","not_after","fingerprint_sha256","signature_algorithm"]){
      if(typeof c[k]!=="string" || !c[k].trim())reasons.push("MISSING_"+k.toUpperCase()+"_"+i);
    }
    if(!/^[a-fA-F0-9]{64}$/.test(c.fingerprint_sha256||"")) reasons.push("INVALID_FINGERPRINT_"+i);
    const start=Date.parse(c.not_before),end=Date.parse(c.not_after),now=Number(policy.now_ms);
    if(!Number.isFinite(start)||!Number.isFinite(end)||!Number.isFinite(now)||!(start<=now&&now<=end&&end>start)) reasons.push("CERT_TIME_INVALID_"+i);
  }
  if(reasons.some(x=>x.startsWith("MALFORMED_CERT")))return fail();
  if(leaf.issuer!==intermediate.subject || intermediate.issuer!==root.subject || root.issuer!==root.subject)reasons.push("BROKEN_ISSUER_CHAIN");
  if(leaf.subject===leaf.issuer)reasons.push("SELF_ISSUED_LEAF");
  if(new Set(certs.map(c=>c.serial)).size!==3)reasons.push("DUPLICATE_CERT_SERIAL");
  if(root.fingerprint_sha256!==policy.expected_external_root_sha256)reasons.push("ROOT_NOT_PINNED");
  if([leaf,intermediate,root].some(c=>c.fingerprint_sha256===policy.dut_root_sha256))reasons.push("SHARED_DUT_ROOT");
  if(typeof packet.device_serial!=="string"||packet.device_serial!==policy.expected_reference_serial)reasons.push("REFERENCE_DEVICE_MISMATCH");
  if(packet.revocation_status!=="good")reasons.push("REVOCATION_NOT_GOOD");
  if(packet.revocation_checked_at !== policy.expected_revocation_timestamp)reasons.push("REVOCATION_RECEIPT_UNBOUND");
  if(policy.external_chain_signature_validation!==true)reasons.push("CHAIN_SIGNATURE_NOT_EXTERNALLY_VERIFIED");
  if(policy.external_revocation_validation!==true)reasons.push("REVOCATION_NOT_EXTERNALLY_VERIFIED");
  if(policy.external_issuer_registry_validation!==true)reasons.push("ISSUER_REGISTRY_NOT_EXTERNALLY_VERIFIED");
  if(policy.physical_source_validation!==true)reasons.push("PHYSICAL_SOURCE_NOT_VERIFIED");
  return {status:reasons.length?"REJECT":"DOCUMENTARY_REVIEW_ONLY",reasons:[...new Set(reasons)],operational_authority:"HOLD",physical_qualification_percent:0,physical_act_allowed:false};
}
