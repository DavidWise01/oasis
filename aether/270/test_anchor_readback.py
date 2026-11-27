import base64
import copy
import unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from anchor_readback import check,canon,sha,SCHEMA

def receipt(nonce):
    r={"nonce":nonce,"challenge_sha256":"a"*64,"issuance_sha256":"b"*64}
    r["receipt_sha256"]=sha({"schema":"AETHER-268/pinned-issuance-nonce-v1",**r})
    return r

def snapshot(nonces):
    r={"schema":"AETHER-269/nonce-anchor-v1","count":len(nonces),
       "receipts":[receipt(nonce) for nonce in nonces]}
    r["snapshot_sha256"]=sha(r)
    return r

def fixture():
    prev=snapshot(["n1"])
    current=snapshot(["n1","n2"])
    pins={};graph={};reads=[]
    for i in range(3):
        private=Ed25519PrivateKey.generate()
        sid="storage"+str(i);cid="controller"+str(i)
        kid="key"+str(i);nonce="readback"+str(i)
        graph[cid]=["root"+str(i)];graph["root"+str(i)]=[]
        body_sha="c"*64
        statement={"schema":SCHEMA,"source_id":sid,"controller_id":cid,
                   "readback_nonce":nonce,"checkpoint_sha256":current["snapshot_sha256"],
                   "retrieval_sha256":body_sha}
        reads.append({"source_id":sid,"controller_id":cid,"key_id":kid,
                      "readback_nonce":nonce,"checkpoint":copy.deepcopy(current),
                      "retrieval_sha256":body_sha,
                      "signed_receipt_b64":base64.b64encode(private.sign(canon(statement))).decode()})
        pins[kid]={"controller_id":cid,"public_key_pem":private.public_key().public_bytes(
            serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()}
    return {"prior_checkpoint":prev,"readbacks":reads,"public_key_pins":pins,
            "controller_ancestry":graph}

class Test(unittest.TestCase):
    def expect(self,modify,reason):
        b=fixture();modify(b)
        answer=check(b)
        self.assertIn(reason,answer["reasons"],answer)
        self.assertEqual(answer["operational_authority"],"HOLD")
    def test_crypto_valid_but_external_hold(self):
        result=check(fixture())
        self.assertTrue(all(r["signature_valid"] for r in result["observed"]["readbacks"]))
        self.assertIn("RETRIEVAL_BYTES_NOT_INDEPENDENTLY_OBSERVED",result["reasons"])
    def test_missing_prior(self):
        self.expect(lambda b:b.update(prior_checkpoint={}),"PRIOR_CHECKPOINT_INVALID")
    def test_lower_count_rollback(self):
        self.expect(lambda b:b["readbacks"][0].update(checkpoint=snapshot([])),"CHECKPOINT_ROLLBACK")
    def test_removed_prior_nonce(self):
        self.expect(lambda b:b["readbacks"][0].update(checkpoint=snapshot(["n2"])),"PINNED_NONCE_MISSING")
    def test_rewritten_prior_nonce(self):
        def change(b):
            s=b["readbacks"][0]["checkpoint"]
            s["receipts"][0]["issuance_sha256"]="f"*64
            r=s["receipts"][0]
            r["receipt_sha256"]=sha({"schema":"AETHER-268/pinned-issuance-nonce-v1","nonce":r["nonce"],
                "challenge_sha256":r["challenge_sha256"],"issuance_sha256":r["issuance_sha256"]})
            s["snapshot_sha256"]=sha({k:v for k,v in s.items() if k!="snapshot_sha256"})
        self.expect(change,"PINNED_NONCE_REWRITTEN")
    def test_cross_source_conflicting_count(self):
        self.expect(lambda b:b["readbacks"][0].update(checkpoint=snapshot(["n1","n3"])),"SAME_COUNT_CONFLICTING_CHECKPOINTS")
    def test_corrupt_snapshot(self):
        self.expect(lambda b:b["readbacks"][0]["checkpoint"].update(snapshot_sha256="f"*64),"READBACK_CHECKPOINT_INVALID")
    def test_corrupt_signature(self):
        self.expect(lambda b:b["readbacks"][0].update(signed_receipt_b64=base64.b64encode(b"x"*64).decode()),"SIGNATURE_INVALID")
    def test_key_substitution(self):
        self.expect(lambda b:b["public_key_pins"]["key0"].update(
            public_key_pem=b["public_key_pins"]["key1"]["public_key_pem"]),"SIGNATURE_INVALID")
    def test_retrieval_hash_substitution(self):
        self.expect(lambda b:b["readbacks"][0].update(retrieval_sha256="e"*64),"SIGNATURE_INVALID")
    def test_invalid_retrieval_digest(self):
        self.expect(lambda b:b["readbacks"][0].update(retrieval_sha256="bad"),"RETRIEVAL_DIGEST_INVALID")
    def test_duplicate_source(self):
        self.expect(lambda b:b["readbacks"][1].update(source_id="storage0"),"SOURCE_ID_REPLAY")
    def test_duplicate_key(self):
        self.expect(lambda b:b["readbacks"][1].update(key_id="key0"),"SIGNER_KEY_REUSE")
    def test_duplicate_nonce(self):
        self.expect(lambda b:b["readbacks"][1].update(readback_nonce="readback0"),"READBACK_NONCE_REPLAY")
    def test_shared_ancestry(self):
        self.expect(lambda b:b["controller_ancestry"]["controller1"].append("root0"),"SHARED_CONTROLLER_ANCESTRY")
    def test_ancestry_cycle(self):
        self.expect(lambda b:b["controller_ancestry"]["root0"].append("controller0"),"ANCESTRY_CYCLE")
    def test_missing_ancestry(self):
        self.expect(lambda b:b["controller_ancestry"].pop("root0"),"ANCESTRY_NODE_MISSING")
    def test_missing_readback(self):
        self.expect(lambda b:b["readbacks"].pop(),"THREE_READBACKS_REQUIRED")
    def test_none(self):
        self.assertIn("BUNDLE_INVALID",check(None)["reasons"])
    def test_no_act(self):
        self.assertFalse(check(fixture())["physical_act_allowed"])

if __name__=="__main__":
    unittest.main()
