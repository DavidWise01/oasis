import base64,hashlib,unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from transport_compare import assess,canon,sha,hash_bytes

def fixture():
    raw=b"immutable snapshot";body=hash_bytes(raw)
    challenge={"challenge_id":"fresh-266","nonce":"challenge-nonce","run_id":266,
               "source_commit":"a"*40,"resource_url":"https://example.org/checkpoint",
               "expected_body_sha256":body}
    pin={"challenge_sha256":sha(challenge),"pin_source_id":"declared-external"}
    pin["pin_receipt_sha256"]=sha(pin)
    keys={};sessions=[]
    for i in range(3):
        obs={"schema":"AETHER-264/https-acquisition-v1","requested_url":challenge["resource_url"],
             "host":"example.org","pinned_ip":"8.8.8.8","dns_address_count":1,
             "tls_hostname_validation":True,"status":200,"elapsed_ms":10,
             "raw_length":len(raw),"raw_sha256":body,
             "raw_b64":base64.b64encode(raw).decode()}
        obs["observation_sha256"]=hash_bytes(canon(obs))
        sid="session"+str(i);nonce="session-nonce-"+str(i);controller="controller"+str(i);kid="key"+str(i)
        stmt={"schema":"AETHER-266/transport-comparison-v1","challenge_sha256":sha(challenge),
              "session_id":sid,"session_nonce":nonce,"controller_claim":controller,
              "observation_sha256":obs["observation_sha256"]}
        priv=Ed25519PrivateKey.generate()
        sessions.append({"session_id":sid,"session_nonce":nonce,"controller_claim":controller,
                         "key_id":kid,"observation":obs,
                         "signature_b64":base64.b64encode(priv.sign(canon(stmt))).decode()})
        keys[kid]={"controller_claim":controller,
                   "public_key_pem":priv.public_key().public_bytes(
                       serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()}
    return {"challenge":challenge,"externally_claimed_challenge_pin":pin,
            "sessions":sessions,"key_pins":keys,"prior_session_nonces":[]}

class Tests(unittest.TestCase):
    def test_valid_signatures_still_hold(self):
        result=assess(fixture())
        self.assertTrue(all(x["signature_valid"] for x in result["observed"]["sessions"]))
        self.assertIn("THREE_TRANSPORT_SESSIONS_NOT_INDEPENDENTLY_ATTESTED",result["reasons"])
    def test_pin_substitution(self):
        b=fixture();b["challenge"]["nonce"]="changed"
        self.assertIn("CHALLENGE_PIN_MISMATCH",assess(b)["reasons"])
    def test_pin_receipt_corrupt(self):
        b=fixture();b["externally_claimed_challenge_pin"]["pin_receipt_sha256"]="0"*64
        self.assertIn("PIN_RECEIPT_HASH_INVALID",assess(b)["reasons"])
    def test_challenge_replay(self):
        b=fixture();b["prior_session_nonces"].append(b["challenge"]["nonce"])
        self.assertIn("CHALLENGE_REPLAY",assess(b)["reasons"])
    def test_session_replay(self):
        b=fixture();b["prior_session_nonces"].append(b["sessions"][0]["session_nonce"])
        self.assertIn("SESSION_NONCE_REPLAY",assess(b)["reasons"])
    def test_duplicate_session_id(self):
        b=fixture();b["sessions"][1]["session_id"]=b["sessions"][0]["session_id"]
        self.assertIn("DUPLICATE_SESSION_ID",assess(b)["reasons"])
    def test_duplicate_nonce(self):
        b=fixture();b["sessions"][1]["session_nonce"]=b["sessions"][0]["session_nonce"]
        self.assertIn("SESSION_NONCE_REPLAY",assess(b)["reasons"])
    def test_shared_controller_label(self):
        b=fixture();b["sessions"][1]["controller_claim"]=b["sessions"][0]["controller_claim"]
        self.assertIn("DUPLICATE_CONTROLLER_CLAIM",assess(b)["reasons"])
    def test_substituted_body(self):
        b=fixture();s=b["sessions"][1]["observation"];s["raw_b64"]=base64.b64encode(b"other").decode()
        s["raw_sha256"]=hash_bytes(b"other")
        self.assertIn("BODY_CONFLICT_WITH_PIN",assess(b)["reasons"])
        self.assertIn("INCONSISTENT_READBACK_BODIES",assess(b)["reasons"])
    def test_wrong_resource(self):
        b=fixture();b["sessions"][0]["observation"]["requested_url"]="https://example.org/other"
        self.assertIn("RESOURCE_SUBSTITUTION",assess(b)["reasons"])
    def test_corrupted_signature(self):
        b=fixture();b["sessions"][0]["signature_b64"]=base64.b64encode(b"x"*64).decode()
        self.assertIn("SIGNATURE_INVALID",assess(b)["reasons"])
    def test_key_substitution(self):
        b=fixture();b["key_pins"]["key0"]["public_key_pem"]=b["key_pins"]["key1"]["public_key_pem"]
        self.assertIn("SIGNATURE_INVALID",assess(b)["reasons"])
    def test_missing_session(self):
        b=fixture();b["sessions"].pop()
        self.assertIn("THREE_SESSIONS_REQUIRED",assess(b)["reasons"])
    def test_unsafe_peer(self):
        b=fixture();b["sessions"][0]["observation"]["pinned_ip"]="127.0.0.1"
        self.assertIn("UNSAFE_PEER",assess(b)["reasons"])
    def test_length_mutation(self):
        b=fixture();b["sessions"][0]["observation"]["raw_length"]=999
        self.assertIn("BODY_LENGTH_INVALID",assess(b)["reasons"])
    def test_observation_hash_mutation(self):
        b=fixture();b["sessions"][0]["observation"]["observation_sha256"]="0"*64
        self.assertIn("OBSERVATION_HASH_MISMATCH",assess(b)["reasons"])
    def test_missing_pin(self):
        b=fixture();b["externally_claimed_challenge_pin"]={}
        self.assertIn("CHALLENGE_PIN_SCHEMA_INVALID",assess(b)["reasons"])
    def test_missing_key(self):
        b=fixture();b["key_pins"].pop("key0")
        self.assertIn("SIGNER_PIN_MISSING",assess(b)["reasons"])
    def test_bad_bundle(self):
        self.assertIn("BUNDLE_INVALID",assess(None)["reasons"])
    def test_never_authorizes(self):
        self.assertFalse(assess(fixture())["physical_act_allowed"])
if __name__=="__main__":unittest.main()
