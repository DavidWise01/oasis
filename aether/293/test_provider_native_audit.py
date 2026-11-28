import base64,copy,json,unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from provider_native_audit import verify_chain,sha,canon,VERSION,CLOCK,ZERO

def pem(k):
    return k.public_key().public_bytes(serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo).decode()

def fixture():
    graph={"journal":["jr"],"jr":[],"clock":["cr"],"cr":[]}
    keys={};providers={};windows=[];records=[];times=[]
    clock_key=Ed25519PrivateKey.generate()
    for i in range(3):
        kid=f"provider{i}";owner=f"owner{i}"
        graph[owner]=[f"root{i}"];graph[f"root{i}"]=[]
        providers[kid]={"controller_id":owner,"api_origin_claim":f"https://provider{i}.example.org"}
    trust={"journal_controller":"journal","graph":graph,"providers":providers,
           "clock":{"controller_id":"clock","public_key_pem":pem(clock_key)}}
    previous=ZERO
    for seq in (1,2):
        windows.append({"artifact_sha":"a"*64,"head_sha":f"{seq}"*64})
        for i in range(3):
            kid=f"provider{i}";url=f"https://provider{i}.example.org/object/version"
            data={"schema":VERSION,"provider_id":kid,"window_seq":seq,
                  "artifact_sha256":"a"*64,"object_key":"stable-object",
                  "version_id":"v1","lock_mode":"COMPLIANCE",
                  "retention_until_claim":"2031-01-01",
                  "response_request_id":f"request{seq}-{i}","response_nonce":f"nonce{seq}-{i}"}
            raw=canon(data)
            records.append({"provider_id":kid,"window_seq":seq,"url":url,
                            "raw_b64":base64.b64encode(raw).decode(),
                            "raw_sha256":__import__("hashlib").sha256(raw).hexdigest(),
                            "transport":{"tls_peer_claim":True,"response_status":200,
                               "request_id":data["response_request_id"],
                               "acquisition_observation_sha256":"c"*64}})
        claim={"schema":CLOCK,"controller_id":"clock","window_seq":seq,
               "window_head_sha256":windows[-1]["head_sha"],
               "previous_attestation_sha256":previous,
               "unix_ms_claim":1700000000000+seq*60000,"nonce":f"clocknonce{seq}"}
        claim["signature_b64"]=base64.b64encode(clock_key.sign(canon(claim))).decode()
        times.append(claim)
        previous=sha(claim)
    return windows,[],trust,sha(trust),records,times

class Tests(unittest.TestCase):
    def setUp(self):
        self.windows,self.nonces,self.trust,self.pin,self.records,self.times=fixture()
    def check(self):
        return verify_chain(self.windows,self.records,self.times,self.trust,self.pin)
    def has(self,reason):
        self.assertIn(reason,self.check()["reasons"])
    def test_valid_claims_still_hold(self):
        report=self.check()
        self.assertTrue(report["observed"]["input_claims_consistent"],report)
        self.assertFalse(report["provider_api_authentication_verified"])
    def test_six_provider_records(self):
        self.assertEqual(self.check()["observed"]["provider_records"],6)
    def test_claimed_interval_not_trusted(self):
        report=self.check()
        self.assertEqual(report["observed"]["clock_claimed_interval_ms"],60000)
        self.assertFalse(report["independent_clock_authority_verified"])
    def test_trust_pin_mismatch(self):
        self.pin="f"*64;self.has("TRUST_ROOT_PIN_MISMATCH")
    def test_missing_response(self):
        self.records.pop()
        self.has("SIX_PROVIDER_AND_TWO_CLOCK_RECORDS_REQUIRED")
    def test_missing_clock(self):
        self.times.pop()
        self.has("SIX_PROVIDER_AND_TWO_CLOCK_RECORDS_REQUIRED")
    def test_provider_raw_tamper(self):
        self.records[0]["raw_b64"]="AAAA"
        self.has("RETAINED_PROVIDER_RESPONSE_INVALID")
    def test_provider_digest_tamper(self):
        self.records[0]["raw_sha256"]="f"*64
        self.has("RETAINED_PROVIDER_RESPONSE_INVALID")
    def test_transport_request_tamper(self):
        self.records[0]["transport"]["request_id"]="substituted"
        self.has("RETAINED_PROVIDER_RESPONSE_INVALID")
    def test_provider_origin_substitution(self):
        self.records[0]["url"]="https://evil.example.org/object/version"
        self.has("PROVIDER_API_ORIGIN_MISMATCH")
    def test_duplicate_provider_slot(self):
        self.records[1]=copy.deepcopy(self.records[0])
        self.has("DUPLICATE_PROVIDER_WINDOW")
    def test_version_change(self):
        response=json.loads(base64.b64decode(self.records[3]["raw_b64"]))
        response["version_id"]="v2"
        raw=canon(response)
        self.records[3]["raw_b64"]=base64.b64encode(raw).decode()
        self.records[3]["raw_sha256"]=__import__("hashlib").sha256(raw).hexdigest()
        self.has("OBJECT_VERSION_CHANGED_ACROSS_WINDOWS")
    def test_clock_signature_tamper(self):
        self.times[0]["signature_b64"]="AAAA"
        self.has("CLOCK_SIGNATURE_INVALID")
    def test_clock_head_conflict(self):
        self.times[0]["window_head_sha256"]="f"*64
        self.has("CLOCK_WINDOW_BINDING_INVALID")
    def test_clock_chain_tamper(self):
        self.times[1]["previous_attestation_sha256"]="f"*64
        self.has("CLOCK_CHAIN_PREDECESSOR_INVALID")
    def test_clock_reversed(self):
        self.times[1]["unix_ms_claim"]=1
        self.has("CLOCK_TIME_NONMONOTONIC")
    def test_shared_ancestry(self):
        self.trust["graph"]["owner1"].append("root0")
        self.pin=sha(self.trust)
        self.has("PROVIDERS_SHARED_ANCESTRY")
    def test_clock_journal_ancestry(self):
        self.trust["graph"]["clock"].append("jr")
        self.pin=sha(self.trust)
        self.has("CLOCK_JOURNAL_SHARED_ANCESTRY")
    def test_no_act(self):
        self.assertFalse(self.check()["physical_act_allowed"])

if __name__=="__main__":unittest.main()
