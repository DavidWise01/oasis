import base64,copy,unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from checkpoint_readback import assess,canonical,sha

def checkpoint(sequence,prior,nonce):
    c={"sequence":sequence,"previous_sha256":prior,"nonce_sha256":nonce,"nonce_count":sequence}
    c["checkpoint_sha256"]=sha(c)
    return c
def fixture():
    a=checkpoint(0,"0"*64,"1"*64)
    b=checkpoint(1,a["checkpoint_sha256"],"2"*64)
    graph={};pins={};readbacks=[]
    for i in range(3):
        key=Ed25519PrivateKey.generate()
        source="source"+str(i);controller="controller"+str(i);kid="key"+str(i);root="root"+str(i)
        graph[controller]=[root];graph[root]=[]
        history=[copy.deepcopy(a),copy.deepcopy(b)]
        signed={"schema":"AETHER-263/readback-v1","source_id":source,"controller_id":controller,
                "checkpoint_sha256":b["checkpoint_sha256"],"history_sha256":sha(history)}
        readbacks.append({"source_id":source,"key_id":kid,"controller_id":controller,
                          "checkpoint":copy.deepcopy(b),"claimed_history":history,
                          "signature_b64":base64.b64encode(key.sign(canonical(signed))).decode()})
        pins[kid]={"controller_id":controller,"public_key_pem":key.public_key().public_bytes(
            serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()}
    return {"externally_claimed_anchor":a,"readbacks":readbacks,
            "public_key_pins":pins,"controller_ancestry":graph}
class Tests(unittest.TestCase):
    def expect(self,mutate,problem):
        b=fixture();mutate(b);r=assess(b)
        self.assertIn(problem,r["reasons"],r);self.assertEqual(r["operational_authority"],"HOLD")
    def test_signatures_valid_but_custody_unverified(self):
        r=assess(fixture())
        self.assertTrue(all(v["signature_valid"] for v in r["observed"]["readbacks"]))
        self.assertIn("NO_INDEPENDENT_READBACK_ACQUISITION_PROOF",r["reasons"])
    def test_rollback_below_anchor(self):
        self.expect(lambda b:b["readbacks"][0].update(checkpoint=checkpoint(0,"0"*64,"2"*64)),"ANCHOR_FORK")
    def test_history_tip_missing(self):
        self.expect(lambda b:b["readbacks"][0]["claimed_history"].pop(),"READBACK_TIP_NOT_HISTORY_TIP")
    def test_history_chain_broken(self):
        self.expect(lambda b:b["readbacks"][0]["claimed_history"][1].update(previous_sha256="0"*64),"HISTORY_CHAIN_BROKEN")
    def test_history_hash_tampered(self):
        self.expect(lambda b:b["readbacks"][0]["checkpoint"].update(nonce_sha256="f"*64),"READBACK_CHECKPOINT_INVALID")
    def test_anchor_substituted(self):
        self.expect(lambda b:b["externally_claimed_anchor"].update(nonce_count=10),"ANCHOR_INVALID")
    def test_missing_anchor_history(self):
        self.expect(lambda b:b["readbacks"][0]["claimed_history"].pop(0),"ANCHOR_NOT_IN_HISTORY")
    def test_shared_ancestry(self):
        self.expect(lambda b:b["controller_ancestry"]["controller1"].append("root0"),"SHARED_CONTROLLER_ANCESTRY")
    def test_ancestry_cycle(self):
        self.expect(lambda b:b["controller_ancestry"]["root0"].append("controller0"),"ANCESTRY_CYCLE")
    def test_missing_ancestry(self):
        self.expect(lambda b:b["controller_ancestry"].pop("root0"),"ANCESTRY_MISSING")
    def test_corrupt_signature(self):
        self.expect(lambda b:b["readbacks"][0].update(signature_b64=base64.b64encode(b"x"*64).decode()),"SIGNATURE_INVALID")
    def test_pin_substitution(self):
        self.expect(lambda b:b["public_key_pins"]["key0"].update(public_key_pem=b["public_key_pins"]["key1"]["public_key_pem"]),"SIGNATURE_INVALID")
    def test_duplicate_source(self):
        self.expect(lambda b:b["readbacks"][1].update(source_id="source0"),"SOURCE_DUPLICATE_OR_INVALID")
    def test_duplicate_key(self):
        self.expect(lambda b:b["readbacks"][1].update(key_id="key0"),"KEY_DUPLICATE_OR_INVALID")
    def test_missing_readback(self):
        self.expect(lambda b:b["readbacks"].pop(),"THREE_READBACKS_REQUIRED")
    def test_bad_history(self):
        self.expect(lambda b:b["readbacks"][0].update(claimed_history=[]),"HISTORY_INVALID")
    def test_invalid_bundle(self):
        self.assertIn("BUNDLE_INVALID",assess(None)["reasons"])
    def test_fail_closed(self):
        self.assertFalse(assess(fixture())["physical_act_allowed"])
if __name__=="__main__":unittest.main()
