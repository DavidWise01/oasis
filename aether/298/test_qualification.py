import base64,hashlib,hmac,json,sqlite3,tempfile,unittest
from pathlib import Path
from qualification import (canonical,sha,sha_bytes,ZERO,inspect_evidence,
    qualified_history,freeze_export,audit_export,qualify_sigv4)
def evidence():
    items=[]
    for op in ("VERSIONING","LOCK_CONFIGURATION","HEAD","RETENTION"):
        raw=b"" if op=="HEAD" else b"<xml>test</xml>"
        items.append({"operation":op,"method":"HEAD" if op=="HEAD" else "GET",
                      "response_status":200,"response_headers":{"x-amz-request-id":"R1"},
                      "path_sha256":"a"*64,"request_sha256":"b"*64,
                      "response_raw_b64":base64.b64encode(raw).decode(),
                      "response_raw_sha256":sha_bytes(raw),"parsed":{}})
    return {"schema":"AETHER-297/owner-bound-evidence-v1","records":items}
def reference_sigv4():
    from urllib.parse import quote
    method,host,path,region="GET","s3.us-east-1.amazonaws.com","/vault/object.txt","us-east-1"
    access,secret,owner,date="AKIDEXAMPLE","SECRETEXAMPLE","123456789012","20261128T115600Z"
    query={"versionId":"v1","retention":""}
    qs="&".join(quote(k,safe="-_.~")+"="+quote(v,safe="-_.~") for k,v in sorted(query.items()))
    headers={"host":host,"x-amz-date":date,"x-amz-content-sha256":sha_bytes(b""),
             "x-amz-expected-bucket-owner":owner}
    signed=";".join(sorted(headers))
    signed_headers="".join(k+":"+headers[k]+"\n" for k in sorted(headers))
    cr="\n".join([method,path,qs,signed_headers,signed,sha_bytes(b"")])
    scope=date[:8]+"/"+region+"/s3/aws4_request"
    to_sign="\n".join(["AWS4-HMAC-SHA256",date,scope,sha_bytes(cr.encode())])
    def mac(key,msg):return hmac.new(key,msg.encode(),hashlib.sha256).digest()
    secret_key=mac(mac(mac(mac(("AWS4"+secret).encode(),date[:8]),region),"s3"),"aws4_request")
    signature=hmac.new(secret_key,to_sign.encode(),hashlib.sha256).hexdigest()
    return {"method":method,"host":host,"path":path,"query":query,"region":region,
            "access_key":access,"secret_key":secret,"session_token":"",
            "amz_date":date,"expected_owner":owner,
            "candidate_canonical_sha256":sha_bytes(cr.encode()),"candidate_signature":signature}
