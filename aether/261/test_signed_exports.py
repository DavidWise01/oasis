import base64,copy,tempfile,unittest,sys
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"258"))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"260"))
from sqlite_cas import initialize,cas,snapshot
from receipt_export import export
from signed_exports import assess,canonical,sha

def fixture():
    with tempfile.TemporaryDirectory() as t:
        db=Path(t)/"a.db";initialize(db)
        h=snapshot(db)["head"]
        cas(db,"a1","host1","c1","n1",h["sequence"],h["hash"])
        first=export(db)
        h=snapshot(db)["head"]
        cas(db,"a2","host2","c2","n2",h["sequence"],h["hash"])
        second=export(db)
    challenge={"challenge_id":"challenge-7","nonce":"unique-7","run_id":7,
               "source_commit":"a"*40,"host_id":"claimed-host"}
    stmt={"schema":"AETHER-261/witness-v1","challenge":challenge,
          "before_sha256":first["export_sha256"],"after_sha256":second["export_sha256"]}
    pins={};receipts=[]
    for i in range(3):
        key=Ed25519PrivateKey.generate();kid="key"+str(i);root="root"+str(i);nonce="witness-"+str(i)
        signed={**stmt,"controller_claim":root,"witness_nonce":nonce}
        receipts.append({"key_id":kid,"controller_claim":root,"nonce":nonce,
                         "signature_b64":base64.b64encode(key.sign(canonical(signed))).decode()})
        pins[kid]={"controller_claim":root,"public_key_pem":key.public_key().public_bytes(
            serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()}
    return {"challenge":challenge,"before_export":first,"after_export":second,
            "receipts":receipts,"externally_claimed_key_pins":pins,
            "consumed_nonces":[],"seen_export_digests":[]}
class Tests(unittest.TestCase):
    def expect(self,alter,problem):
        b=fixture();alter(b);r=assess(b)
        self.assertIn(problem,r["reasons"],r);self.assertEqual(r["operational_authority"],"HOLD")
    def test_genuine_crypto_still_unqualified(self):
        b=fixture();r=assess(b)
        self.assertEqual(sum(x["valid"] for x in r["observed"]["verified_signatures"]),3)
        self.assertIn("KEY_CUSTODY_AND_ANCESTRY_NOT_INDEPENDENTLY_VERIFIED",r["reasons"])
    def test_before_modified(self):self.expect(lambda b:b["before_export"]["events"][0].update(host="forged"),"BEFORE_EXPORT_INVALID")
    def test_after_modified(self):self.expect(lambda b:b["after_export"]["events"][0].update(host="forged"),"AFTER_EXPORT_INVALID")
    def test_history_rewritten(self):
        def change(b):
            b["after_export"]["events"][0].update(host="changed")
            b["after_export"]["export_sha256"]=sha({k:v for k,v in b["after_export"].items() if k!="export_sha256"})
        self.expect(change,"RESTART_HISTORY_REWRITTEN_OR_TRUNCATED")
    def test_truncation(self):
        def change(b):
            b["after_export"]=copy.deepcopy(b["before_export"])
        self.expect(change,"EXPORT_UNCHANGED_ACROSS_RESTART")
    def test_nonce_replay(self):self.expect(lambda b:b["consumed_nonces"].append("unique-7"),"CHALLENGE_REPLAY")
    def test_export_replay(self):self.expect(lambda b:b["seen_export_digests"].append(b["before_export"]["export_sha256"]),"EXPORT_DIGEST_REPLAY")
    def test_witness_nonce_replay(self):self.expect(lambda b:b["consumed_nonces"].append("witness-0"),"WITNESS_NONCE_REPLAY")
    def test_duplicate_witness_nonce(self):self.expect(lambda b:b["receipts"][1].update(nonce="witness-0"),"WITNESS_NONCE_REPLAY")
    def test_signature_corrupted(self):self.expect(lambda b:b["receipts"][0].update(signature_b64=base64.b64encode(b"x"*64).decode()),"SIGNATURE_INVALID")
    def test_key_substitution(self):self.expect(lambda b:b["externally_claimed_key_pins"]["key0"].update(
        public_key_pem=b["externally_claimed_key_pins"]["key1"]["public_key_pem"]),"SIGNATURE_INVALID")
    def test_wrong_controller(self):self.expect(lambda b:b["receipts"][1].update(controller_claim="root0"),"CONTROLLER_DUPLICATE_OR_INVALID")
    def test_missing_witness(self):self.expect(lambda b:b["receipts"].pop(),"THREE_RECEIPTS_REQUIRED")
    def test_missing_pin(self):self.expect(lambda b:b["externally_claimed_key_pins"].pop("key0"),"KEY_PIN_MISSING")
    def test_wrong_run(self):self.expect(lambda b:b["challenge"].update(run_id=True),"RUN_INVALID")
    def test_wrong_commit(self):self.expect(lambda b:b["challenge"].update(source_commit="bad"),"COMMIT_INVALID")
    def test_invalid_bundle(self):self.assertIn("BUNDLE_INVALID",assess(None)["reasons"])
    def test_hold(self):self.assertFalse(assess(fixture())["physical_act_allowed"])
if __name__=="__main__":unittest.main()
