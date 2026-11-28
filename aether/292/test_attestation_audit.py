import base64,copy,json,unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from attestation_audit import (qualify,sha,canon,VERSION_SCHEMA,CLOCK_SCHEMA,ZERO)

def pem(k):
    return k.public_key().public_bytes(serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo).decode()
def sign(k,body):
    body["signature_b64"]=base64.b64encode(k.sign(canon(body))).decode()
    return body

def fixture():
    graph={"journal":["journal-root"],"journal-root":[]}
    owners={};keys={};versions=[];times=[];windows=[];nonces=[]
    clock_key=Ed25519PrivateKey.generate()
    graph["clock"]=["clock-root"];graph["clock-root"]=[]
    providers={}
    for i in range(3):
        kid=f"provider{i}";controller=f"owner{i}"
        k=Ed25519PrivateKey.generate();owners[kid]=k
        graph[controller]=[f"root{i}"];graph[f"root{i}"]=[]
        providers[kid]={"controller_id":controller,"public_key_pem":pem(k)}
    trust={"journal_controller":"journal","graph":graph,"providers":providers,
           "clock":{"controller_id":"clock","public_key_pem":pem(clock_key)}}
    artifact="a"*64
    previous=ZERO
    for seq in (1,2):
        manifest={"schema":"AETHER-291/paired-observation-v1","seq":seq,
                  "window_nonce":f"capture-window-{seq}","previous_head_sha256":previous,
                  "artifact_sha256":artifact,"trust_sha256":"c"*64,
                  "urls":{kid:f"https://vault{i}.example.org/object" for i,kid in enumerate(providers)},
                  "readings":[{"endpoint_id":kid} for kid in providers]}
        digest=sha(manifest)
        windows.append({"seq":seq,"window_nonce":f"capture-window-{seq}",
                        "previous_sha":previous,"head_sha":digest,"artifact_sha":artifact,
                        "trust_sha":"c"*64,"manifest_json":canon(manifest).decode()})
        previous=digest
        for i,(kid,k) in enumerate(owners.items()):
            value={"schema":VERSION_SCHEMA,"controller_id":f"owner{i}",
                   "provider_id":kid,"window_seq":seq,"artifact_sha256":artifact,
                   "object_key":"fixed-object","object_version":"version-1",
                   "object_lock_mode":"COMPLIANCE","retention_until_claim":"2030-01-01",
                   "nonce":f"version-{seq}-{i}"}
            versions.append(sign(k,value))
            nonces.append({"window_seq":seq,"endpoint_id":kid,"value":f"window-{seq}-{i}"})
        time={"schema":CLOCK_SCHEMA,"controller_id":"clock",
              "window_seq":seq,"window_head_sha256":digest,
              "observed_unix_ms_claim":1795800000000+seq*60000,
              "nonce":f"clock-{seq}"}
        times.append(sign(clock_key,time))
    return windows,nonces,trust,sha(trust),versions,times

class Tests(unittest.TestCase):
    def setUp(self):
        self.windows,self.nonces,self.trust,self.pin,self.versions,self.times=fixture()
    def check(self):
        return qualify(self.windows,self.nonces,self.trust,self.pin,self.versions,self.times)
    def expect(self,mutate,reason):
        mutate()
        self.assertIn(reason,self.check()["reasons"])
    def test_all_signatures_valid_still_hold(self):
        result=self.check()
        self.assertTrue(result["observed"]["matching_local_claims"])
        self.assertFalse(result["independent_elapsed_time_verified"])
    def test_version_signature_substitution(self):
        self.expect(lambda:self.versions[0].update(signature_b64="AAAA"),"VERSION_ATTESTATION_INVALID")
    def test_clock_signature_substitution(self):
        self.expect(lambda:self.times[0].update(signature_b64="AAAA"),"CLOCK_ATTESTATION_INVALID")
    def test_changed_object_digest(self):
        self.expect(lambda:self.versions[0].update(artifact_sha256="f"*64),"VERSION_ATTESTATION_INVALID")
    def test_object_version_changed_between_windows(self):
        self.expect(lambda:self.versions[3].update(object_version="version-2"),"VERSION_ATTESTATION_INVALID")
    def test_missing_provider_attestation(self):
        self.versions.pop()
        self.assertIn("SIX_VERSION_AND_TWO_CLOCK_ATTESTATIONS_REQUIRED",self.check()["reasons"])
    def test_missing_clock_attestation(self):
        self.times.pop()
        self.assertIn("SIX_VERSION_AND_TWO_CLOCK_ATTESTATIONS_REQUIRED",self.check()["reasons"])
    def test_reused_attestation_nonce(self):
        self.expect(lambda:self.versions[1].update(nonce=self.versions[0]["nonce"]),"ATTESTATION_NONCE_REUSE")
    def test_clock_replayed_nonce(self):
        self.expect(lambda:self.times[0].update(nonce=self.versions[0]["nonce"]),"ATTESTATION_NONCE_REUSE")
    def test_clock_head_mismatch(self):
        self.expect(lambda:self.times[0].update(window_head_sha256="f"*64),"CLOCK_ATTESTATION_INVALID")
    def test_reversed_clock_order(self):
        self.times[1]["observed_unix_ms_claim"]=self.times[0]["observed_unix_ms_claim"]-1
        self.assertIn("CLOCK_WINDOW_NOT_INCREASING",self.check()["reasons"])
    def test_pin_substitution(self):
        self.pin="f"*64
        self.assertIn("OUT_OF_BAND_TRUST_PIN_MISMATCH",self.check()["reasons"])
    def test_shared_provider_ancestry(self):
        self.trust["graph"]["owner1"].append("root0")
        self.pin=sha(self.trust)
        self.assertIn("PROVIDER_SHARED_ANCESTRY",self.check()["reasons"])
    def test_clock_shared_provider_ancestry(self):
        self.trust["graph"]["clock"].append("root0")
        self.pin=sha(self.trust)
        self.assertIn("CLOCK_PROVIDER_SHARED_ANCESTRY",self.check()["reasons"])
    def test_clock_journal_shared_ancestry(self):
        self.trust["graph"]["clock"].append("journal-root")
        self.pin=sha(self.trust)
        self.assertIn("CLOCK_JOURNAL_SHARED_ANCESTRY",self.check()["reasons"])
    def test_missing_second_window(self):
        self.windows.pop()
        self.assertIn("TWO_COMPLETE_WINDOWS_REQUIRED",self.check()["reasons"])
    def test_window_reading_source_mismatch(self):
        m=json.loads(self.windows[0]["manifest_json"])
        m["readings"][0]["endpoint_id"]="unapproved"
        self.windows[0]["manifest_json"]=canon(m).decode()
        self.assertIn("PROVIDER_WINDOW_SOURCE_MISMATCH",self.check()["reasons"])
    def test_duplicate_version_slot(self):
        self.versions[1]["window_seq"]=1
        self.versions[1]["provider_id"]="provider0"
        self.assertIn("VERSION_ATTESTATION_DUPLICATE",self.check()["reasons"])
    def test_no_act(self):
        self.assertFalse(self.check()["physical_act_allowed"])
if __name__=="__main__":unittest.main()
