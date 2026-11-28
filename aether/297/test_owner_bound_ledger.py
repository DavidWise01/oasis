import base64,copy,json,sqlite3,tempfile,unittest
from pathlib import Path
from owner_bound_ledger import (snapshot,sign,targets,metadata,append,audit,
                                canon,digest,sha,validate_owner,validate_target,HOLD)
REGION="us-east-1"
OWNER="123456789012"
HOST="s3.us-east-1.amazonaws.com"
DATE="20261128T115600Z"
VERSION="version-1"
KEY="archive/payload.json"
BUCKET="witness-vault"
def xml(kind):
    values={
      "VERSIONING":b"<VersioningConfiguration><Status>Enabled</Status></VersioningConfiguration>",
      "LOCK_CONFIGURATION":b"<ObjectLockConfiguration><ObjectLockEnabled>Enabled</ObjectLockEnabled></ObjectLockConfiguration>",
      "RETENTION":b"<Retention><Mode>COMPLIANCE</Mode><RetainUntilDate>2030-01-01T00:00:00Z</RetainUntilDate></Retention>"
    }
    return values[kind]
class Fixture(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.db=Path(t.name)/"a297.sqlite"
        self.requests=[]
        self.payloads={}
        for kind,method,path,query in targets(BUCKET,KEY,VERSION):
            ordered="&".join(k+"="+v for k,v in sorted(query.items()))
            self.payloads[(method,path+"?"+ordered)]=(
                200,{"x-amz-version-id":VERSION,"x-amz-object-lock-mode":"COMPLIANCE",
                     "x-amz-object-lock-retain-until-date":"2030-01-01T00:00:00Z"},
                b"" if kind=="HEAD" else xml(kind))
    def transport(self,method,host,path,headers):
        self.assertEqual(host,HOST)
        self.requests.append((method,host,path,headers))
        return self.payloads[(method,path)]
    def snapshot(self):
        return snapshot(REGION,BUCKET,KEY,VERSION,OWNER,"TESTACCESS","TESTSECRET","",DATE,self.transport)
    def commit(self):
        return append(self.db,self.snapshot(),"unique-capture-297-a")
    def test_four_read_only_requests(self):
        self.snapshot()
        self.assertEqual([r[0] for r in self.requests],["GET","GET","HEAD","GET"])
    def test_expected_owner_in_signed_headers(self):
        self.snapshot()
        for _,_,_,headers in self.requests:
            self.assertEqual(headers["x-amz-expected-bucket-owner"],OWNER)
            self.assertIn("x-amz-expected-bucket-owner",headers["authorization"])
    def test_no_credentials_in_transcript(self):
        text=json.dumps(self.snapshot())
        self.assertNotIn("TESTSECRET",text)
        self.assertNotIn("TESTACCESS",text)
        self.assertNotIn("authorization",text.lower())
        self.assertNotIn("session-token",text.lower())
    def test_signed_owner_changes_request_hash(self):
        args=("GET",HOST,"/bucket",{"versioning":""},REGION)
        one=sign(*args,OWNER,"ACCESS","SECRET","",DATE)
        two=sign(*args,"999999999999","ACCESS","SECRET","",DATE)
        self.assertNotEqual(one[2],two[2])
    def test_owner_rejects_short(self):
        with self.assertRaisesRegex(ValueError,"EXPECTED_OWNER_12_DIGITS_REQUIRED"):
            validate_owner("123")
    def test_owner_rejects_non_ascii_numeric(self):
        with self.assertRaisesRegex(ValueError,"EXPECTED_OWNER_12_DIGITS_REQUIRED"):
            validate_owner("１２３４５６７８９０１２")
    def test_owner_rejects_float(self):
        with self.assertRaises(ValueError):validate_owner(123456789012)
    def test_http_write_forbidden(self):
        with self.assertRaisesRegex(ValueError,"READ_ONLY_METHODS_ONLY"):
            sign("PUT",HOST,"/bucket",{},REGION,OWNER,"a","b","",DATE)
    def test_invalid_bucket(self):
        with self.assertRaisesRegex(ValueError,"BUCKET_INVALID"):
            validate_target(REGION,"INVALID_BUCKET",KEY,VERSION,OWNER)
    def test_version_mandatory(self):
        with self.assertRaisesRegex(ValueError,"EXPLICIT_NON_NULL_VERSION_REQUIRED"):
            validate_target(REGION,BUCKET,KEY,"null",OWNER)
    def test_bucket_lock_missing(self):
        key=("GET","/"+BUCKET+"?object-lock=")
        self.payloads[key]=(200,{},b"<ObjectLockConfiguration/>")
        with self.assertRaisesRegex(ValueError,"BUCKET_OBJECT_LOCK_DISABLED"):self.snapshot()
    def test_suspended_versioning(self):
        key=("GET","/"+BUCKET+"?versioning=")
        self.payloads[key]=(200,{},b"<VersioningConfiguration><Status>Suspended</Status></VersioningConfiguration>")
        with self.assertRaisesRegex(ValueError,"BUCKET_VERSIONING_DISABLED"):self.snapshot()
    def test_wrong_explicit_version(self):
        path="/"+BUCKET+"/"+KEY+"?versionId="+VERSION
        self.payloads[("HEAD",path)]=(200,{"x-amz-version-id":"substituted",
                 "x-amz-object-lock-mode":"COMPLIANCE",
                 "x-amz-object-lock-retain-until-date":"2030-01-01T00:00:00Z"},b"")
        with self.assertRaisesRegex(ValueError,"VERSION_ID_CHANGED"):self.snapshot()
    def test_changed_retention_mode(self):
        path="/"+BUCKET+"/"+KEY+"?retention=&versionId="+VERSION
        self.payloads[("GET",path)]=(200,{},b"<Retention><Mode>GOVERNANCE</Mode><RetainUntilDate>2030-01-01T00:00:00Z</RetainUntilDate></Retention>")
        with self.assertRaisesRegex(ValueError,"VERSION_SPECIFIC_RETENTION_CONFLICT"):self.snapshot()
    def test_changed_retention_date(self):
        path="/"+BUCKET+"/"+KEY+"?retention=&versionId="+VERSION
        self.payloads[("GET",path)]=(200,{},b"<Retention><Mode>COMPLIANCE</Mode><RetainUntilDate>2020-01-01</RetainUntilDate></Retention>")
        with self.assertRaisesRegex(ValueError,"VERSION_SPECIFIC_RETENTION_CONFLICT"):self.snapshot()
    def test_non_200_rejected(self):
        path="/"+BUCKET+"?object-lock="
        self.payloads[("GET",path)]=(403,{},b"")
        with self.assertRaisesRegex(ValueError,"STATUS_REJECTED"):self.snapshot()
    def test_attested_transport_still_hold(self):
        entry=self.commit()
        self.assertFalse(entry["independent_external_custody_verified"])
    def test_recovery_rehash(self):
        self.commit()
        report=audit(self.db)
        self.assertEqual(report["batches"],1)
        self.assertNotIn("HISTORY_HASH_CHANGED",report["reasons"])
    def test_replayed_challenge(self):
        self.commit()
        with self.assertRaisesRegex(ValueError,"CHALLENGE_REPLAY"):self.commit()
    def test_append_only_second_batch(self):
        first=self.commit()
        second=append(self.db,self.snapshot(),"unique-capture-297-b")
        self.assertEqual(second["sequence"],2)
        self.assertNotEqual(first["head_sha256"],second["head_sha256"])
    def test_modified_record_tamper(self):
        self.commit()
        with sqlite3.connect(self.db) as d:
            d.execute("UPDATE evidence SET head=?",("f"*64,))
        self.assertIn("HISTORY_HASH_CHANGED",audit(self.db)["reasons"])
    def test_deleted_history_detected_by_pin(self):
        first=self.commit()
        with sqlite3.connect(self.db) as d:d.execute("DELETE FROM evidence")
        self.assertIn("HISTORICAL_PREFIX_REMOVED",audit(self.db,1,first["head_sha256"])["reasons"])
    def test_raw_response_tamper(self):
        self.commit()
        with sqlite3.connect(self.db) as d:
            row=d.execute("SELECT manifest FROM evidence").fetchone()[0]
            m=json.loads(row);m["evidence"]["records"][0]["response_raw_b64"]=base64.b64encode(b"changed").decode()
            d.execute("UPDATE evidence SET manifest=?",(canon(m).decode(),))
        self.assertIn("RAW_EVIDENCE_SUBSTITUTED",audit(self.db)["reasons"])
    def test_no_act(self):
        self.assertFalse(self.commit()["physical_act_allowed"])
if __name__=="__main__":unittest.main()
