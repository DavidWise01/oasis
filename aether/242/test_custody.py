import unittest
from custody import assess,sha
def fixture():
    pin={"manifest_sha256":"a"*64,"source_commit":"b"*40,"challenge_id":"challenge-1","run_id":77,"run_started_at":"2026-11-26T20:00:00Z"}
    keys=[];times=[];nonces=[]
    for i in range(3):
        c="root"+str(i)
        keys.append({"controller":c,"key_fingerprint_sha256":"1"*64,"enrollment_sha256":"2"*64,"custody_claim_sha256":"3"*64})
        v={"controller":c,"challenge_id":"challenge-1","manifest_sha256":"a"*64,"observed_at":"2026-11-26T19:00:00Z"}
        v["receipt_sha256"]=sha(v);times.append(v)
        n={"controller":c,"challenge_id":"challenge-1","nonce":"n"+str(i),"run_id":77,"previous_head_sha256":"4"*64,"new_head_sha256":"5"*64}
        n["consumption_sha256"]=sha(n);nonces.append(n)
    return {"pin":pin,"key_custody":keys,"time_receipts":times,"nonce_consumptions":nonces}
class Tests(unittest.TestCase):
    def expect(self,change,reason):
        x=fixture();change(x);r=assess(x)
        self.assertIn(reason,r["reasons"],r);self.assertEqual(r["operational_authority"],"HOLD")
    def test_valid_claims_hold(self):self.expect(lambda x:None,"EXTERNAL_SIGNER_ANCESTRY_AND_TRUSTED_TIME_NOT_AUTHENTICATED")
    def test_nonce_custody_hold(self):self.expect(lambda x:None,"EXTERNAL_IMMUTABLE_NONCE_CUSTODY_NOT_AUTHENTICATED")
    def test_missing_controller(self):self.expect(lambda x:x["key_custody"].pop(),"THREE_KEY_CUSTODIANS_REQUIRED")
    def test_shared_label(self):self.expect(lambda x:x["key_custody"][1].update(controller="root0"),"SHARED_CONTROLLER_LABEL")
    def test_post_run_time(self):self.expect(lambda x:x["time_receipts"][0].update(observed_at="2026-11-26T21:00:00Z"),"POST_RUN_TIME_CLAIM")
    def test_tamper_time_digest(self):self.expect(lambda x:x["time_receipts"][0].update(manifest_sha256="f"*64),"TIME_RECEIPT_DIGEST_MISMATCH")
    def test_time_binding(self):self.expect(lambda x:x["time_receipts"][0].update(challenge_id="wrong"),"TIME_BINDING_MISMATCH")
    def test_bad_utc(self):self.expect(lambda x:x["time_receipts"][0].update(observed_at="2026-11-26T19:00:00-06:00"),"TIME_CLAIM_INVALID")
    def test_nonce_replay(self):self.expect(lambda x:x["nonce_consumptions"][1].update(nonce="n0"),"NONCE_REPLAY")
    def test_nonce_run(self):self.expect(lambda x:x["nonce_consumptions"][0].update(run_id=78),"NONCE_RUN_MISMATCH")
    def test_nonce_hash(self):self.expect(lambda x:x["nonce_consumptions"][0].update(new_head_sha256="f"*64),"NONCE_RECEIPT_DIGEST_MISMATCH")
    def test_unknown_nonce_controller(self):self.expect(lambda x:x["nonce_consumptions"][0].update(controller="other"),"NONCE_CONTROLLER_NOT_ENROLLED")
    def test_unknown_time_controller(self):self.expect(lambda x:x["time_receipts"][0].update(controller="other"),"TIME_CONTROLLER_NOT_ENROLLED")
    def test_bad_pin(self):self.expect(lambda x:x["pin"].update(manifest_sha256="bad"),"PIN_HASH_INVALID")
    def test_bad_commit(self):self.expect(lambda x:x["pin"].update(source_commit="bad"),"PIN_COMMIT_INVALID")
    def test_empty(self):self.assertIn("BUNDLE_INVALID",assess(None)["reasons"])
    def test_missing_nonce(self):self.expect(lambda x:x["nonce_consumptions"].pop(),"THREE_NONCE_RECEIPTS_REQUIRED")
    def test_bad_enrollment(self):self.expect(lambda x:x["key_custody"][0].update(enrollment_sha256="bad"),"KEY_CUSTODY_HASH_INVALID")
if __name__=="__main__":unittest.main()
