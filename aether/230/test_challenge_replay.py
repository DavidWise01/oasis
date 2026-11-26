"""AETHER-230 synthetic out-of-band challenge replay tests; never external proof."""
import copy
import json
import unittest
from challenge_replay import assess,sha,stable

NONCE="SYNTHETIC-NONCE-230-abcdef-987654321"
def fixture():
    challenge={"schema":"AETHER-230/external-challenge-v1",
       "nonce":NONCE,"enrollment_id":"ENR-230","challenge_id":"CH-230",
       "custodian_id":"CUST-230","source_root":"OWNED-ROOT",
       "holder_root":"DECLARED-EXTERNAL-HOLDER",
       "issuer_root":"DECLARED-EXTERNAL-ISSUER","holder_key_sha256":"a"*64,
       "capture_sha256":"b"*64,
       "external_controller_authentication":"NOT_PERFORMED",
       "signature_verification":"NOT_PERFORMED",
       "previous_phase_freeze":"../224/decision.json",
       "operational_authority":"HOLD","physical_act_allowed":False,"may_recover":False}
    receipt={k:challenge[k] for k in ("nonce","enrollment_id","challenge_id",
                                      "custodian_id","holder_key_sha256","capture_sha256")}
    receipt.update(signature_verification="NOT_PERFORMED",operational_authority="HOLD",
                   physical_act_allowed=False)
    receipt_bytes=(json.dumps(receipt,sort_keys=True)+"\n").encode()
    challenge["receipt_sha256"]=sha(receipt_bytes)
    first={key:challenge[key] for key in ("nonce","enrollment_id","challenge_id","custodian_id")}
    first["previous_sha256"]="0"*64
    first["entry_sha256"]=sha(stable(first))
    ledger={"entries":[first],"head_sha256":first["entry_sha256"],
            "controller_authentication":"NOT_PERFORMED"}
    ledger_bytes=(json.dumps(ledger,sort_keys=True)+"\n").encode()
    challenge["ledger_sha256"]=sha(ledger_bytes)
    return [challenge,receipt_bytes,ledger_bytes]

def replace_ledger(x,fn):
    ledger=json.loads(x[2])
    fn(ledger)
    x[2]=(json.dumps(ledger,sort_keys=True)+"\n").encode()
    x[0]["ledger_sha256"]=sha(x[2])

def replace_receipt(x,fn):
    receipt=json.loads(x[1])
    fn(receipt)
    x[1]=(json.dumps(receipt,sort_keys=True)+"\n").encode()
    x[0]["receipt_sha256"]=sha(x[1])

