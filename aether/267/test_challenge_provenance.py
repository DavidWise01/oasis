import base64,unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from challenge_provenance import assess,canon,sha,SCHEMA

def fixture():
    challenge={"challenge_id":"fresh-267","nonce":"challenge-nonce","run_id":267,
               "source_commit":"a"*40,"resource_url":"https://example.org/item",
               "expected_body_sha256":"b"*64}
    graph={"issuer":["issuer-root"],"issuer-root":[]}
    issue_priv=Ed25519PrivateKey.generate()
    statement={"schema":SCHEMA,"custodian_id":"separate-store","controller_id":"issuer",
               "challenge_sha256":sha(challenge),"issuance_nonce":"issue-nonce"}
    issuance={"custodian_id":"separate-store","controller_id":"issuer","key_id":"issue-key",
              "challenge_sha256":sha(challenge),"issuance_nonce":"issue-nonce",
              "signature_b64":base64.b64encode(issue_priv.sign(canon(statement))).decode()}
    pub=lambda private:private.public_key().public_bytes(
        serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    pin={"key_id":"issue-key","controller_id":"issuer","public_key_pem":pub(issue_priv)}
    transports=[];keys={}
    for i in range(3):
        sid="session"+str(i);nonce="transport-nonce-"+str(i);controller="agent"+str(i)
        graph[controller]=["root"+str(i)];graph["root"+str(i)]=[]
        receipt={"session_id":sid,"session_nonce":nonce,"source_id":"source"+str(i),
                 "controller_id":controller,"key_id":"key"+str(i),
                 "challenge_sha256":sha(challenge),"body_sha256":"b"*64}
        priv=Ed25519PrivateKey.generate()
        signed={k:v for k,v in receipt.items() if k!="key_id"}
        signed["schema"]=SCHEMA
        receipt["signature_b64"]=base64.b64encode(priv.sign(canon(signed))).decode()
        transports.append(receipt)
        keys["key"+str(i)]={"controller_id":controller,"public_key_pem":pub(priv)}
    return {"challenge":challenge,"issuance_receipt":issuance,"issuance_key_pin":pin,
            "transport_receipts":transports,"transport_key_pins":keys,
            "controller_ancestry":graph,"previously_consumed_nonces":[]}

class Tests(unittest.TestCase):
    def expect(self,change,reason):
        b=fixture();change(b);r=assess(b)
        self.assertIn(reason,r["reasons"],r)
        self.assertEqual(r["operational_authority"],"HOLD")
    def test_correct_signatures_still_hold(self):
        r=assess(fixture())
        self.assertTrue(r["observed"]["issuance_signature_valid"])
        self.assertTrue(all(x["signature_valid"] for x in r["observed"]["transport_signatures"]))
        self.assertIn("ISSUANCE_KEY_CUSTODY_NOT_EXTERNALLY_ATTESTED",r["reasons"])
    def test_self_issued(self):
        self.expect(lambda b:b["controller_ancestry"]["agent0"].append("issuer-root"),
                    "SELF_ISSUED_CHALLENGE_OR_SHARED_CUSTODY")
    def test_shared_transport_ancestry(self):
        self.expect(lambda b:b["controller_ancestry"]["agent1"].append("root0"),"TRANSPORT_SHARED_ANCESTRY")
    def test_ancestry_cycle(self):
        self.expect(lambda b:b["controller_ancestry"]["issuer-root"].append("issuer"),"ANCESTRY_CYCLE")
    def test_missing_ancestor(self):
        self.expect(lambda b:b["controller_ancestry"].pop("issuer-root"),"ANCESTRY_NODE_MISSING")
    def test_issuance_challenge_changed(self):
        self.expect(lambda b:b["challenge"].update(challenge_id="forged"),"ISSUANCE_CHALLENGE_MISMATCH")
    def test_issuance_signature_corrupted(self):
        self.expect(lambda b:b["issuance_receipt"].update(signature_b64=base64.b64encode(b"x"*64).decode()),"ISSUANCE_SIGNATURE_INVALID")
    def test_issuance_key_substitution(self):
        self.expect(lambda b:b["issuance_key_pin"].update(public_key_pem=b["transport_key_pins"]["key0"]["public_key_pem"]),"ISSUANCE_SIGNATURE_INVALID")
    def test_receipt_body_substituted(self):
        self.expect(lambda b:b["transport_receipts"][0].update(body_sha256="c"*64),"TRANSPORT_BODY_PIN_MISMATCH")
    def test_receipt_challenge_substituted(self):
        self.expect(lambda b:b["transport_receipts"][0].update(challenge_sha256="c"*64),"TRANSPORT_CHALLENGE_MISMATCH")
    def test_transport_signature_corrupted(self):
        self.expect(lambda b:b["transport_receipts"][0].update(signature_b64=base64.b64encode(b"x"*64).decode()),"TRANSPORT_SIGNATURE_INVALID")
    def test_duplicate_session_id(self):
        self.expect(lambda b:b["transport_receipts"][1].update(session_id="session0"),"SESSION_ID_REPLAY")
    def test_duplicate_session_nonce(self):
        self.expect(lambda b:b["transport_receipts"][1].update(session_nonce="transport-nonce-0"),"TRANSPORT_NONCE_REPLAY")
    def test_prior_challenge_nonce(self):
        self.expect(lambda b:b["previously_consumed_nonces"].append("challenge-nonce"),"CHALLENGE_ALREADY_CONSUMED")
    def test_prior_transport_nonce(self):
        self.expect(lambda b:b["previously_consumed_nonces"].append("transport-nonce-0"),"TRANSPORT_NONCE_REPLAY")
    def test_prior_issuer_nonce(self):
        self.expect(lambda b:b["previously_consumed_nonces"].append("issue-nonce"),"ISSUANCE_NONCE_REPLAY")
    def test_transport_key_reused_from_issuer(self):
        self.expect(lambda b:b["transport_receipts"][0].update(key_id="issue-key"),"TRANSPORT_SIGNER_KEY_REUSE")
    def test_missing_transport(self):
        self.expect(lambda b:b["transport_receipts"].pop(),"THREE_TRANSPORT_RECEIPTS_REQUIRED")
    def test_invalid_source_commit(self):
        self.expect(lambda b:b["challenge"].update(source_commit="bad"),"COMMIT_INVALID")
    def test_none(self):
        self.assertIn("BUNDLE_INVALID",assess(None)["reasons"])
    def test_no_act(self):
        self.assertFalse(assess(fixture())["physical_act_allowed"])
if __name__=="__main__":
    unittest.main()
