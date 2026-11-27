import copy,unittest
from isolation import DENIALS,assess
def fixture():
    return {"allowed_hosts":["evidence.example.org"],
      "acquirer_environment":{"credential_free":True,"read_only_filesystem":True,"isolated_network_namespace":True},
      "denial_trials":[{"category":x,"blocked":True,"observer":"external-claim"} for x in sorted(DENIALS)],
      "acquisitions":[{"url":"https://evidence.example.org/object","bytes":100,"sha256":"a"*64}]}
class Tests(unittest.TestCase):
    def expect(self,change,reason):
        b=fixture();change(b);r=assess(b)
        self.assertIn(reason,r["reasons"],r);self.assertEqual(r["operational_authority"],"HOLD")
    def test_claims_not_proof(self):self.expect(lambda x:None,"NETWORK_TELEMETRY_NOT_INDEPENDENTLY_ATTESTED")
    def test_dns_not_measured(self):self.expect(lambda x:None,"DNS_PINNING_AND_EGRESS_ENFORCEMENT_NOT_MEASURED_BY_THIS_TOOL")
    def test_custody_unverified(self):self.expect(lambda x:None,"EXTERNAL_CUSTODY_NOT_AUTHENTICATED")
    def test_token(self):self.expect(lambda x:x["acquirer_environment"].update(GITHUB_TOKEN="secret"),"CREDENTIAL_EXPOSURE")
    def test_secret_key(self):self.expect(lambda x:x["acquirer_environment"].update(APP_SECRET="secret"),"CREDENTIAL_EXPOSURE")
    def test_no_credential_free(self):self.expect(lambda x:x["acquirer_environment"].update(credential_free=False),"CREDENTIAL_FREE_NOT_CONFIRMED")
    def test_no_namespace(self):self.expect(lambda x:x["acquirer_environment"].update(isolated_network_namespace=False),"NETWORK_NAMESPACE_NOT_CONFIRMED")
    def test_no_readonly(self):self.expect(lambda x:x["acquirer_environment"].update(read_only_filesystem=False),"READ_ONLY_FILESYSTEM_NOT_CONFIRMED")
    def test_failed_denial(self):self.expect(lambda x:x["denial_trials"][0].update(blocked=False),"EGRESS_DENIAL_NOT_OBSERVED")
    def test_missing_denial(self):self.expect(lambda x:x["denial_trials"].pop(),"REQUIRED_DENIAL_TRIALS_MISSING")
    def test_duplicate_denial(self):self.expect(lambda x:x["denial_trials"].append(copy.deepcopy(x["denial_trials"][0])),"DENIAL_CATEGORY_DUPLICATE_OR_INVALID")
    def test_http(self):self.expect(lambda x:x["acquisitions"][0].update(url="http://evidence.example.org"),"ACQUISITION_INVALID:URL_NOT_CREDENTIAL_FREE_HTTPS")
    def test_unpinned(self):self.expect(lambda x:x["acquisitions"][0].update(url="https://other.example.org"),"ACQUISITION_INVALID:HOST_OR_PORT_NOT_PINNED")
    def test_localhost(self):
        def change(x):x["allowed_hosts"].append("127.0.0.1");x["acquisitions"][0]["url"]="https://127.0.0.1/a"
        self.expect(change,"ACQUISITION_INVALID:NONPUBLIC_LITERAL_IP")
    def test_bad_digest(self):self.expect(lambda x:x["acquisitions"][0].update(sha256="bad"),"ACQUISITION_INVALID:ACQUISITION_DIGEST_INVALID")
    def test_oversize(self):self.expect(lambda x:x["acquisitions"][0].update(bytes=2000000),"ACQUISITION_INVALID:ACQUISITION_LENGTH_INVALID")
    def test_empty(self):self.expect(lambda x:x.update(acquisitions=[]),"ACQUISITION_SET_INVALID")
    def test_invalid(self):self.assertIn("BUNDLE_INVALID",assess(None)["reasons"])
    def test_secret_not_leaked(self):
        b=fixture();b["acquirer_environment"]["GITHUB_TOKEN"]="private-test-value"
        self.assertNotIn("private-test-value",str(assess(b)))
if __name__=="__main__":unittest.main()
