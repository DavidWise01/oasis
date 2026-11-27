import base64,copy,unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from exit_ledger import assess,canonical,digest

def fixture():
    identity={"pid":401,"start_ticks":123456,"boot_id":"11111111-2222-3333-4444-555555555555","netns_inode":101}
    process={"identity":identity,"samples":[
        {"state":"MATCHED","observed_identity":identity},
        {"state":"MISSING","observed_identity":None}],
        "wait_status":{"direct_child":False,"pidfd_wait_confirmed":False,"exit_code":None}}
    anchor={"sequence":6,"head_sha256":"0"*64}
    event={"sequence":7,"previous_sha256":"0"*64,"challenge_id":"fresh-7","nonce":"nonce-7",
           "run_id":77,"identity_sha256":digest(identity),"state":"EXIT_UNCERTAIN"}
    event["event_sha256"]=digest(event)
    stmt={"schema":"AETHER-253/exit-ledger-v1","anchor_sha256":anchor["head_sha256"],
          "final_head_sha256":event["event_sha256"],"process_evidence_sha256":digest(process)}
    pins={};receipts=[]
    for i in range(3):
        priv=Ed25519PrivateKey.generate();key="key"+str(i);root="root"+str(i)
        receipts.append({"key_id":key,"controller_root":root,
                         "signature_b64":base64.b64encode(priv.sign(canonical(stmt))).decode()})
        pins[key]={"controller_root":root,"public_key_pem":priv.public_key().public_bytes(
             serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()}
    return {"externally_claimed_anchor":anchor,"ledger_events":[event],
            "process_evidence":process,"witness_receipts":receipts,"public_key_pins":pins}
class Tests(unittest.TestCase):
    def expect(self,change,reason):
        b=fixture();change(b);r=assess(b)
        self.assertIn(reason,r["reasons"],r)
        self.assertEqual(r["operational_authority"],"HOLD")
    def test_real_signatures_still_hold(self):
        r=assess(fixture());self.assertEqual(sum(x["signature_valid"] for x in r["observed"]["signed_receipts"]),3)
        self.assertIn("EXTERNAL_ANCHOR_CUSTODY_UNAUTHENTICATED",r["reasons"])
    def test_disappearance_uncertain(self):self.expect(lambda b:None,"DISAPPEARANCE_NOT_PROOF_OF_EXIT")
    def test_invalid_sequence(self):self.expect(lambda b:b["ledger_events"][0].update(sequence=99),"NON_MONOTONIC_SEQUENCE")
    def test_previous_head(self):self.expect(lambda b:b["ledger_events"][0].update(previous_sha256="f"*64),"ANCHOR_OR_PREVIOUS_HEAD_MISMATCH")
    def test_tampered_event(self):self.expect(lambda b:b["ledger_events"][0].update(nonce="altered"),"EVENT_DIGEST_MISMATCH")
    def test_duplicate_nonce(self):
        def change(b):
            e=copy.deepcopy(b["ledger_events"][0]);e["sequence"]=8;e["previous_sha256"]=b["ledger_events"][0]["event_sha256"]
            e["event_sha256"]=digest({k:v for k,v in e.items() if k!="event_sha256"})
            b["ledger_events"].append(e)
        self.expect(change,"NONCE_REPLAY")
    def test_pid_reuse(self):self.expect(lambda b:b["process_evidence"]["samples"][1].update(state="DIFFERENT"),"PID_REUSE_OBSERVED")
    def test_identity_mismatch(self):self.expect(lambda b:b["process_evidence"]["samples"][0].update(observed_identity=None),"PROCESS_IDENTITY_REUSED_OR_MISMATCHED")
    def test_false_exit_claim(self):self.expect(lambda b:b["ledger_events"][0].update(state="EXIT_CORROBORATED"),"FALSE_CORROBORATED_EXIT_CLAIM")
    def test_wait_status_unconfirmed(self):self.expect(lambda b:None,"PROCESS_EXIT_NOT_OS_CORROBORATED")
    def test_event_identity(self):self.expect(lambda b:b["ledger_events"][0].update(identity_sha256="f"*64),"EVENT_PROCESS_IDENTITY_MISMATCH")
    def test_bad_anchor(self):self.expect(lambda b:b["externally_claimed_anchor"].update(head_sha256="bad"),"ANCHOR_INVALID")
    def test_bad_pid(self):self.expect(lambda b:b["process_evidence"]["identity"].update(pid=True),"PROCESS_IDENTITY_INVALID")
    def test_bad_signature(self):self.expect(lambda b:b["witness_receipts"][0].update(signature_b64=base64.b64encode(b"x"*64).decode()),"SIGNATURE_INVALID")
    def test_unknown_key(self):self.expect(lambda b:b["public_key_pins"].pop("key0"),"KEY_PIN_UNAVAILABLE")
    def test_duplicate_root(self):self.expect(lambda b:b["witness_receipts"][1].update(controller_root="root0"),"DUPLICATE_OR_INVALID_ROOT")
    def test_missing_receipt(self):self.expect(lambda b:b["witness_receipts"].pop(),"THREE_WITNESS_RECEIPTS_REQUIRED")
    def test_empty_events(self):self.expect(lambda b:b.update(ledger_events=[]),"EVENT_SET_INVALID")
    def test_invalid_bundle(self):self.assertIn("BUNDLE_INVALID",assess(None)["reasons"])
if __name__=="__main__":unittest.main()
