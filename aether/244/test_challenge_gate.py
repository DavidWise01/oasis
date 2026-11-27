import base64,unittest
from challenge_gate import assess
def fixture():
    graph={f"key-controller-{i}":[f"owner-{i}"] for i in range(3)}
    graph.update({f"owner-{i}":[] for i in range(3)})
    receipts=[];keys={}
    for i,host in enumerate(("alpha.example.org","beta.example.org","gamma.example.org")):
        s={"schema":"AETHER-244/signed-challenge-v1","source_sha256":"a"*64,"run_head":"b"*40,
           "run_id":55,"challenge_id":"challenge-55","nonce":f"nonce-{i}",
           "controller_id":f"key-controller-{i}","source_url":f"https://{host}/evidence",
           "receipt_id":f"receipt-{i}"}
        receipts.append({"statement":s,"key_id":f"key-{i}",
                         "signature_b64":base64.b64encode(b"x"*64).decode()})
        keys[f"key-{i}"]={"controller_id":f"key-controller-{i}","public_key_pem":"mock-key"}
    return {"receipts":receipts,"controller_graph":graph,"externally_pinned_public_keys":keys,
            "previous_nonces":[],"declared_network_policy":{
            "external_egress_only":True,"block_private_ranges":True,
            "redirects_disabled":True,"dns_pinning":True},
            "allowed_hosts":["alpha.example.org","beta.example.org","gamma.example.org"],
            "challenge":{"challenge_id":"challenge-55","run_id":55,"run_head":"b"*40}}
def mock(*args):return True
class Tests(unittest.TestCase):
    def expect(self,change,reason):
        b=fixture();change(b);r=assess(b,mock)
        self.assertIn(reason,r["reasons"],r)
        self.assertEqual(r["operational_authority"],"HOLD")
        self.assertFalse(r["physical_act_allowed"])
    def test_well_formed_hold(self):self.expect(lambda b:None,"EXTERNAL_CONTROLLER_CUSTODY_NOT_AUTHENTICATED")
    def test_isolation_unmeasured(self):self.expect(lambda b:None,"NETWORK_ISOLATION_NOT_MEASURED")
    def test_challenge_unattested(self):self.expect(lambda b:None,"CHALLENGE_ISSUANCE_AND_NONCE_LEDGER_NOT_INDEPENDENTLY_ATTESTED")
    def test_duplicate_nonce(self):self.expect(lambda b:b["receipts"][1]["statement"].update(nonce="nonce-0"),"NONCE_REPLAY_OR_INVALID")
    def test_consumed_nonce(self):self.expect(lambda b:b["previous_nonces"].append("nonce-0"),"NONCE_REPLAY_OR_INVALID")
    def test_shared_ancestry(self):self.expect(lambda b:b["controller_graph"]["key-controller-1"].append("owner-0"),"SHARED_CONTROLLER_ANCESTRY")
    def test_cycle(self):self.expect(lambda b:b["controller_graph"]["owner-0"].append("key-controller-0"),"ANCESTRY_CYCLE")
    def test_missing_parent(self):self.expect(lambda b:b["controller_graph"].pop("owner-0"),"ANCESTRY_MISSING_NODE")
    def test_wrong_challenge(self):self.expect(lambda b:b["receipts"][0]["statement"].update(challenge_id="other"),"CHALLENGE_RUN_BINDING_MISMATCH")
    def test_wrong_run(self):self.expect(lambda b:b["receipts"][0]["statement"].update(run_id=77),"CHALLENGE_RUN_BINDING_MISMATCH")
    def test_source_mismatch(self):self.expect(lambda b:b["receipts"][0]["statement"].update(source_sha256="f"*64),"CROSS_RECEIPT_BINDING_MISMATCH")
    def test_signature_reject(self):self.assertIn("SIGNATURE_INVALID",assess(fixture(),lambda *args:False)["reasons"])
    def test_missing_key(self):self.expect(lambda b:b["externally_pinned_public_keys"].pop("key-1"),"EXTERNAL_KEY_PIN_UNAVAILABLE")
    def test_redirect_policy(self):self.expect(lambda b:b["declared_network_policy"].update(redirects_disabled=False),"NETWORK_POLICY:ISOLATION_POLICY_UNPROVEN")
    def test_http(self):self.expect(lambda b:b["receipts"][0]["statement"].update(source_url="http://alpha.example.org/a"),"NETWORK_POLICY:URL_SCHEME_AUTH_OR_PORT")
    def test_internal_ip(self):
        def change(b):
            b["allowed_hosts"].append("127.0.0.1");b["receipts"][0]["statement"]["source_url"]="https://127.0.0.1/a"
        self.expect(change,"NETWORK_POLICY:NONPUBLIC_LITERAL_IP")
    def test_unknown_host(self):self.expect(lambda b:b["receipts"][0]["statement"].update(source_url="https://evil.example.org/a"),"NETWORK_POLICY:HOST_NOT_PINNED")
    def test_missing_receipt(self):self.expect(lambda b:b["receipts"].pop(),"EXACTLY_THREE_RECEIPTS_REQUIRED")
    def test_invalid_bundle(self):self.assertIn("INVALID_BUNDLE",assess(None,mock)["reasons"])
    def test_boolean_run_id(self):self.expect(lambda b:b["receipts"][0]["statement"].update(run_id=True),"RUN_ID_INVALID")
if __name__=="__main__":unittest.main()
