import base64,hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from live_provider_capture import capture,audit,sha,canon,ZERO

def capture_observation(url,data):
    fields={"schema":"AETHER-264/https-acquisition-v1",
            "requested_url":url,"host":url.split("/")[2],
            "pinned_ip":"8.8.8.8","dns_address_count":1,
            "tls_hostname_validation":True,"status":200,"elapsed_ms":2,
            "raw_length":len(data),"raw_sha256":hashlib.sha256(data).hexdigest(),
            "raw_b64":base64.b64encode(data).decode()}
    return {**fields,"observation_sha256":sha(fields),"operational_authority":"HOLD"}

class Tests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.db=Path(temp.name)/"a294.sqlite"
        self.data={};providers={};clock={}
        self.artifact="a"*64
        heads=["1"*64,"2"*64]
        for i in range(3):
            key=f"provider{i}";host=f"p{i}.example.org"
            urls=[]
            for n in (1,2):
                url=f"https://{host}/object/version/{n}";urls.append(url)
                body={"schema":"AETHER-293/provider-object-response-v1",
                      "provider_id":key,"window_seq":n,"artifact_sha256":self.artifact,
                      "object_key":"stable-object","version_id":"v1",
                      "lock_mode":"COMPLIANCE","retention_until_claim":"2030",
                      "response_request_id":f"request{i}-{n}","response_nonce":f"nonce{i}-{n}"}
                self.data[url]=canon(body)
            providers[key]=urls
        previous=ZERO
        clock_urls=[]
        for n in (1,2):
            url=f"https://clock.example.org/attestation/{n}";clock_urls.append(url)
            body={"schema":"AETHER-293/signed-time-chain-v1",
                  "controller_id":"claimed-clock","window_seq":n,
                  "window_head_sha256":heads[n-1],
                  "previous_attestation_sha256":previous,
                  "unix_ms_claim":1800000000000+n*60000,
                  "nonce":f"clocknonce{n}","signature_b64":"unverified"}
            self.data[url]=canon(body);previous=sha(body)
        clock["clock0"]=clock_urls
        self.plan={"schema":"AETHER-294/acquisition-plan-v1","provider_urls":providers,
                   "clock_urls":clock,"artifact_sha256":self.artifact,"window_heads":heads}
        self.pin=sha(self.plan)
        self.nonce="capture-294-nonce-A"
    def collector(self,url,allowed):
        self.assertIn(url.split("/")[2],allowed)
        return capture_observation(url,self.data[url])
    def run_capture(self,collector=None,nonce=None):
        return capture(self.db,self.plan,self.pin,nonce or self.nonce,
                       collector or self.collector)
    def test_eight_raw_records_atomic(self):
        result=self.run_capture()
        self.assertEqual(result["raw_records_retained"],8)
        self.assertFalse(result["provider_identity_verified"])
    def test_readback_conservation(self):
        self.run_capture()
        result=audit(self.db)
        self.assertEqual(result["observations"],8)
        self.assertNotIn("OBSERVATION_SET_DIVERGENCE",result["reasons"])
    def test_capture_challenge_replay(self):
        self.run_capture()
        with self.assertRaisesRegex(ValueError,"CAPTURE_NONCE_REPLAY"):self.run_capture()
    def test_new_capture_nonce(self):
        self.run_capture()
        result=self.run_capture(nonce="capture-294-nonce-B")
        self.assertEqual(result["acquisition_id"],2)
    def test_plan_pin_changed(self):
        self.pin="f"*64
        with self.assertRaisesRegex(ValueError,"PLAN_PIN_MISMATCH"):self.run_capture()
    def test_http_not_allowed(self):
        self.plan["provider_urls"]["provider0"][0]="http://p0.example.org/object/version/1"
        self.pin=sha(self.plan)
        with self.assertRaises(ValueError):self.run_capture()
    def test_shared_host_blocked(self):
        self.plan["provider_urls"]["provider1"]=["https://p0.example.org/a",
                                                  "https://p0.example.org/b"]
        self.pin=sha(self.plan)
        with self.assertRaisesRegex(ValueError,"SHARED_HOST_BETWEEN_SOURCES"):self.run_capture()
    def test_url_changes_between_windows(self):
        self.plan["provider_urls"]["provider0"][1]="https://other.example.org/object/version/2"
        self.pin=sha(self.plan)
        with self.assertRaisesRegex(ValueError,"SOURCE_HOST_CHANGED"):self.run_capture()
    def test_raw_hash_tamper(self):
        def bad(url,allow):
            value=self.collector(url,allow);value["raw_sha256"]="f"*64;return value
        with self.assertRaisesRegex(ValueError,"RAW_DIGEST_OR_LENGTH_INVALID"):self.run_capture(bad)
    def test_observation_hash_tamper(self):
        def bad(url,allow):
            value=self.collector(url,allow);value["observation_sha256"]="f"*64;return value
        with self.assertRaisesRegex(ValueError,"OBSERVATION_PREIMAGE_HASH_INVALID"):self.run_capture(bad)
    def test_provider_content_substitution(self):
        url=self.plan["provider_urls"]["provider0"][0]
        val=json.loads(self.data[url]);val["artifact_sha256"]="f"*64;self.data[url]=canon(val)
        with self.assertRaisesRegex(ValueError,"PROVIDER_BODY_BINDING_INVALID"):self.run_capture()
    def test_changed_object_version(self):
        url=self.plan["provider_urls"]["provider0"][1]
        val=json.loads(self.data[url]);val["version_id"]="v2";self.data[url]=canon(val)
        with self.assertRaisesRegex(ValueError,"PROVIDER_VERSION_CHANGED"):self.run_capture()
    def test_replayed_provider_nonce(self):
        a=self.plan["provider_urls"]["provider0"][0]
        b=self.plan["provider_urls"]["provider1"][0]
        val=json.loads(self.data[b]);val["response_nonce"]=json.loads(self.data[a])["response_nonce"];self.data[b]=canon(val)
        with self.assertRaisesRegex(ValueError,"SOURCE_NONCE_DUPLICATE"):self.run_capture()
    def test_decreasing_clock_time(self):
        url=self.plan["clock_urls"]["clock0"][1]
        val=json.loads(self.data[url]);val["unix_ms_claim"]=1;self.data[url]=canon(val)
        with self.assertRaisesRegex(ValueError,"CLOCK_CLAIM_NOT_INCREASING"):self.run_capture()
    def test_invalid_clock_chain(self):
        url=self.plan["clock_urls"]["clock0"][1]
        val=json.loads(self.data[url]);val["previous_attestation_sha256"]="f"*64;self.data[url]=canon(val)
        with self.assertRaisesRegex(ValueError,"CLOCK_CLAIM_CHAIN_INVALID"):self.run_capture()
    def test_failed_collection_rolls_back(self):
        url=self.plan["provider_urls"]["provider0"][0]
        self.data[url]=b"corrupt"
        with self.assertRaises(ValueError):self.run_capture()
        self.assertEqual(audit(self.db)["acquisitions"],0)
    def test_modified_retained_head(self):
        self.run_capture()
        with sqlite3.connect(self.db) as con:
            con.execute("UPDATE acquisition SET head_sha=?",("f"*64,))
        self.assertIn("BATCH_HASH_INVALID",audit(self.db)["reasons"])
    def test_deleted_observation(self):
        self.run_capture()
        with sqlite3.connect(self.db) as con:
            con.execute("DELETE FROM source_observation WHERE id='clock:clock0:2'")
        self.assertIn("OBSERVATION_SET_DIVERGENCE",audit(self.db)["reasons"])
    def test_no_act(self):
        self.assertFalse(self.run_capture()["physical_act_allowed"])
if __name__=="__main__":unittest.main()
