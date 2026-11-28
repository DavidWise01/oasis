import base64,hashlib,json,unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from authenticated_provider import (fetch_s3,signed_headers,validate_target,
    clock_audit,canon,sha,digest,CLOCK_SCHEMA)

HOST="s3.us-east-1.amazonaws.com"
DATE="20261128T103000Z"
class Response:
    def __init__(self,status=200,body=b"",headers=None):
        self.status=status;self.body=body;self._headers=headers or {}
    def getheaders(self):return list(self._headers.items())
    def read(self,count):return self.body[:count]
class FakeConnection:
    calls=[]
    result=Response(headers={"x-amz-version-id":"version1",
                             "x-amz-object-lock-mode":"COMPLIANCE",
                             "x-amz-object-lock-retain-until-date":"2030-01-01"})
    def __init__(self,host,ip,timeout):
        self.host=host;self.ip=ip;self.timeout=timeout
    def request(self,method,url,headers):
        self.calls.append((method,url,headers))
    def getresponse(self):return self.result
    def close(self):pass

def read(kind="HEAD",result=None):
    FakeConnection.calls=[]
    FakeConnection.result=result or Response(headers={"x-amz-version-id":"version1"})
    return fetch_s3(HOST,"bucket/object.txt","version1","us-east-1",kind,
                    "TESTACCESS","TESTSECRET","","20261128T103000Z",
                    resolver=lambda h:["8.8.8.8"],factory=FakeConnection)
class Tests(unittest.TestCase):
    def test_signed_head_is_read_only(self):
        result=read()
        self.assertEqual(result["metadata"]["version_id"],"version1")
        self.assertEqual(FakeConnection.calls[0][0],"HEAD")
        self.assertEqual(result["operational_authority"],"HOLD")
    def test_signed_retention_get(self):
        raw=b"<Retention><Mode>COMPLIANCE</Mode><RetainUntilDate>2030-01-01</RetainUntilDate></Retention>"
        result=read("RETENTION",Response(body=raw))
        self.assertEqual(result["metadata"]["lock_mode"],"COMPLIANCE")
        self.assertEqual(FakeConnection.calls[0][0],"GET")
    def test_authorization_not_exported(self):
        result=read()
        self.assertNotIn("authorization",json.dumps(result).lower())
        self.assertIn("authorization",FakeConnection.calls[0][2])
    def test_session_token_in_signing(self):
        headers,query,_=signed_headers("HEAD",HOST,"/bucket/key",{"versionId":"v1"},
              "us-east-1","ACCESS","SECRET","temporary","20261128T103000Z")
        self.assertEqual(headers["x-amz-security-token"],"temporary")
        self.assertIn("x-amz-security-token",headers["authorization"])
    def test_signature_deterministic(self):
        args=("GET",HOST,"/bucket/key",{"retention":"","versionId":"v1"},
              "us-east-1","ACCESS","SECRET",None,DATE)
        self.assertEqual(signed_headers(*args),signed_headers(*args))
    def test_get_query_sorted(self):
        headers,q,_=signed_headers("GET",HOST,"/bucket/key",
                 {"versionId":"v1","retention":""},"us-east-1","a","b","",DATE)
        self.assertEqual(q,"retention=&versionId=v1")
    def test_write_method_rejected(self):
        with self.assertRaisesRegex(ValueError,"READ_ONLY_METHOD_REQUIRED"):
            signed_headers("PUT",HOST,"/bucket/k",{},"us-east-1","a","b","",DATE)
    def test_other_cloud_host_rejected(self):
        with self.assertRaisesRegex(ValueError,"AWS_SERVICE_HOST_NOT_PINNED"):
            validate_target("hostile.example.org","bucket/k","v1","us-east-1","HEAD")
    def test_invalid_empty_version(self):
        with self.assertRaisesRegex(ValueError,"VERSION_REQUIRED"):
            validate_target(HOST,"bucket/k","","us-east-1","HEAD")
    def test_private_dns_rejected(self):
        with self.assertRaisesRegex(ValueError,"DNS_NOT_PUBLIC"):
            fetch_s3(HOST,"bucket/key","version1","us-east-1","HEAD",
                 "a","b","","20261128T103000Z",
                 resolver=lambda h:["127.0.0.1"],factory=FakeConnection)
    def test_version_mismatch(self):
        with self.assertRaisesRegex(ValueError,"VERSION_ID_DIVERGENCE"):
            read(result=Response(headers={"x-amz-version-id":"wrong"}))
    def test_provider_error_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"AWS_STATUS_NOT_OK"):
            read(result=Response(status=403))
    def test_retention_missing_policy_rejected(self):
        with self.assertRaisesRegex(ValueError,"RETENTION_NOT_ESTABLISHED"):
            read("RETENTION",Response(body=b"<Retention><Mode>GOVERNANCE</Mode></Retention>"))
    def test_credentials_missing(self):
        with self.assertRaisesRegex(ValueError,"CREDENTIAL_FIELDS_MISSING"):
            signed_headers("GET",HOST,"/bucket/key",{},"us-east-1","","secret","",DATE)

class ClockTests(unittest.TestCase):
    def setUp(self):
        key=Ed25519PrivateKey.generate()
        self.pem=key.public_key().public_bytes(serialization.Encoding.PEM,
                  serialization.PublicFormat.SubjectPublicKeyInfo).decode()
        self.pin=digest(self.pem.encode())
        self.heads=["a"*64,"b"*64]
        claims=[];prev="0"*64
        for i in (1,2):
            doc={"schema":CLOCK_SCHEMA,"window_seq":i,
                 "window_head_sha256":self.heads[i-1],
                 "previous_attestation_sha256":prev,
                 "unix_ms_claim":1800000000000+i*60000,"nonce":f"clock{i}"}
            doc["signature_b64"]=base64.b64encode(key.sign(canon(doc))).decode()
            claims.append(doc);prev=sha(doc)
        self.claims=claims
    def check(self):
        return clock_audit(self.claims,self.pem,self.pin,self.heads)
    def test_valid_signatures_still_hold(self):
        result=self.check()
        self.assertEqual(result["claimed_delta_ms"],60000)
        self.assertFalse(result["trusted_clock_independent"])
    def test_wrong_root_pin(self):
        self.pin="f"*64
        self.assertIn("PINNED_CLOCK_KEY_REQUIRED",self.check()["reasons"])
    def test_modified_clock_signature(self):
        self.claims[1]["signature_b64"]="AAAA"
        self.assertIn("CLOCK_SIGNATURE_INVALID",self.check()["reasons"])
    def test_changed_first_clock_breaks_chain(self):
        self.claims[0]["nonce"]="changed"
        self.assertIn("CLOCK_CHAIN_BROKEN",self.check()["reasons"])
    def test_stale_clock_replay(self):
        self.claims[1]["nonce"]="clock1"
        self.assertIn("CLOCK_NONCE_REPLAY",self.check()["reasons"])
    def test_reverse_clock(self):
        self.claims[1]["unix_ms_claim"]=1
        self.assertIn("CLOCK_TIME_NONMONOTONIC",self.check()["reasons"])
    def test_wrong_window_head(self):
        self.claims[0]["window_head_sha256"]="f"*64
        self.assertIn("CLOCK_WINDOW_MISMATCH",self.check()["reasons"])
    def test_no_act(self):
        self.assertFalse(self.check()["physical_act_allowed"])
if __name__=="__main__":unittest.main()
