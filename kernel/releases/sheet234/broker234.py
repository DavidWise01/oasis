"""S234: verify original full mTLS target/floor receipts, preserving signatures."""
from broker230 import BoundBroker
from broker227 import Denied
from broker228 import canon
from cryptography.exceptions import InvalidSignature

class LiveReceiptBroker(BoundBroker):
    def _verify_sig(self,record,pub,kind,fields):
        if not isinstance(record,dict) or set(record)!={'body','signature'}:raise Denied('SIGNED_FIELDS')
        body=record['body']
        if not isinstance(body,dict) or set(body)!=(set(fields)|{'kind','epoch','holder'}):raise Denied('SIGNED_FIELDS')
        if any(body.get(k)!=v for k,v in {'kind':kind,**fields}.items()):raise Denied('SIGNED_FIELDS')
        d=self.connect()
        try:owner=d.execute('SELECT epoch,holder FROM owner WHERE resource=?',(fields['resource'],)).fetchone()
        finally:d.close()
        if owner!=(body['epoch'],body['holder']):raise Denied('SIGNED_OWNER')
        try:pub.verify(bytes.fromhex(record['signature']),canon(body))
        except (InvalidSignature,ValueError,TypeError,KeyError):raise Denied('INVALID_SIGNATURE')
