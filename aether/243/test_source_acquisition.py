import hashlib,unittest
from source_acquisition import assess
def fixture():
    hosts=["alpha.example.org","beta.example.org","gamma.example.org"]
    return {"allowed_hosts":hosts,"sources":[{"source_id":str(i),"url":"https://"+h+"/evidence.bin",
      "controller_claim":"controller-"+str(i),"expected_sha256":hashlib.sha256(("evidence-"+str(i)).encode()).hexdigest()}
      for i,h in enumerate(hosts)]}
def mock(url):
    hosts=["alpha.example.org","beta.example.org","gamma.example.org"]
    return ("evidence-"+str(hosts.index(url.split("/")[2]))).encode()
class Tests(unittest.TestCase):
    def expect(self,mutate,reason,fetch=mock):
        c=fixture();mutate(c);r=assess(c,fetch)
        self.assertIn(reason,r["reasons"],r);self.assertEqual(r["operational_authority"],"HOLD")
    def test_consistent_unqualified(self):self.expect(lambda c:None,"CONTROLLER_ANCESTRY_AND_EXTERNAL_CUSTODY_UNAUTHENTICATED")
    def test_physical_hold(self):self.assertEqual(assess(fixture(),mock)["physical_qualification_percent"],0)
    def test_digest(self):self.expect(lambda c:c["sources"][0].update(expected_sha256="0"*64),"RESPONSE_DIGEST_MISMATCH")
    def test_duplicate_id(self):self.expect(lambda c:c["sources"][1].update(source_id="0"),"SOURCE_ID_DUPLICATE_OR_INVALID")
    def test_shared_controller(self):self.expect(lambda c:c["sources"][1].update(controller_claim="controller-0"),"SHARED_DECLARED_CONTROLLER")
    def test_http(self):self.expect(lambda c:c["sources"][0].update(url="http://alpha.example.org/a"),"FETCH_OR_VALIDATION_FAILED:ValueError")
    def test_unpinned_host(self):self.expect(lambda c:c["sources"][0].update(url="https://other.example.org/a"),"FETCH_OR_VALIDATION_FAILED:ValueError")
    def test_credentials(self):self.expect(lambda c:c["sources"][0].update(url="https://me:secret@alpha.example.org/a"),"FETCH_OR_VALIDATION_FAILED:ValueError")
    def test_fragment(self):self.expect(lambda c:c["sources"][0].update(url="https://alpha.example.org/a#b"),"FETCH_OR_VALIDATION_FAILED:ValueError")
    def test_local_ip(self):
        self.expect(lambda c:(c["allowed_hosts"].append("127.0.0.1"),c["sources"][0].update(url="https://127.0.0.1/a")),"FETCH_OR_VALIDATION_FAILED:ValueError")
    def test_no_source(self):self.expect(lambda c:c["sources"].clear(),"SOURCE_SET_INVALID")
    def test_no_hosts(self):self.expect(lambda c:c["allowed_hosts"].clear(),"HOST_PINS_INVALID")
    def test_bad_body(self):self.expect(lambda c:None,"FETCH_OR_VALIDATION_FAILED:ValueError",lambda url:"string")
    def test_transport(self):
        def fail(url):raise OSError("offline")
        self.expect(lambda c:None,"FETCH_OR_VALIDATION_FAILED:OSError",fail)
    def test_duplicate_bytes(self):
        c=fixture();raw=b"same"
        for s in c["sources"]:s["expected_sha256"]=hashlib.sha256(raw).hexdigest()
        self.assertIn("DUPLICATE_EVIDENCE_BYTES",assess(c,lambda url:raw)["reasons"])
    def test_invalid_config(self):self.assertIn("CONFIG_INVALID",assess(None,mock)["reasons"])
    def test_bad_expected_digest(self):self.expect(lambda c:c["sources"][0].update(expected_sha256="pass"),"FETCH_OR_VALIDATION_FAILED:ValueError")
    def test_no_secret_in_error(self):
        c=fixture();c["sources"][0]["url"]="https://alpha.example.org/secret-token"
        def fail(url):raise OSError("secret-token")
        self.assertNotIn("secret-token",str(assess(c,fail)))
if __name__=="__main__":unittest.main()
