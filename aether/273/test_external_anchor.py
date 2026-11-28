import base64,copy,unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from external_anchor import ANCHOR_SCHEMA,TRANSCRIPT_SCHEMA,canonical,sha,sha_bytes,review

def fixture():
    challenge={"challenge_id":"challenge-273","nonce":"cnonce-273","source_commit":"a"*40,"run_id":273}
    rows=[];private_keys={}
    for i in range(3):
        key=Ed25519PrivateKey.generate();kid="key"+str(i)
        private_keys[kid]=key
        rows.append({"key_id":kid,"source_id":"source"+str(i),
                     "controller_id":"owner"+str(i),"public_key_pem":key.public_key().public_bytes(
                         serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()})
    regdigest=sha(rows)
    statement={"schema":ANCHOR_SCHEMA,"registry_sha256":regdigest,"epoch":7,
               "challenge_count_floor":10,"anchor_nonce":"anchored-273","controller_claim":"claimed-custodian"}
    anchor_key=Ed25519PrivateKey.generate()
    anchor={"statement":statement,
            "signature_b64":base64.b64encode(anchor_key.sign(canonical(statement))).decode()}
    raw=b"stable retained body"
    reads=[]
    for i,row in enumerate(rows):
        data={"session_id":"s"+str(i),"session_nonce":"rnonce"+str(i),
              "key_id":row["key_id"],"source_id":row["source_id"],
              "controller_id":row["controller_id"],"requested_url":"https://example.org/receipt",
              "raw_b64":base64.b64encode(raw).decode(),"raw_sha256":sha_bytes(raw)}
        signed={"schema":TRANSCRIPT_SCHEMA,"challenge":challenge,"registry_sha256":regdigest,
                **{k:data[k] for k in ("session_id","session_nonce","key_id","source_id",
                                       "controller_id","requested_url","raw_sha256")}}
        data["signature_b64"]=base64.b64encode(private_keys[row["key_id"]].sign(canonical(signed))).decode()
        reads.append(data)
    bundle={"anchor":anchor,"anchor_key_pem":anchor_key.public_key().public_bytes(
            serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode(),
            "registry":{"rows":rows,"sealed_sha256":regdigest,"challenge_count":11},
            "readbacks":reads,"challenge":challenge,"previous_challenge_nonces":[]}
    return bundle,sha(statement)

class Tests(unittest.TestCase):
    def expect(self,change,reason):
        b,p=fixture();change(b);r=review(b,p)
        self.assertIn(reason,r["reasons"],r)
        self.assertFalse(r["physical_act_allowed"])
    def test_signatures_valid_custody_still_hold(self):
        b,p=fixture();r=review(b,p)
        self.assertTrue(r["observed"]["anchor_signature_valid"])
        self.assertTrue(all(x["signature_valid"] for x in r["observed"]["signed_transcripts"]))
        self.assertIn("HTTP_ACQUISITION_NOT_INDEPENDENTLY_OBSERVED",r["reasons"])
    def test_pin_required(self):
        b,p=fixture();self.assertIn("OUT_OF_BAND_ANCHOR_DIGEST_REQUIRED",review(b,None)["reasons"])
    def test_wrong_out_of_band_anchor(self):
        b,p=fixture();self.assertIn("OUT_OF_BAND_ANCHOR_MISMATCH",review(b,"f"*64)["reasons"])
    def test_counter_rollback(self):
        self.expect(lambda b:b["registry"].update(challenge_count=9),"CHALLENGE_COUNTER_ROLLBACK")
    def test_registry_digest_replacement(self):
        self.expect(lambda b:b["registry"].update(sealed_sha256="f"*64),"REGISTRY_ROLLBACK_OR_SUBSTITUTION")
    def test_registry_key_substitution(self):
        self.expect(lambda b:b["registry"]["rows"][0].update(public_key_pem=b["registry"]["rows"][1]["public_key_pem"]),"REGISTRY_SEAL_INVALID")
    def test_registry_duplicate_source(self):
        self.expect(lambda b:b["registry"]["rows"][1].update(source_id="source0"),"REGISTRY_DUPLICATE_IDENTITY")
    def test_registry_reorder(self):
        self.expect(lambda b:b["registry"]["rows"].reverse(),"REGISTRY_ORDER_INVALID")
    def test_anchor_signature_corrupt(self):
        self.expect(lambda b:b["anchor"].update(signature_b64=base64.b64encode(b"x"*64).decode()),"ANCHOR_SIGNATURE_INVALID")
    def test_anchor_key_substituted(self):
        self.expect(lambda b:b.update(anchor_key_pem=b["registry"]["rows"][0]["public_key_pem"]),"ANCHOR_SIGNATURE_INVALID")
    def test_challenge_replayed(self):
        self.expect(lambda b:b["previous_challenge_nonces"].append("cnonce-273"),"CHALLENGE_REPLAY")
    def test_receipt_nonce_replayed(self):
        self.expect(lambda b:b["previous_challenge_nonces"].append("rnonce0"),"READBACK_NONCE_REPLAY")
    def test_duplicate_receipt_nonce(self):
        self.expect(lambda b:b["readbacks"][1].update(session_nonce="rnonce0"),"READBACK_NONCE_REPLAY")
    def test_duplicate_session(self):
        self.expect(lambda b:b["readbacks"][1].update(session_id="s0"),"DUPLICATE_SESSION")
    def test_substituted_raw_bytes(self):
        self.expect(lambda b:b["readbacks"][0].update(raw_b64=base64.b64encode(b"forged").decode()),"RAW_BODY_TAMPER")
    def test_substituted_body_with_hash(self):
        def change(b):
            b["readbacks"][0]["raw_b64"]=base64.b64encode(b"forged").decode()
            b["readbacks"][0]["raw_sha256"]=sha_bytes(b"forged")
        self.expect(change,"RAW_READBACK_CONFLICT")
    def test_corrupt_receipt_signature(self):
        self.expect(lambda b:b["readbacks"][0].update(signature_b64=base64.b64encode(b"x"*64).decode()),"READBACK_SIGNATURE_INVALID")
    def test_unknown_signer(self):
        self.expect(lambda b:b["readbacks"][0].update(key_id="unknown"),"REGISTRY_SIGNER_MISMATCH")
    def test_missing_readback(self):
        self.expect(lambda b:b["readbacks"].pop(),"THREE_RAW_READBACKS_REQUIRED")
    def test_bad_bundle(self):
        self.assertIn("BUNDLE_INVALID",review(None,"a"*64)["reasons"])
    def test_no_act(self):
        b,p=fixture();self.assertEqual(review(b,p)["operational_authority"],"HOLD")
if __name__=="__main__":unittest.main()
