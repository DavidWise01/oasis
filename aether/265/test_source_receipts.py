import base64
import copy
import hashlib
import unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from source_receipts import assess,canonical,sha_bytes,sha,OBS_SCHEMA,RECEIPT_SCHEMA

def fixture():
    challenge={"challenge_id":"fresh-265","nonce":"nonce-265",
               "run_id":265,"source_commit":"a"*40}
    graph={};pins={};entries=[]
    for i in range(3):
        sid="source"+str(i);controller="controller"+str(i)
        root="root"+str(i);kid="key"+str(i);rnonce="w-nonce-"+str(i)
        raw=("raw data "+str(i)).encode()
        obs={"schema":OBS_SCHEMA,"requested_url":"https://e"+str(i)+".example.net/data",
             "host":"e"+str(i)+".example.net","pinned_ip":"8.8.8.8",
             "dns_address_count":1,"tls_hostname_validation":True,"status":200,
             "elapsed_ms":10,"raw_length":len(raw),"raw_sha256":sha_bytes(raw),
             "raw_b64":base64.b64encode(raw).decode()}
        obs["observation_sha256"]=sha_bytes(canonical(obs))
        statement={"schema":RECEIPT_SCHEMA,"challenge":challenge,
                   "source_id":sid,"controller_id":controller,"receipt_nonce":rnonce,
                   "observation_sha256":obs["observation_sha256"],"raw_sha256":obs["raw_sha256"]}
        key=Ed25519PrivateKey.generate()
        entries.append({"source_id":sid,"controller_id":controller,"key_id":kid,
                        "receipt_nonce":rnonce,"observation":obs,
                        "signature_b64":base64.b64encode(key.sign(canonical(statement))).decode()})
        pins[kid]={"controller_id":controller,"public_key_pem":key.public_key().public_bytes(
            serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()}
        graph[controller]=[root];graph[root]=[]
    return {"challenge":challenge,"acquisitions":entries,
            "public_key_pins":pins,"source_ancestry":graph,"consumed_nonces":[]}

class Tests(unittest.TestCase):
    def expect(self,mutation,code):
        b=fixture();mutation(b);r=assess(b)
        self.assertIn(code,r["reasons"],r)
        self.assertEqual(r["operational_authority"],"HOLD")
    def test_three_real_signatures_not_external_custody(self):
        result=assess(fixture())
        self.assertEqual(sum(item["signature_valid"] for item in result["observed"]["sources"]),3)
        self.assertIn("ACQUISITION_HOST_ORIGIN_NOT_INDEPENDENTLY_ATTESTED",result["reasons"])
    def test_corrupt_bytes(self):
        self.expect(lambda b:b["acquisitions"][0]["observation"].update(raw_b64=base64.b64encode(b"forged").decode()),"RAW_SHA256_MISMATCH")
    def test_length_tamper(self):
        self.expect(lambda b:b["acquisitions"][0]["observation"].update(raw_length=999),"RAW_LENGTH_MISMATCH")
    def test_observation_tamper(self):
        self.expect(lambda b:b["acquisitions"][0]["observation"].update(status=206),"OBSERVATION_SHA256_MISMATCH")
    def test_bad_transport(self):
        self.expect(lambda b:b["acquisitions"][0]["observation"].update(status=302),"OBSERVATION_TRANSPORT_INVALID")
    def test_unsafe_peer(self):
        self.expect(lambda b:b["acquisitions"][0]["observation"].update(pinned_ip="169.254.169.254"),"OBSERVATION_UNSAFE_PEER")
    def test_challenge_replay(self):
        self.expect(lambda b:b["consumed_nonces"].append("nonce-265"),"CHALLENGE_NONCE_REPLAY")
    def test_witness_nonce_replay(self):
        self.expect(lambda b:b["consumed_nonces"].append("w-nonce-0"),"RECEIPT_NONCE_REPLAY")
    def test_duplicate_witness_nonce(self):
        self.expect(lambda b:b["acquisitions"][1].update(receipt_nonce="w-nonce-0"),"RECEIPT_NONCE_REPLAY")
    def test_duplicate_source(self):
        self.expect(lambda b:b["acquisitions"][1].update(source_id="source0"),"DUPLICATE_SOURCE_OR_INVALID")
    def test_duplicate_host(self):
        self.expect(lambda b:b["acquisitions"][1]["observation"].update(host="e0.example.net"),"DUPLICATE_OR_MISSING_HOST")
    def test_duplicate_key(self):
        self.expect(lambda b:b["acquisitions"][1].update(key_id="key0"),"DUPLICATE_KEY_OR_INVALID")
    def test_shared_ancestry(self):
        self.expect(lambda b:b["source_ancestry"]["controller1"].append("root0"),"SHARED_SOURCE_CONTROLLER_ANCESTRY")
    def test_cyclic_ancestry(self):
        self.expect(lambda b:b["source_ancestry"]["root0"].append("controller0"),"ANCESTRY_CYCLE")
    def test_missing_ancestry(self):
        self.expect(lambda b:b["source_ancestry"].pop("root0"),"ANCESTRY_NODE_UNAVAILABLE")
    def test_bad_signature(self):
        self.expect(lambda b:b["acquisitions"][0].update(signature_b64=base64.b64encode(b"x"*64).decode()),"SIGNATURE_INVALID")
    def test_wrong_key(self):
        self.expect(lambda b:b["public_key_pins"]["key0"].update(public_key_pem=b["public_key_pins"]["key1"]["public_key_pem"]),"SIGNATURE_INVALID")
    def test_missing_receipt(self):
        self.expect(lambda b:b["acquisitions"].pop(),"THREE_ACQUISITIONS_REQUIRED")
    def test_invalid_commit(self):
        self.expect(lambda b:b["challenge"].update(source_commit="bad"),"COMMIT_INVALID")
    def test_invalid_bundle(self):
        self.assertIn("BUNDLE_INVALID",assess(None)["reasons"])
    def test_cannot_authorize_act(self):
        self.assertFalse(assess(fixture())["physical_act_allowed"])

if __name__=="__main__":
    unittest.main()
