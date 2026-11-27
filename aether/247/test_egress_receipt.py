import base64,hashlib,unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from egress_receipt import assess,canonical,digest,CATEGORIES
def fixture():
    m=[{"category":x,"outcome":"blocked","errno":101,"elapsed_ms":4} for x in sorted(CATEGORIES)]
    keys={};receipts=[]
    for i in range(3):
        k=Ed25519PrivateKey.generate()
        statement={"schema":"AETHER-247/signed-observation-v1","controller_root":"r"+str(i),
            "challenge_id":"challenge-A","run_id":111,"source_commit":"a"*40,
            "measurements_sha256":digest(m),"nonce":"nonce-"+str(i)}
        receipts.append({"key_id":"key"+str(i),"statement":statement,
          "signature_b64":base64.b64encode(k.sign(canonical(statement))).decode()})
        keys["key"+str(i)]={"controller_root":"r"+str(i),
          "public_key_pem":k.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()}
    return {"measurements":m,"receipts":receipts,"public_key_pins":keys,
      "consumed_challenges":[],"challenge_id":"challenge-A","run_id":111,
      "source_commit":"a"*40,"namespace_separated":True,"credential_free":True}
class Tests(unittest.TestCase):
    def expect(self,change,reason):
        d=fixture();change(d);r=assess(d)
        self.assertIn(reason,r["reasons"],r);self.assertEqual(r["operational_authority"],"HOLD")
    def test_signatures_verified_and_hold(self):
        r=assess(fixture());self.assertEqual(sum(x["signature_valid"] for x in r["observed"]["receipts"]),3)
        self.assertIn("SIGNER_CUSTODY_NOT_INDEPENDENTLY_AUTHENTICATED",r["reasons"])
    def test_measurement_allowed(self):self.expect(lambda x:x["measurements"][0].update(outcome="allowed"),"EGRESS_DENIAL_FAILED")
    def test_measurement_tamper(self):self.expect(lambda x:x["measurements"][0].update(elapsed_ms=20),"MEASUREMENT_DIGEST_MISMATCH")
    def test_measurement_missing(self):self.expect(lambda x:x["measurements"].pop(),"SIX_MEASUREMENTS_REQUIRED")
    def test_duplicate_category(self):self.expect(lambda x:x["measurements"][1].update(category=x["measurements"][0]["category"]),"CATEGORY_DUPLICATE_OR_INVALID")
    def test_bad_errno(self):self.expect(lambda x:x["measurements"][0].update(errno=-1),"ERRNO_INVALID")
    def test_bad_duration(self):self.expect(lambda x:x["measurements"][0].update(elapsed_ms=31000),"MEASUREMENT_DURATION_INVALID")
    def test_namespace(self):self.expect(lambda x:x.update(namespace_separated=False),"NETWORK_NAMESPACE_SEPARATION_NOT_RECORDED")
    def test_credentials(self):self.expect(lambda x:x.update(credential_free=False),"CREDENTIAL_FREE_NOT_RECORDED")
    def test_challenge_replay(self):self.expect(lambda x:x["consumed_challenges"].append("challenge-A"),"CHALLENGE_REPLAY")
    def test_nonce_replay(self):self.expect(lambda x:x["consumed_challenges"].append("nonce-0"),"NONCE_REPLAY_OR_INVALID")
    def test_wrong_run(self):self.expect(lambda x:x["receipts"][0]["statement"].update(run_id=44),"RECEIPT_RUN_BINDING_MISMATCH")
    def test_wrong_commit(self):self.expect(lambda x:x["receipts"][0]["statement"].update(source_commit="b"*40),"RECEIPT_RUN_BINDING_MISMATCH")
    def test_signature_poison(self):self.expect(lambda x:x["receipts"][0].update(signature_b64=base64.b64encode(b"x"*64).decode()),"SIGNATURE_INVALID")
    def test_wrong_public_key(self):
        self.expect(lambda x:x["public_key_pins"]["key0"].update(public_key_pem=x["public_key_pins"]["key1"]["public_key_pem"]),"SIGNATURE_INVALID")
    def test_missing_key(self):self.expect(lambda x:x["public_key_pins"].pop("key0"),"TRUST_PIN_UNAVAILABLE")
    def test_duplicate_root(self):self.expect(lambda x:x["receipts"][1]["statement"].update(controller_root="r0"),"CONTROLLER_ROOT_DUPLICATE_OR_INVALID")
    def test_duplicate_key(self):self.expect(lambda x:x["receipts"][1].update(key_id="key0"),"DUPLICATE_KEY_ID")
    def test_missing_receipt(self):self.expect(lambda x:x["receipts"].pop(),"THREE_SIGNED_RECEIPTS_REQUIRED")
    def test_bad_schema(self):self.expect(lambda x:x["receipts"][0]["statement"].update(schema="bad"),"STATEMENT_SCHEMA_INVALID")
    def test_none(self):self.assertIn("BUNDLE_INVALID",assess(None)["reasons"])
    def test_unverified(self):self.expect(lambda x:None,"PROBE_TRANSPORT_AND_NETWORK_ENFORCEMENT_NOT_INDEPENDENTLY_OBSERVED")
if __name__=="__main__":unittest.main()
