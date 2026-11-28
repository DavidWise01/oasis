import base64,hashlib,json,unittest
from account_lock_audit import request,endpoint,sign,correlate,HOLD
HOST_S3="s3.us-east-1.amazonaws.com"
HOST_STS="sts.us-east-1.amazonaws.com"
NOW="20261128T103000Z"
class Response:
    def __init__(self,data,status=200,headers=None):
        self.data=data;self.status=status
        self.headers=headers or [("x-amz-request-id","request-123"),("content-type","application/xml")]
    def getheaders(self):return self.headers
    def read(self,n):return self.data[:n]
class Connection:
    response=None
    calls=[]
    def __init__(self,host,ip,timeout):
        self.host=host;self.ip=ip
    def request(self,method,path,headers):
        self.calls.append((self.host,method,path,headers))
    def getresponse(self):return self.response
    def close(self):pass
def probe(kind,data=None,response=None,resolver=None):
    service="sts" if kind=="IDENTITY" else "s3"
    Connection.calls=[]
    payload=data if data is not None else {
      "IDENTITY":b"<GetCallerIdentityResponse><GetCallerIdentityResult><Account>123456789012</Account><Arn>arn:aws:iam::123456789012:user/observer</Arn><UserId>EXAMPLEIDENTITY</UserId></GetCallerIdentityResult></GetCallerIdentityResponse>",
      "VERSIONING":b"<VersioningConfiguration><Status>Enabled</Status></VersioningConfiguration>",
      "LOCK_CONFIGURATION":b"<ObjectLockConfiguration><ObjectLockEnabled>Enabled</ObjectLockEnabled><Rule><DefaultRetention><Mode>COMPLIANCE</Mode><Days>365</Days></DefaultRetention></Rule></ObjectLockConfiguration>"
    }[kind]
    Connection.response=response or Response(payload)
    return request(service,"us-east-1",kind,None if service=="sts" else "sample-bucket",
                   "AKID","SECRET","","20261128T103000Z",
                   resolver or (lambda host:["8.8.8.8"]),Connection)
