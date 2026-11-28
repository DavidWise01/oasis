import base64
import copy
import unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from provenance_gate import SCHEMA,OBS_SCHEMA,assess,canon,sha,sha_bytes

def fixture():
    raw=b"stable remote bytes"
    url="https://evidence.example.org/frozen"
    challenge={"challenge_id":"c274","nonce":"ch274","run_id":274,
               "expected_raw_sha256":sha_bytes(raw),"url":url}
    graph={"issuer":["issuer-root"],"issuer-root":[]}
    sources={};records=[]
    for i in range(3):
        source="source"+str(i);controller="controller"+str(i)
        kid="key"+str(i);sid="session"+str(i);nonce="n"+str(i)
        graph[controller]=["root"+str(i)];graph["root"+str(i)]=[]
        private=Ed25519PrivateKey.generate()
        pem=private.public_key().public_bytes(serialization.Encoding.PEM,
             serialization.PublicFormat.SubjectPublicKeyInfo).decode()
        sources[source]={"controller_id":controller,"key_id":kid,
                         "public_key_pem":pem,"hostname":"evidence.example.org"}
        obs={"schema":OBS_SCHEMA,"requested_url":url,"host":"evidence.example.org",
             "pinned_ip":"8.8.8.8","dns_address_count":1,"tls_hostname_validation":True,
             "status":200,"elapsed_ms":10,"raw_length":len(raw),
             "raw_sha256":sha_bytes(raw),"raw_b64":base64.b64encode(raw).decode()}
        obs["observation_sha256"]=sha(obs)
        statement={"schema":SCHEMA,"challenge":challenge,"source_id":source,
                   "controller_id":controller,"key_id":kid,"session_id":sid,
                   "session_nonce":nonce,"observation_sha256":obs["observation_sha256"]}
        records.append({"source_id":source,"controller_id":controller,"key_id":kid,
                        "session_id":sid,"session_nonce":nonce,"observation":obs,
                        "signed_receipt_b64":base64.b64encode(private.sign(canon(statement))).decode()})
    reg={"sources":sources,"controllers":graph,"issuer_controller":"issuer"}
    return {"registry":reg,"challenge":challenge,"previous_session_nonces":[],
            "acquisitions":records},sha(reg)

class Test(unittest.TestCase):
    def expect(self,change,reason):
        b,p=fixture();change(b);r=assess(b,p)
        self.assertIn(reason,r["reasons"],r)
        self.assertEqual(r["operational_authority"],"HOLD")
    def test_three_valid_signatures_still_hold(self):
        b,p=fixture();r=assess(b,p)
        self.assertTrue(all(x["valid"] for x in r["observed"]["signatures"]))
        self.assertIn("RAW_OBSERVATIONS_SUPPLIED_NOT_LIVE_ACQUIRED",r["reasons"])
    def test_external_digest_required(self):
        b,p=fixture()
        self.assertIn("OUT_OF_BAND_REGISTRY_DIGEST_REQUIRED",assess(b,"bad")["reasons"])
    def test_registry_mutated(self):
        self.expect(lambda b:b["registry"]["sources"]["source0"].update(hostname="other.example.org"),"REGISTRY_DIGEST_SUBSTITUTION")
    def test_self_issued(self):
        self.expect(lambda b:b["registry"]["controllers"]["controller0"].append("issuer-root"),"SELF_ISSUED_OR_SHARED_ISSUER_ANCESTRY")
    def test_shared_ancestry(self):
        self.expect(lambda b:b["registry"]["controllers"]["controller1"].append("root0"),"SHARED_ACQUISITION_ANCESTRY")
    def test_cycle(self):
        self.expect(lambda b:b["registry"]["controllers"]["root0"].append("controller0"),"CONTROLLER_CYCLE")
    def test_replayed_challenge(self):
        self.expect(lambda b:b["previous_session_nonces"].append("ch274"),"CHALLENGE_NONCE_REPLAY")
    def test_replayed_session_nonce(self):
        self.expect(lambda b:b["previous_session_nonces"].append("n0"),"SESSION_NONCE_CONSUMED")
    def test_duplicate_nonce(self):
        self.expect(lambda b:b["acquisitions"][1].update(session_nonce="n0"),"NONCE_REPLAY_OR_INVALID")
    def test_duplicate_session(self):
        self.expect(lambda b:b["acquisitions"][1].update(session_id="session0"),"SESSION_REPLAY_OR_INVALID")
    def test_duplicate_source(self):
        self.expect(lambda b:b["acquisitions"][1].update(source_id="source0"),"SOURCE_REPLAY_OR_INVALID")
    def test_changed_raw_body(self):
        self.expect(lambda b:b["acquisitions"][0]["observation"].update(raw_b64=base64.b64encode(b"fake").decode()),"RAW_BODY_SHA256_MISMATCH")
    def test_changed_raw_body_hash(self):
        self.expect(lambda b:b["acquisitions"][0]["observation"].update(raw_sha256="f"*64),"PINNED_RAW_BYTES_CONFLICT")
    def test_changed_url(self):
        self.expect(lambda b:b["acquisitions"][0]["observation"].update(requested_url="https://example.org/other"),"ACQUISITION_URL_SUBSTITUTION")
    def test_changed_hostname(self):
        self.expect(lambda b:b["acquisitions"][0]["observation"].update(host="another.example.org"),"SOURCE_HOSTNAME_PIN_MISMATCH")
    def test_unsafe_peer(self):
        self.expect(lambda b:b["acquisitions"][0]["observation"].update(pinned_ip="127.0.0.1"),"PEER_NOT_PUBLIC")
    def test_bad_signature(self):
        self.expect(lambda b:b["acquisitions"][0].update(signed_receipt_b64=base64.b64encode(b"x"*64).decode()),"SIGNED_RECEIPT_INVALID")
    def test_wrong_signer(self):
        self.expect(lambda b:b["acquisitions"][0].update(key_id="key1"),"SOURCE_REGISTRY_PIN_MISMATCH")
    def test_missing_record(self):
        self.expect(lambda b:b["acquisitions"].pop(),"THREE_ACQUISITIONS_REQUIRED")
    def test_invalid_bundle(self):
        self.assertIn("BUNDLE_SCHEMA_INVALID",assess(None,"a"*64)["reasons"])
    def test_never_act(self):
        b,p=fixture();self.assertFalse(assess(b,p)["physical_act_allowed"])
if __name__=="__main__":
    unittest.main()
