import base64,copy,unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from checkpoint_gate import assess,canonical,digest

def fixture():
    before={"sequence":9,"previous_sha256":"f"*64,"nonce_sha256":"a"*64,"nonce_count":10}
    before["checkpoint_sha256"]=digest(before)
    item={"nonce":"n11","run_id":7,"challenge_id":"c11","previous_nonce_sha256":before["nonce_sha256"]}
    item["nonce_sha256"]=digest(item)
    after={"sequence":10,"previous_sha256":before["checkpoint_sha256"],
           "nonce_sha256":item["nonce_sha256"],"nonce_count":11}
    after["checkpoint_sha256"]=digest(after)
    statement={"schema":"AETHER-262/checkpoint-v1","before_sha256":before["checkpoint_sha256"],
               "after_sha256":after["checkpoint_sha256"]}
    graph={};pins={};receipts=[]
    for index in range(3):
        priv=Ed25519PrivateKey.generate()
        controller="controller"+str(index)
        root="root"+str(index)
        kid="key"+str(index)
        graph[controller]=[root];graph[root]=[]
        signed={**statement,"controller_id":controller}
        receipts.append({"key_id":kid,"controller_id":controller,
                         "signature_b64":base64.b64encode(priv.sign(canonical(signed))).decode()})
        pins[kid]={"controller_id":controller,"public_key_pem":priv.public_key().public_bytes(
            serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()}
    return {"previous_checkpoint":before,"next_checkpoint":after,"new_consumptions":[item],
            "witnesses":receipts,"public_key_pins":pins,"controller_ancestry":graph}

class Tests(unittest.TestCase):
    def expect(self,mutate,code):
        bundle=fixture();mutate(bundle);result=assess(bundle)
        self.assertIn(code,result["reasons"],result)
        self.assertEqual(result["operational_authority"],"HOLD")
    def test_three_valid_signatures_still_hold(self):
        result=assess(fixture())
        self.assertEqual(sum(x["signature_valid"] for x in result["observed"]["signatures"]),3)
        self.assertIn("EXTERNAL_CHECKPOINT_CUSTODY_UNVERIFIED",result["reasons"])
    def test_previous_checkpoint_tamper(self):
        self.expect(lambda b:b["previous_checkpoint"].update(nonce_count=99),"BEFORE_CHECKPOINT_TAMPER")
    def test_next_checkpoint_tamper(self):
        self.expect(lambda b:b["next_checkpoint"].update(nonce_count=99),"AFTER_CHECKPOINT_TAMPER")
    def test_parent_mismatch(self):
        self.expect(lambda b:b["next_checkpoint"].update(previous_sha256="0"*64),"CHECKPOINT_PARENT_MISMATCH")
    def test_sequence_regression(self):
        self.expect(lambda b:b["next_checkpoint"].update(sequence=9),"CHECKPOINT_SEQUENCE_NOT_MONOTONIC")
    def test_nonce_count_mismatch(self):
        self.expect(lambda b:b["next_checkpoint"].update(nonce_count=12),"NONCE_COUNTER_MISMATCH")
    def test_nonce_checkpoint_mismatch(self):
        self.expect(lambda b:b["next_checkpoint"].update(nonce_sha256="b"*64),"NONCE_CHECKPOINT_MISMATCH")
    def test_nonce_replay(self):
        self.expect(lambda b:b["new_consumptions"].append(copy.deepcopy(b["new_consumptions"][0])),"NONCE_REPLAY")
    def test_nonce_chain_broken(self):
        self.expect(lambda b:b["new_consumptions"][0].update(previous_nonce_sha256="f"*64),"NONCE_HASH_CHAIN_BROKEN")
    def test_nonce_hash_corrupt(self):
        self.expect(lambda b:b["new_consumptions"][0].update(nonce_sha256="f"*64),"CONSUMPTION_HASH_TAMPER")
    def test_duplicate_controller_ancestry(self):
        self.expect(lambda b:b["controller_ancestry"]["controller1"].append("root0"),"SHARED_WITNESS_ANCESTRY")
    def test_ancestry_cycle(self):
        self.expect(lambda b:b["controller_ancestry"]["root0"].append("controller0"),"ANCESTRY_CYCLE")
    def test_missing_ancestor(self):
        self.expect(lambda b:b["controller_ancestry"].pop("root0"),"ANCESTRY_MISSING")
    def test_signature_corrupt(self):
        self.expect(lambda b:b["witnesses"][0].update(signature_b64=base64.b64encode(b"x"*64).decode()),"SIGNATURE_INVALID")
    def test_signer_substitution(self):
        self.expect(lambda b:b["public_key_pins"]["key0"].update(public_key_pem=b["public_key_pins"]["key1"]["public_key_pem"]),"SIGNATURE_INVALID")
    def test_duplicate_key(self):
        self.expect(lambda b:b["witnesses"][1].update(key_id="key0"),"WITNESS_KEY_DUPLICATE")
    def test_missing_witness(self):
        self.expect(lambda b:b["witnesses"].pop(),"THREE_WITNESSES_REQUIRED")
    def test_invalid_receipt(self):
        self.expect(lambda b:b["witnesses"][0].update(controller_id=None),"PIN_MISSING_OR_MISMATCHED")
    def test_invalid_bundle(self):
        self.assertIn("BUNDLE_INVALID",assess(None)["reasons"])
    def test_no_act(self):
        self.assertFalse(assess(fixture())["physical_act_allowed"])

if __name__=="__main__":
    unittest.main()
