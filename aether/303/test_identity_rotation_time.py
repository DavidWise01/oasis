import base64,copy,unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from identity_rotation_time import (REGISTRY,ROTATION,TIME,ZERO,
    sha,canon,qualify,registry_check,rotation_check,time_check)
def pair(name):
    key=Ed25519PrivateKey.generate()
    pem=key.public_key().public_bytes(serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    return key,{"controller_id":name,"public_key_pem":pem}
def sign(key,body,field="signature_b64"):
    body[field]=base64.b64encode(key.sign(canon(body))).decode()
    return body
def fixture():
    registry_sk,registry=pair("registry")
    clock_sk,clock=pair("clock")
    old_sk,old=pair("custodian-old")
    new_sk,new=pair("custodian-new")
    graph={}
    for node in ("source","custodian","registry","clock"):
        graph[node]=[node+"-root"];graph[node+"-root"]=[]
    roots={"registry_key":registry,"clock_key":clock,"ancestry_graph":graph,
           "source_root":"source","custodian_root":"custodian",
           "registry_root":"registry","clock_root":"clock"}
    source="a"*64;receipt="b"*64;custodian="custodian-303"
    old_registration=sign(registry_sk,{"schema":REGISTRY,
        "registry_controller_id":"registry","custodian_id":custodian,
        "key_epoch":1,"custodian_key_sha256":sha(old),
        "previous_registry_sha256":ZERO,"subject_head_sha256":source})
    rotation={"schema":ROTATION,"custodian_id":custodian,
        "old_key_sha256":sha(old),"new_key_sha256":sha(new),
        "from_epoch":1,"to_epoch":2,"previous_rotation_sha256":ZERO,
        "source_head_sha256":source}
    rotation_unsigned=copy.deepcopy(rotation)
    rotation["old_signature_b64"]=base64.b64encode(old_sk.sign(canon(rotation_unsigned))).decode()
    rotation["new_signature_b64"]=base64.b64encode(new_sk.sign(canon(rotation_unsigned))).decode()
    new_registration=sign(registry_sk,{"schema":REGISTRY,
        "registry_controller_id":"registry","custodian_id":custodian,
        "key_epoch":2,"custodian_key_sha256":sha(new),
        "previous_registry_sha256":sha(old_registration),"subject_head_sha256":source})
    times=[];prev=ZERO
    for seq in (1,2):
        claim=sign(clock_sk,{"schema":TIME,"clock_controller_id":"clock",
             "window_seq":seq,"source_head_sha256":source,
             "receipt_head_sha256":receipt,"previous_time_sha256":prev,
             "unix_ms_claim":1800000000000+seq*60000,
             "nonce":f"time-witness-{seq}-unique"})
        times.append(claim);prev=sha(claim)
    bundle={"schema":"AETHER-303/qualification-v1","source_head_sha256":source,
            "receipt_head_sha256":receipt,"custodian_id":custodian,
            "old_key":old,"new_key":new,"old_registry":old_registration,
            "rotation":rotation,"new_registry":new_registration,"time_windows":times}
    return bundle,roots,sha(roots)
class Tests(unittest.TestCase):
    def setUp(self):self.bundle,self.roots,self.pin=fixture()
    def check(self):return qualify(self.bundle,self.roots,self.pin)
    def rejected(self,fragment):
        response=self.check()
        self.assertFalse(response["signature_and_ancestry_claims_consistent"],response)
        self.assertTrue(any(fragment in x for x in response["reasons"]),response)
    def test_valid_claims_still_hold(self):
        result=self.check()
        self.assertTrue(result["signature_and_ancestry_claims_consistent"],result)
        self.assertFalse(result["independent_custodian_identity_verified"])
    def test_two_claimed_windows(self):
        self.assertEqual(self.check()["claimed_elapsed_ms"],60000)
        self.assertFalse(self.check()["independent_elapsed_time_verified"])
    def test_root_pin_mismatch(self):
        self.pin="f"*64;self.rejected("OUT_OF_BAND_ROOT_PIN_MISMATCH")
    def test_shared_controller_ancestry(self):
        self.roots["ancestry_graph"]["clock"]=["source-root"]
        self.pin=sha(self.roots);self.rejected("DECLARED_CONTROLLERS_SHARE_ANCESTRY")
    def test_ancestry_cycle(self):
        self.roots["ancestry_graph"]["clock-root"]=["clock"]
        self.pin=sha(self.roots);self.rejected("ANCESTRY_CYCLE")
    def test_old_registry_signature_corrupt(self):
        self.bundle["old_registry"]["signature_b64"]="AAAA";self.rejected("SIGNATURE_INVALID")
    def test_new_registry_signature_corrupt(self):
        self.bundle["new_registry"]["signature_b64"]="AAAA";self.rejected("SIGNATURE_INVALID")
    def test_new_registry_predecessor_wrong(self):
        self.bundle["new_registry"]["previous_registry_sha256"]="f"*64
        self.rejected("REGISTRY_BINDING_INVALID")
    def test_wrong_old_epoch(self):
        self.bundle["old_registry"]["key_epoch"]=3;self.rejected("REGISTRY_BINDING_INVALID")
    def test_key_replacement(self):
        _,self.bundle["new_key"]=pair("forged-new")
        self.rejected("ROTATION_KEY_SUBSTITUTION")
    def test_missing_old_rotation_signature(self):
        self.bundle["rotation"]["old_signature_b64"]="AAAA"
        self.rejected("OLD_KEY_SIGNATURE_INVALID")
    def test_missing_new_rotation_signature(self):
        self.bundle["rotation"]["new_signature_b64"]="AAAA"
        self.rejected("NEW_KEY_SIGNATURE_INVALID")
    def test_rotation_epoch_skip(self):
        self.bundle["rotation"]["to_epoch"]=4;self.rejected("ROTATION_EPOCH_INVALID")
    def test_rotation_ancestry_conflict(self):
        self.bundle["rotation"]["source_head_sha256"]="f"*64
        self.rejected("ROTATION_ANCESTRY_INVALID")
    def test_receipt_head_substitution(self):
        self.bundle["time_windows"][0]["receipt_head_sha256"]="f"*64
        self.rejected("TIME_SUBJECT_MISMATCH")
    def test_time_signature_corrupt(self):
        self.bundle["time_windows"][0]["signature_b64"]="AAAA"
        self.rejected("SIGNATURE_INVALID")
    def test_time_nonce_reused(self):
        self.bundle["time_windows"][1]["nonce"]=self.bundle["time_windows"][0]["nonce"]
        self.rejected("TIME_NONCE_INVALID_OR_REPLAY")
    def test_time_nonmonotonic(self):
        self.bundle["time_windows"][1]["unix_ms_claim"]=1
        self.rejected("TIME_CLAIM_NOT_INCREASING")
    def test_time_predecessor_invalid(self):
        self.bundle["time_windows"][1]["previous_time_sha256"]="f"*64
        self.rejected("TIME_PREDECESSOR_INVALID")
    def test_missing_clock_window(self):
        self.bundle["time_windows"].pop();self.rejected("TWO_TIME_WINDOWS_REQUIRED")
    def test_source_head_changed(self):
        self.bundle["source_head_sha256"]="f"*64
        self.rejected("REGISTRY_BINDING_INVALID")
    def test_physical_gate_false(self):
        self.assertFalse(self.check()["physical_act_allowed"])
if __name__=="__main__":unittest.main()
