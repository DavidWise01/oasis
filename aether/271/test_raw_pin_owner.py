import base64,copy,unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from raw_pin_owner import assess,canonical,sha,sha_bytes,SCHEMA

def receipt(nonce):
    r={"nonce":nonce,"challenge_sha256":"a"*64,"issuance_sha256":"b"*64}
    r["receipt_sha256"]=sha({"schema":"AETHER-268/pinned-issuance-nonce-v1",**r})
    return r

def fixture():
    checkpoint={"schema":"AETHER-269/nonce-anchor-v1","count":2,
                "receipts":[receipt("n1"),receipt("n2")]}
    checkpoint["snapshot_sha256"]=sha(checkpoint)
    raw=canonical(checkpoint)
    graph={"issuer":["issuer-root"],"issuer-root":[]}
    keys={};source_controllers={};readbacks=[]
    for index in range(3):
        source="source"+str(index);controller="controller"+str(index)
        kid="key"+str(index);session="session"+str(index)
        nonce="receipt"+str(index)
        graph[controller]=["root"+str(index)];graph["root"+str(index)]=[]
        private=Ed25519PrivateKey.generate()
        keys[kid]={"controller_id":controller,
                   "public_key_pem":private.public_key().public_bytes(
                       serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()}
        source_controllers[source]=controller
        statement={"schema":SCHEMA,"source_id":source,"session_id":session,
                   "receipt_nonce":nonce,"challenge_nonce":"challenge-271",
                   "raw_sha256":sha_bytes(raw),"checkpoint_sha256":checkpoint["snapshot_sha256"]}
        readbacks.append({"source_id":source,"session_id":session,"receipt_nonce":nonce,
                          "raw_b64":base64.b64encode(raw).decode(),
                          "raw_sha256":sha_bytes(raw),"controller_id":controller,
                          "key_id":kid,
                          "signature_b64":base64.b64encode(private.sign(canonical(statement))).decode()})
    trust={"issuer_controller":"issuer","public_keys":keys,
           "source_controllers":source_controllers,"ancestry":graph}
    bundle={"trust_record":trust,"expected_checkpoint_sha256":checkpoint["snapshot_sha256"],
            "readbacks":readbacks,"challenge_nonce":"challenge-271"}
    return bundle,sha(trust)

class Tests(unittest.TestCase):
    def expect(self,mutate,reason):
        b,p=fixture();mutate(b)
        result=assess(b,p)
        self.assertIn(reason,result["reasons"],result)
        self.assertEqual(result["operational_authority"],"HOLD")
    def test_valid_crypto_still_hold(self):
        b,p=fixture();result=assess(b,p)
        self.assertTrue(all(x["signature_valid"] for x in result["observed"]["readbacks"]))
        self.assertIn("READBACK_TRANSPORT_NOT_INDEPENDENTLY_ACQUIRED",result["reasons"])
    def test_pin_required(self):
        b,p=fixture()
        self.assertIn("OUT_OF_BAND_PIN_REQUIRED",assess(b,None)["reasons"])
    def test_pin_substitution(self):
        b,p=fixture()
        self.assertIn("OUT_OF_BAND_TRUST_PIN_MISMATCH",assess(b,"f"*64)["reasons"])
    def test_trust_record_rewritten(self):
        self.expect(lambda b:b["trust_record"]["source_controllers"].update(source0="other"),"OUT_OF_BAND_TRUST_PIN_MISMATCH")
    def test_self_issued_controller(self):
        self.expect(lambda b:b["trust_record"]["ancestry"]["controller0"].append("issuer-root"),"SELF_ISSUED_OR_SHARED_ISSUER_ANCESTRY")
    def test_shared_source_parent(self):
        self.expect(lambda b:b["trust_record"]["ancestry"]["controller1"].append("root0"),"SHARED_SOURCE_ANCESTRY")
    def test_bad_ancestry_cycle(self):
        self.expect(lambda b:b["trust_record"]["ancestry"]["root0"].append("controller0"),"LINEAGE_CYCLE")
    def test_missing_parent(self):
        self.expect(lambda b:b["trust_record"]["ancestry"].pop("root0"),"LINEAGE_MISSING")
    def test_bad_source_controller(self):
        self.expect(lambda b:b["readbacks"][0].update(controller_id="controller1"),"SOURCE_CONTROLLER_PIN_MISMATCH")
    def test_duplicate_session(self):
        self.expect(lambda b:b["readbacks"][1].update(session_id="session0"),"DUPLICATE_SESSION")
    def test_duplicate_source(self):
        self.expect(lambda b:b["readbacks"][1].update(source_id="source0"),"DUPLICATE_SOURCE")
    def test_duplicate_nonce(self):
        self.expect(lambda b:b["readbacks"][1].update(receipt_nonce="receipt0"),"READBACK_NONCE_REPLAY")
    def test_corrupted_raw(self):
        self.expect(lambda b:b["readbacks"][0].update(raw_b64=base64.b64encode(b"invalid").decode()),"RAW_CHECKPOINT_INVALID")
    def test_substituted_checkpoint(self):
        def mutate(b):
            row=b["readbacks"][0]
            raw=base64.b64decode(row["raw_b64"])
            check=__import__("json").loads(raw)
            check["count"]=0
            row["raw_b64"]=base64.b64encode(canonical(check)).decode()
        self.expect(mutate,"RAW_CHECKPOINT_INVALID")
    def test_raw_hash_mismatch(self):
        self.expect(lambda b:b["readbacks"][0].update(raw_sha256="f"*64),"RAW_READBACK_HASH_MISMATCH")
    def test_bad_signature(self):
        self.expect(lambda b:b["readbacks"][0].update(signature_b64=base64.b64encode(b"x"*64).decode()),"SIGNATURE_INVALID")
    def test_missing_key(self):
        self.expect(lambda b:b["readbacks"][0].update(key_id="unknown"),"SIGNER_NOT_IN_PINNED_TRUST_RECORD")
    def test_invalid_bundle(self):
        self.assertIn("BUNDLE_INVALID",assess(None,"a"*64)["reasons"])
    def test_missing_readback(self):
        self.expect(lambda b:b["readbacks"].pop(),"THREE_READBACKS_REQUIRED")
    def test_no_act(self):
        b,p=fixture();self.assertFalse(assess(b,p)["physical_act_allowed"])
if __name__=="__main__":unittest.main()