class Tests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.root=Path(t.name);self.db=self.root/"evidence.sqlite"
        self.export=self.root/"export.json"
        db=sqlite3.connect(self.db)
        db.execute("CREATE TABLE evidence(id INTEGER PRIMARY KEY,challenge TEXT,previous_head TEXT,head TEXT,manifest TEXT)")
        self.evidence=evidence()
        manifest={"schema":"AETHER-297/owner-bound-evidence-v1",
                  "challenge":"capture-challenge-298","previous_head_sha256":ZERO,
                  "evidence":self.evidence}
        self.head=sha(manifest)
        db.execute("INSERT INTO evidence VALUES (?,?,?,?,?)",
                   (1,"capture-challenge-298",ZERO,self.head,canonical(manifest).decode()))
        db.commit();db.close()
    def test_sigv4_official_botocore_parity(self):
        result=qualify_sigv4(reference_sigv4())
        self.assertTrue(result["signature_equal"])
        self.assertEqual(result["operational_authority"],"HOLD")
    def test_sigv4_modified_signature(self):
        c=reference_sigv4();c["candidate_signature"]="f"*64
        with self.assertRaisesRegex(ValueError,"SIGV4_SIGNATURE_NOT_PARITY"):qualify_sigv4(c)
    def test_sigv4_modified_canonical_request(self):
        c=reference_sigv4();c["candidate_canonical_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"SIGV4_CANONICAL_REQUEST_NOT_PARITY"):qualify_sigv4(c)
    def test_sigv4_write_operation_rejected(self):
        c=reference_sigv4();c["method"]="PUT"
        with self.assertRaisesRegex(ValueError,"SIGV4_METHOD_NOT_READ_ONLY"):qualify_sigv4(c)
    def test_sigv4_invalid_owner(self):
        c=reference_sigv4();c["expected_owner"]="0123"
        with self.assertRaisesRegex(ValueError,"EXPECTED_BUCKET_OWNER_INVALID"):qualify_sigv4(c)
    def test_sigv4_missing_field(self):
        c=reference_sigv4();del c["amz_date"]
        with self.assertRaisesRegex(ValueError,"SIGV4_CASE_SCHEMA_INVALID"):qualify_sigv4(c)
    def test_qualified_history(self):
        rows,manifests=qualified_history(self.db,1,self.head)
        self.assertEqual((len(rows),len(manifests)),(1,1))
    def test_create_only_export(self):
        result=freeze_export(self.db,self.export,1,self.head)
        self.assertTrue(self.export.exists())
        self.assertEqual(result["source_head_sha256"],self.head)
    def test_readback_audit(self):
        freeze_export(self.db,self.export,1,self.head)
        self.assertEqual(audit_export(self.export,self.db)["record_count"],1)
    def test_existing_export_not_overwritten(self):
        self.export.write_bytes(b"original")
        with self.assertRaises(FileExistsError):freeze_export(self.db,self.export,1,self.head)
        self.assertEqual(self.export.read_bytes(),b"original")
    def test_rejected_wrong_historical_pin(self):
        with self.assertRaisesRegex(ValueError,"PINNED_HISTORY_REWRITTEN"):
            freeze_export(self.db,self.export,1,"f"*64)
    def test_deleted_history_rejected(self):
        with sqlite3.connect(self.db) as db:db.execute("DELETE FROM evidence")
        with self.assertRaisesRegex(ValueError,"EMPTY_EVIDENCE_JOURNAL"):qualified_history(self.db,1,self.head)
    def test_changed_local_head_detected(self):
        with sqlite3.connect(self.db) as db:db.execute("UPDATE evidence SET head=?",("f"*64,))
        with self.assertRaisesRegex(ValueError,"HISTORY_MANIFEST_HASH_INVALID"):qualified_history(self.db)
    def test_changed_local_raw_body_detected(self):
        with sqlite3.connect(self.db) as db:
            m=json.loads(db.execute("SELECT manifest FROM evidence").fetchone()[0])
            m["evidence"]["records"][0]["response_raw_b64"]="AAAA"
            db.execute("UPDATE evidence SET manifest=?,head=?",(canonical(m).decode(),sha(m)))
        with self.assertRaisesRegex(ValueError,"RAW_RESPONSE_DIGEST_MISMATCH"):qualified_history(self.db)
    def test_unsafe_response_header_rejected(self):
        self.evidence["records"][0]["response_headers"]["authorization"]="secret"
        with self.assertRaisesRegex(ValueError,"UNSAFE_HEADER_IN_TRANSCRIPT"):inspect_evidence(self.evidence)
    def test_duplicate_operation_rejected(self):
        self.evidence["records"][1]["operation"]="VERSIONING"
        with self.assertRaisesRegex(ValueError,"OPERATION_DUPLICATED"):inspect_evidence(self.evidence)
    def test_wrong_http_method_rejected(self):
        self.evidence["records"][0]["method"]="POST"
        with self.assertRaisesRegex(ValueError,"READ_ONLY_OPERATION_MISMATCH"):inspect_evidence(self.evidence)
    def test_export_edit_detected(self):
        freeze_export(self.db,self.export,1,self.head)
        m=json.loads(self.export.read_bytes());m["source_head_sha256"]="f"*64
        self.export.write_bytes(canonical(m))
        with self.assertRaisesRegex(ValueError,"EXPORTED_HEAD_MISMATCH"):audit_export(self.export)
    def test_export_authority_change_detected(self):
        freeze_export(self.db,self.export,1,self.head)
        m=json.loads(self.export.read_bytes());m["physical_act_allowed"]=True
        self.export.write_bytes(canonical(m))
        with self.assertRaisesRegex(ValueError,"AUTHORITY_GATE_CHANGED"):audit_export(self.export)
    def test_snapshot_after_source_divergence(self):
        freeze_export(self.db,self.export,1,self.head)
        with sqlite3.connect(self.db) as db:db.execute("UPDATE evidence SET head=?",("f"*64,))
        with self.assertRaisesRegex(ValueError,"HISTORY_MANIFEST_HASH_INVALID"):audit_export(self.export,self.db)
    def test_export_no_custody_promotion(self):
        freeze_export(self.db,self.export,1,self.head)
        result=audit_export(self.export,self.db)
        self.assertFalse(result["independent_external_custody_verified"])
        self.assertFalse(result["physical_act_allowed"])
if __name__=="__main__":unittest.main()