class Tests(unittest.TestCase):
    def test_sts_identity(self):
        result=probe("IDENTITY")
        self.assertEqual(result["metadata"]["account"],"123456789012")
        self.assertEqual(Connection.calls[0][0],HOST_STS)
    def test_bucket_versioning(self):
        self.assertEqual(probe("VERSIONING")["metadata"]["status"],"Enabled")
    def test_bucket_object_lock(self):
        self.assertEqual(probe("LOCK_CONFIGURATION")["metadata"]["object_lock_enabled"],"Enabled")
    def test_only_get(self):
        probe("VERSIONING")
        self.assertEqual(Connection.calls[0][1],"GET")
    def test_credentials_not_reported(self):
        result=probe("IDENTITY")
        self.assertNotIn("SECRET",json.dumps(result))
        self.assertNotIn("AKID",json.dumps(result))
        self.assertIn("authorization",Connection.calls[0][3])
    def test_sigv4_deterministic(self):
        args=("GET",HOST_STS,"/",{"Action":"GetCallerIdentity","Version":"2011-06-15"},
               "sts","us-east-1","AKID","SECRET","",NOW)
        self.assertEqual(sign(*args),sign(*args))
    def test_sts_service_scope(self):
        headers,_,_=sign("GET",HOST_STS,"/",{"Action":"GetCallerIdentity","Version":"2011-06-15"},
                         "sts","us-east-1","AKID","SECRET","",NOW)
        self.assertIn("/sts/aws4_request",headers["authorization"])
    def test_session_token(self):
        headers,_,_=sign("GET",HOST_STS,"/",{}, "sts","us-east-1",
                         "AKID","SECRET","TOKEN",NOW)
        self.assertEqual(headers["x-amz-security-token"],"TOKEN")
    def test_write_disallowed(self):
        with self.assertRaisesRegex(ValueError,"GET_ONLY"):
            sign("PUT",HOST_STS,"/",{},"sts","us-east-1","AKID","SECRET","",NOW)
    def test_unallowlisted_service(self):
        with self.assertRaisesRegex(ValueError,"SERVICE_NOT_ALLOWLISTED"):
            endpoint("ec2","us-east-1")
    def test_bucket_name_invalid(self):
        with self.assertRaisesRegex(ValueError,"BUCKET_INVALID"):
            endpoint("s3","us-east-1","INVALID_BUCKET")
    def test_private_dns_rejected(self):
        with self.assertRaisesRegex(ValueError,"DNS_UNSAFE_OR_EMPTY"):
            probe("IDENTITY",resolver=lambda host:["127.0.0.1"])
    def test_missing_credentials(self):
        with self.assertRaisesRegex(ValueError,"CREDENTIALS_REQUIRED"):
            request("sts","us-east-1","IDENTITY",None,"","secret","",NOW,
                    lambda host:["8.8.8.8"],Connection)
    def test_provider_denial(self):
        with self.assertRaisesRegex(ValueError,"AWS_RESPONSE_STATUS_REJECTED"):
            probe("IDENTITY",response=Response(b"",403))
    def test_disabled_versioning(self):
        with self.assertRaisesRegex(ValueError,"VERSIONING_NOT_ENABLED"):
            probe("VERSIONING",data=b"<VersioningConfiguration><Status>Suspended</Status></VersioningConfiguration>")
    def test_missing_object_lock(self):
        with self.assertRaisesRegex(ValueError,"OBJECT_LOCK_NOT_ENABLED"):
            probe("LOCK_CONFIGURATION",data=b"<ObjectLockConfiguration/>")
    def test_sts_missing_account(self):
        with self.assertRaisesRegex(ValueError,"STS_IDENTITY_RESPONSE_INVALID"):
            probe("IDENTITY",data=b"<GetCallerIdentityResponse/>")
    def test_duplicate_headers(self):
        response=Response(b"<VersioningConfiguration><Status>Enabled</Status></VersioningConfiguration>",
                          headers=[("Date","one"),("date","two")])
        with self.assertRaisesRegex(ValueError,"DUPLICATE_OR_EXCESS_HEADERS"):
            probe("VERSIONING",response=response)
    def test_raw_response_preserved(self):
        result=probe("LOCK_CONFIGURATION")
        self.assertTrue(base64.b64decode(result["raw_body_b64"]).startswith(b"<ObjectLockConfiguration>"))
    def test_provider_identity_still_hold(self):
        result=probe("IDENTITY")
        self.assertFalse(result["storage_account_identity_independently_verified"])
    def bundle(self):
        service="s3.us-east-1.amazonaws.com"
        return {
          "identity":{"operation":"IDENTITY","metadata":{"account":"123456789012"}},
          "versioning":{"operation":"VERSIONING","service_host":service,"metadata":{"status":"Enabled"}},
          "lock":{"operation":"LOCK_CONFIGURATION","service_host":service,"metadata":{"object_lock_enabled":"Enabled"}},
          "head":{"operation":"HEAD","url_host":service,"object_version":"v1","metadata":{"lock_mode":"COMPLIANCE","retain_until":"2030-01-01"}},
          "retention":{"operation":"RETENTION","url_host":service,"object_version":"v1","metadata":{"lock_mode":"COMPLIANCE","retain_until":"2030-01-01"}}
        }
    def check(self,bundle):
        return correlate(*(bundle[k] for k in ("identity","versioning","lock","head","retention")),"123456789012","v1")
    def test_full_consistency_still_hold(self):
        result=self.check(self.bundle())
        self.assertTrue(result["metadata_consistent"])
        self.assertFalse(result["external_custody_verified"])
    def test_account_mismatch(self):
        b=self.bundle();b["identity"]["metadata"]["account"]="111111111111"
        self.assertIn("ACCOUNT_PIN_CONFLICT",self.check(b)["reasons"])
    def test_version_mismatch(self):
        b=self.bundle();b["head"]["object_version"]="v2"
        self.assertIn("VERSION_PIN_CONFLICT",self.check(b)["reasons"])
    def test_lock_policy_mismatch(self):
        b=self.bundle();b["retention"]["metadata"]["lock_mode"]="GOVERNANCE"
        self.assertIn("VERSION_RETENTION_MODE_CONFLICT",self.check(b)["reasons"])
    def test_retention_date_mismatch(self):
        b=self.bundle();b["retention"]["metadata"]["retain_until"]="2029-01-01"
        self.assertIn("VERSION_RETENTION_DATE_CONFLICT",self.check(b)["reasons"])
    def test_region_host_substitution(self):
        b=self.bundle();b["lock"]["service_host"]="s3.eu-west-1.amazonaws.com"
        self.assertIn("PROVIDER_REGION_HOST_CONFLICT",self.check(b)["reasons"])
if __name__=="__main__":unittest.main()