class ChallengeReplayTests(unittest.TestCase):
    def reject(self,code,change):
        x=fixture();change(x);v=assess(*x)
        self.assertEqual(v["verdict"],"REJECT",v)
        self.assertIn(code,v["reasons"],v)
        self.assertEqual(v["operational_authority"],"HOLD")
        self.assertFalse(v["physical_act_allowed"])
        self.assertFalse(v["independent_nonce_consumption_authenticated"])

    def test_consistent_synthetic_record_is_not_authenticated(self):
        d=assess(*fixture())
        self.assertEqual(d["verdict"],"DOCUMENTARY_CHALLENGE_LEDGER_CONSISTENT_ONLY",d)
        self.assertFalse(d["remote_signature_cryptographically_verified"])
        self.assertFalse(d["external_controller_authenticated"])

    def test_missing_receipt(self):
        self.reject("EXTERNAL_RECEIPT_NOT_OBSERVED",lambda x:x.__setitem__(1,None))
    def test_missing_ledger(self):
        self.reject("CONSUMPTION_LEDGER_NOT_OBSERVED",lambda x:x.__setitem__(2,None))
    def test_receipt_byte_tamper(self):
        self.reject("RECEIPT_BYTE_DIGEST_MISMATCH",lambda x:x.__setitem__(1,x[1]+b"x"))
    def test_ledger_byte_tamper(self):
        self.reject("LEDGER_BYTE_DIGEST_MISMATCH",lambda x:x.__setitem__(2,x[2]+b"x"))
    def test_missing_receipt_pin(self):
        self.reject("SHA256_PIN_MISSING:receipt_sha256",lambda x:x[0].update(receipt_sha256=""))
    def test_missing_ledger_pin(self):
        self.reject("SHA256_PIN_MISSING:ledger_sha256",lambda x:x[0].update(ledger_sha256=""))
    def test_missing_capture_pin(self):
        self.reject("SHA256_PIN_MISSING:capture_sha256",lambda x:x[0].update(capture_sha256=""))
    def test_missing_key_fingerprint(self):
        self.reject("HOLDER_KEY_FINGERPRINT_INVALID",lambda x:x[0].update(holder_key_sha256="bad"))
    def test_weak_nonce(self):
        self.reject("NONCE_INVALID_OR_WEAK",lambda x:x[0].update(nonce="replay"))
    def test_nonce_binding_swapped(self):
        self.reject("RECEIPT_CHALLENGE_BINDING_MISMATCH:nonce",
                    lambda x:x[0].update(nonce="SYNTHETIC-NONCE-SWAP-abcdef-9999"))
    def test_enrollment_binding_swapped(self):
        self.reject("RECEIPT_CHALLENGE_BINDING_MISMATCH:enrollment_id",
                    lambda x:x[0].update(enrollment_id="ENR-SWAPPED"))
    def test_receipt_key_swap(self):
        self.reject("RECEIPT_CHALLENGE_BINDING_MISMATCH:holder_key_sha256",
                    lambda x:replace_receipt(x,lambda r:r.update(holder_key_sha256="f"*64)))
    def test_receipt_physical_act_promotion(self):
        self.reject("RECEIPT_AUTHORITY_PROMOTION",
                    lambda x:replace_receipt(x,lambda r:r.update(physical_act_allowed=True)))
    def test_receipt_false_signature_verified(self):
        self.reject("RECEIPT_SIGNATURE_AUTHENTICATION_MISREPRESENTED",
                    lambda x:replace_receipt(x,lambda r:r.update(signature_verification="VERIFIED")))
    def test_replayed_nonce_in_chain(self):
        def edit(x):
            def change(l):
                second=copy.deepcopy(l["entries"][0]);second["previous_sha256"]=l["head_sha256"]
                second["entry_sha256"]=sha(stable({k:second[k] for k in
                      ("nonce","enrollment_id","challenge_id","custodian_id","previous_sha256")}))
                l["entries"].append(second);l["head_sha256"]=second["entry_sha256"]
            replace_ledger(x,change)
        self.reject("LEDGER_NONCE_REPLAY",edit)
    def test_missing_consumed_nonce(self):
        self.reject("CHALLENGE_NONCE_NOT_UNIQUELY_CONSUMED",
                    lambda x:replace_ledger(x,lambda l:l["entries"][0].update(nonce="OTHER-UNIQUE-NONCE-123456789")))
    def test_broken_chain_head(self):
        self.reject("LEDGER_HEAD_MISMATCH",
                    lambda x:replace_ledger(x,lambda l:l.update(head_sha256="f"*64)))
    def test_broken_previous_hash(self):
        self.reject("LEDGER_CHAIN_BROKEN",
                    lambda x:replace_ledger(x,lambda l:l["entries"][0].update(previous_sha256="f"*64)))
    def test_broken_entry_digest(self):
        self.reject("LEDGER_ENTRY_DIGEST_INVALID",
                    lambda x:replace_ledger(x,lambda l:l["entries"][0].update(entry_sha256="f"*64)))
    def test_missing_ledger_entries(self):
        self.reject("LEDGER_JSON_INVALID",
                    lambda x:replace_ledger(x,lambda l:l.update(entries=[])))
    def test_ledger_false_external_authentication(self):
        self.reject("LEDGER_INDEPENDENCE_MISREPRESENTED",
                    lambda x:replace_ledger(x,lambda l:l.update(controller_authentication="VERIFIED")))
    def test_root_false_signature_claim(self):
        self.reject("EXTERNAL_AUTHENTICATION_MISREPRESENTED",
                    lambda x:x[0].update(signature_verification="VERIFIED"))
    def test_root_false_controller_claim(self):
        self.reject("EXTERNAL_AUTHENTICATION_MISREPRESENTED",
                    lambda x:x[0].update(external_controller_authentication="VERIFIED"))
    def test_shared_issuer_holder(self):
        self.reject("SHARED_SOURCE_CUSTODIAN_ISSUER_CONTROL",
                    lambda x:x[0].update(issuer_root="DECLARED-EXTERNAL-HOLDER"))
    def test_promoted_act(self):
        self.reject("OPERATIONAL_AUTHORITY_PROMOTION",
                    lambda x:x[0].update(physical_act_allowed=True))
    def test_promoted_recovery(self):
        self.reject("OPERATIONAL_AUTHORITY_PROMOTION",
                    lambda x:x[0].update(may_recover=True))
    def test_missing_phase_freeze(self):
        self.reject("PREVIOUS_FREEZE_BINDING_INVALID",
                    lambda x:x[0].update(previous_phase_freeze="../223/protocol.json"))
    def test_bad_receipt_json(self):
        self.reject("RECEIPT_JSON_INVALID",
                    lambda x:(x.__setitem__(1,b"bad json"),x[0].update(receipt_sha256=sha(b"bad json"))))
    def test_repeat_evaluation_deterministic(self):
        self.assertEqual(assess(*fixture()),assess(*fixture()))

if __name__=="__main__":
    unittest.main()
