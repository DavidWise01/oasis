import base64,json,sqlite3,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"303"))
from test_identity_rotation_time import fixture
from controller_readback import capture,audit,validate,canon,sha,digest

class ReadbackTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        self.db=Path(tmp.name)/"aether304.sqlite"
        self.bundle,self.roots,self.roots_pin,_=fixture()
        self.endpoints={
            "registry_old":"https://registry.example.org/registry/epoch-1",
            "registry_new":"https://registry.example.org/registry/epoch-2",
            "clock_first":"https://clock.example.net/time/window-1",
            "clock_second":"https://clock.example.net/time/window-2"}
        self.plan={"schema":"AETHER-304/readback-plan-v1",
                   "bundle_sha256":sha(self.bundle),"roots_sha256":self.roots_pin,
                   "endpoints":self.endpoints.copy()}
        self.pin=sha(self.plan)
        self.responses={
            self.endpoints["registry_old"]:canon(self.bundle["old_registry"]),
            self.endpoints["registry_new"]:canon(self.bundle["new_registry"]),
            self.endpoints["clock_first"]:canon(self.bundle["time_windows"][0]),
            self.endpoints["clock_second"]:canon(self.bundle["time_windows"][1])}
    def collector(self,url,allowed):
        raw=self.responses[url]
        self.assertIn(url.split("/")[2],allowed)
        fields={"schema":"AETHER-264/https-acquisition-v1",
                "requested_url":url,"host":url.split("/")[2],
                "pinned_ip":"8.8.8.8","dns_address_count":1,
                "tls_hostname_validation":True,"status":200,"elapsed_ms":1,
                "raw_length":len(raw),"raw_sha256":digest(raw),
                "raw_b64":base64.b64encode(raw).decode()}
        return {**fields,"observation_sha256":sha(fields)}
    def first(self):
        return capture(self.db,self.plan,self.pin,self.bundle,self.roots,self.roots_pin,
                       "first-capture-nonce-304",self.collector)
    def second(self):
        return capture(self.db,self.plan,self.pin,self.bundle,self.roots,self.roots_pin,
                       "second-capture-nonce-304",self.collector)
    def report(self,seq=None,head=None):
        return audit(self.db,self.plan,self.pin,self.bundle,self.roots,self.roots_pin,seq,head)
    def test_exact_preimage_first_window(self):
        v=self.first()
        self.assertEqual(v["raw_observations"],4)
        self.assertTrue(v["frozen_signatures_and_exact_preimages_matched"])
    def test_two_windows_recovery(self):
        self.first();self.second()
        report=self.report()
        self.assertEqual(report["windows"],2)
        self.assertNotIn("RETAINED_OBSERVATION_INVALID",report["reasons"])
    def test_no_independence_promotion(self):
        self.first()
        self.assertFalse(self.report()["independent_clock_control_verified"])
        self.assertFalse(self.report()["physical_act_allowed"])
    def test_nonce_replay_rejected(self):
        self.first()
        with self.assertRaisesRegex(ValueError,"WINDOW_NONCE_REPLAY"):self.first()
    def test_third_window_rejected(self):
        self.first();self.second()
        with self.assertRaisesRegex(ValueError,"TWO_WINDOWS_ONLY"):
            capture(self.db,self.plan,self.pin,self.bundle,self.roots,self.roots_pin,
                    "third-capture-nonce-304",self.collector)
    def test_plan_pin_tamper(self):
        with self.assertRaisesRegex(ValueError,"PLAN_PIN_OR_SCHEMA_INVALID"):
            capture(self.db,self.plan,"f"*64,self.bundle,self.roots,self.roots_pin,
                    "first-capture-nonce-304",self.collector)
    def test_bundle_pin_tamper(self):
        self.bundle["receipt_head_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"BUNDLE_OR_ROOT_PIN_CONFLICT"):self.first()
    def test_key_root_pin_tamper(self):
        with self.assertRaisesRegex(ValueError,"BUNDLE_OR_ROOT_PIN_CONFLICT"):
            capture(self.db,self.plan,self.pin,self.bundle,self.roots,"f"*64,
                    "first-capture-nonce-304",self.collector)
    def test_mirrored_registry_and_clock_host_rejected(self):
        self.plan["endpoints"]["clock_first"]="https://registry.example.org/clock/first"
        self.plan["endpoints"]["clock_second"]="https://registry.example.org/clock/second"
        self.pin=sha(self.plan)
        with self.assertRaisesRegex(ValueError,"REGISTRY_CLOCK_HOST_ANCESTRY_RISK"):self.first()
    def test_duplicate_endpoint_url_rejected(self):
        self.plan["endpoints"]["registry_new"]=self.plan["endpoints"]["registry_old"]
        self.pin=sha(self.plan)
        with self.assertRaisesRegex(ValueError,"DUPLICATE_ENDPOINT_URL"):self.first()
    def test_registry_body_changed(self):
        self.responses[self.endpoints["registry_new"]]=b'{"modified":true}'
        with self.assertRaisesRegex(ValueError,"REMOTE_PREIMAGE_DIVERGENCE"):self.first()
    def test_clock_body_changed(self):
        self.responses[self.endpoints["clock_second"]]=b'{"modified":true}'
        with self.assertRaisesRegex(ValueError,"REMOTE_PREIMAGE_DIVERGENCE"):self.first()
    def test_corrupt_source_signature_disallows_acquisition(self):
        self.bundle["old_registry"]["signature_b64"]="AAAA"
        self.plan["bundle_sha256"]=sha(self.bundle)
        self.pin=sha(self.plan)
        with self.assertRaisesRegex(ValueError,"FROZEN_303_QUALIFICATION_FAILED"):self.first()
    def test_atomic_failed_readback(self):
        self.responses[self.endpoints["clock_second"]]=b'changed'
        with self.assertRaises(ValueError):self.first()
        self.assertEqual(self.report()["windows"],0)
    def test_history_head_tamper_detected(self):
        self.first()
        with sqlite3.connect(self.db) as db:db.execute("UPDATE readback SET head=?",("f"*64,))
        self.assertIn("MANIFEST_PREIMAGE_OR_HEAD_INVALID",self.report()["reasons"])
    def test_history_removed_against_prefix(self):
        first=self.first()
        with sqlite3.connect(self.db) as db:db.execute("DELETE FROM readback")
        self.assertIn("HISTORICAL_WINDOW_REMOVED",
                      self.report(1,first["head_sha256"])["reasons"])
    def test_wrong_external_checkpoint(self):
        self.first()
        self.assertIn("HISTORICAL_WINDOW_REWRITTEN",self.report(1,"f"*64)["reasons"])
    def test_second_window_config_changed(self):
        self.first()
        self.plan["endpoints"]["clock_second"]="https://clock.example.net/new-window-2"
        self.pin=sha(self.plan)
        with self.assertRaisesRegex(ValueError,"BUNDLE_OR_ROOT_PIN_CONFLICT|PLAN_CHANGED_BETWEEN_WINDOWS"):
            self.second()
    def test_clock_claim_not_authenticated_time(self):
        self.first();self.second()
        self.assertIn("CLOCK_OWNER_AND_ELAPSED_TIME_UNVERIFIED",self.report()["reasons"])
    def test_read_only_audit(self):
        self.first()
        before=self.db.read_bytes()
        self.report()
        self.assertEqual(before,self.db.read_bytes())
if __name__=="__main__":unittest.main()
