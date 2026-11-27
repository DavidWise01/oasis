import base64,hashlib,unittest
from qualification import assess,canonical
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

def fixture():
    artifacts=[];keys={}
    for i in range(3):
        k=Ed25519PrivateKey.generate()
        b=("fixture-"+str(i)).encode()
        s={"schema":"AETHER-245/signed-byte-statement-v1","challenge_id":"c1","run_id":19,
           "source_commit":"a"*40,"nonce":"n"+str(i),"controller_claim":"controller"+str(i),
           "body_sha256":hashlib.sha256(b).hexdigest(),"source_id":"s"+str(i)}
        artifacts.append({"key_id":"key"+str(i),"statement":s,
            "body_b64":base64.b64encode(b).decode(),
            "signature_b64":base64.b64encode(k.sign(canonical(s))).decode()})
        keys["key"+str(i)]={"controller_claim":"controller"+str(i),
            "public_key_pem":k.public_key().public_bytes(
                serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()}
    return {"artifacts":artifacts,"independently_pinned_keys":keys,
            "consumed_nonces":[],"challenge":{"challenge_id":"c1","run_id":19,"source_commit":"a"*40}}
class Tests(unittest.TestCase):
    def expect(self,change,reason):
        d=fixture();change(d);r=assess(d)
        self.assertIn(reason,r["reasons"],r)
        self.assertEqual(r["operational_authority"],"HOLD")
    def test_real_signatures_still_hold(self):
        d=fixture();r=assess(d)
        self.assertEqual([o["signature_valid"] for o in r["observed"]],[True]*3)
        self.assertIn("EXTERNAL_KEY_CUSTODY_UNAUTHENTICATED",r["reasons"])
    def test_tampered_signature(self):
        self.expect(lambda d:d["artifacts"][0].update(signature_b64=base64.b64encode(b"x"*64).decode()),"SIGNATURE_INVALID")
    def test_body_changed(self):
        self.expect(lambda d:d["artifacts"][0].update(body_b64=base64.b64encode(b"bad").decode()),"BODY_DIGEST_MISMATCH")
    def test_wrong_public_key(self):
        self.expect(lambda d:d["independently_pinned_keys"]["key0"].update(public_key_pem=d["independently_pinned_keys"]["key1"]["public_key_pem"]),"SIGNATURE_INVALID")
    def test_nonce_replay(self):
        self.expect(lambda d:d["consumed_nonces"].append("n0"),"NONCE_REPLAY_OR_INVALID")
    def test_cross_source_nonce(self):
        self.expect(lambda d:d["artifacts"][1]["statement"].update(nonce="n0"),"NONCE_REPLAY_OR_INVALID")
    def test_changed_run(self):
        self.expect(lambda d:d["artifacts"][1]["statement"].update(run_id=20),"CHALLENGE_BINDING_MISMATCH")
    def test_duplicate_body(self):
        self.expect(lambda d:d["artifacts"][1].update(body_b64=d["artifacts"][0]["body_b64"]),"DUPLICATE_BODY")
    def test_missing_key(self):
        self.expect(lambda d:d["independently_pinned_keys"].pop("key0"),"PUBLIC_KEY_NOT_PINNED")
    def test_missing_artifact(self):
        self.expect(lambda d:d["artifacts"].pop(),"EXACT_THREE_ARTIFACTS_REQUIRED")
    def test_bool_run(self):
        self.expect(lambda d:d["artifacts"][0]["statement"].update(run_id=True),"RUN_OR_SOURCE_INVALID")
    def test_bad_commit(self):
        self.expect(lambda d:d["artifacts"][0]["statement"].update(source_commit="bad"),"RUN_OR_SOURCE_INVALID")
    def test_reused_controller(self):
        self.expect(lambda d:d["artifacts"][1]["statement"].update(controller_claim="controller0"),"CONTROLLER_REUSED_OR_INVALID")
    def test_bad_b64(self):
        self.expect(lambda d:d["artifacts"][0].update(signature_b64="!"),"BODY_OR_SIGNATURE_INVALID")
    def test_schema(self):
        self.expect(lambda d:d["artifacts"][0]["statement"].update(schema="poison"),"STATEMENT_SCHEMA_INVALID")
    def test_invalid_bundle(self):
        self.assertIn("BUNDLE_INVALID",assess(None)["reasons"])
    def test_network_hold(self):
        self.assertIn("NETWORK_ISOLATION_NOT_MEASURED",assess(fixture())["reasons"])
    def test_custody_hold(self):
        self.assertEqual(assess(fixture())["physical_qualification_percent"],0)
if __name__=="__main__":unittest.main()
