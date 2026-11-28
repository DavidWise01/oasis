import base64,json,sys,unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from live_capture import collect,keyring,body,check_record,canon,sha_bytes

def fixture():
    challenge="fresh-275-challenge-abcdef123456"
    ring={"schema":"AETHER-275/keyring-v1","sources":[]}
    keys={}
    for i in range(3):
        s={"source_id":"source"+str(i),"controller_claim":"controller"+str(i),
           "url":"https://source"+str(i)+".example.org/record"}
        k=Ed25519PrivateKey.generate()
        keys[s["url"]]=k
        s["public_key_pem"]=k.public_key().public_bytes(serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo).decode()
        ring["sources"].append(s)
    raw_ring=canon(ring)
    key_url="https://registry.example.org/keyring"
    responses={key_url:raw_ring}
    for s in ring["sources"]:
        blob=b"same payload"
        statement={"schema":"AETHER-275/signature-v1","source_id":s["source_id"],
                   "challenge_nonce":challenge,"payload_sha256":sha_bytes(blob)}
        record={"schema":"AETHER-275/signed-record-v1","challenge_nonce":challenge,
                "payload_b64":base64.b64encode(blob).decode(),
                "signature_b64":base64.b64encode(keys[s["url"]].sign(canon(statement))).decode()}
        responses[s["url"]]=canon(record)
    def fake(url,allow):
        assert url.split("/")[2] in allow
        raw=responses[url]
        return {"requested_url":url,"raw_b64":base64.b64encode(raw).decode(),
                "raw_length":len(raw),"raw_sha256":sha_bytes(raw)}
    hosts=["registry.example.org"]+["source"+str(i)+".example.org" for i in range(3)]
    return ring,key_url,sha_bytes(raw_ring),challenge,hosts,responses,fake

class Tests(unittest.TestCase):
    def test_three_crypto_signatures_still_hold(self):
        _,url,pin,c,hosts,_,fake=fixture()
        result=collect(url,pin,c,hosts,fake)
        self.assertEqual(len(result["signed_receipts"]),3)
        self.assertTrue(result["payload_agreement"])
        self.assertFalse(result["independent_external_custody_proven"])
    def test_modified_keyring_rejected(self):
        ring,url,pin,c,hosts,responses,fake=fixture()
        responses[url]=b"changed"
        with self.assertRaisesRegex(ValueError,"KEYRING_PIN_MISMATCH"):
            collect(url,pin,c,hosts,fake)
    def test_missing_source_allowlist(self):
        _,url,pin,c,hosts,_,fake=fixture()
        with self.assertRaisesRegex(ValueError,"SOURCE_HOST_NOT_ALLOWED"):
            collect(url,pin,c,hosts[:-1],fake)
    def test_reused_controller_label(self):
        ring,url,pin,c,hosts,_,fake=fixture()
        ring["sources"][1]["controller_claim"]=ring["sources"][0]["controller_claim"]
        with self.assertRaisesRegex(ValueError,"SOURCE_LABEL_OR_HOST_REUSE"):
            keyring(canon(ring),sha_bytes(canon(ring)))
    def test_duplicate_hostname(self):
        ring,url,pin,c,hosts,_,fake=fixture()
        ring["sources"][1]["url"]=ring["sources"][0]["url"]
        with self.assertRaisesRegex(ValueError,"SOURCE_LABEL_OR_HOST_REUSE"):
            keyring(canon(ring),sha_bytes(canon(ring)))
    def test_bad_challenge(self):
        _,url,pin,c,hosts,_,fake=fixture()
        with self.assertRaisesRegex(ValueError,"FRESH_CHALLENGE_REQUIRED"):
            collect(url,pin,"a",hosts,fake)
    def test_http_keyring_rejected(self):
        _,url,pin,c,hosts,_,fake=fixture()
        with self.assertRaisesRegex(ValueError,"HTTPS_URL_INVALID"):
            collect("http://registry.example.org/keyring",pin,c,hosts,fake)
    def test_signature_replacement(self):
        ring,url,pin,c,hosts,responses,fake=fixture()
        src=ring["sources"][0]["url"];record=json.loads(responses[src])
        record["signature_b64"]=base64.b64encode(b"x"*64).decode()
        responses[src]=canon(record)
        with self.assertRaisesRegex(ValueError,"SIGNATURE_INVALID"):
            collect(url,pin,c,hosts,fake)
    def test_challenge_binding(self):
        ring,url,pin,c,hosts,responses,fake=fixture()
        src=ring["sources"][0]["url"];record=json.loads(responses[src])
        record["challenge_nonce"]="changed"
        responses[src]=canon(record)
        with self.assertRaisesRegex(ValueError,"CHALLENGE_BINDING_MISMATCH"):
            collect(url,pin,c,hosts,fake)
    def test_raw_digest_corruption(self):
        ring,url,pin,c,hosts,responses,fake=fixture()
        src=ring["sources"][0]["url"];wrapped=fake(src,[src.split("/")[2]])
        wrapped["raw_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"RAW_BODY_TAMPER"):body(wrapped)
    def test_nested_payload_oversize_rejected_at_outer_limit(self):
        ring,url,pin,c,hosts,responses,fake=fixture()
        src=ring["sources"][0]["url"];record=json.loads(responses[src])
        record["payload_b64"]=base64.b64encode(b"x"*65537).decode()
        responses[src]=canon(record)
        with self.assertRaisesRegex(ValueError,"RAW_BODY_TAMPER"):
            collect(url,pin,c,hosts,fake)
    def test_custody_never_authorized(self):
        _,url,pin,c,hosts,_,fake=fixture()
        self.assertFalse(collect(url,pin,c,hosts,fake)["physical_act_allowed"])
if __name__=="__main__":unittest.main()