"""S230: deny unverified writer bindings; bind authorization serialized in SQLite."""
from broker228 import VerifiedBroker,Denied
class BoundBroker(VerifiedBroker):
    def run(self,uid,q):
        if not isinstance(q,dict) or q.get('op')!='bind':
            return super().run(uid,q)
        if self.uid_roles.get(uid)!='writer':raise Denied('ROLE')
        if set(q)!={'op','resource','epoch','holder','previous_head','previous_seq','head','seq','nonce'}:raise Denied('FIELDS')
        resource=q['resource']
        if not isinstance(resource,str) or not resource or len(resource)>64 or not isinstance(q['nonce'],str) or not q['nonce']:raise Denied('IDENTITY')
        for k in ('epoch','seq','previous_seq'):
            if type(q[k]) is not int:raise Denied('TYPE')
        d=self.connect()
        try:
            d.execute('BEGIN IMMEDIATE')
            owner=d.execute('SELECT epoch,holder FROM owner WHERE resource=?',(resource,)).fetchone()
            bound=d.execute('SELECT head,seq FROM bound WHERE resource=?',(resource,)).fetchone()
            if owner!=(q['epoch'],q['holder']):raise Denied('STALE_OWNER')
            if bound!=(q['previous_head'],q['previous_seq']):raise Denied('STALE_BINDING')
            self._wal(q['head'],q['seq'],q['previous_head'],q['previous_seq'],q['nonce'])
            d.execute('UPDATE bound SET head=?,seq=? WHERE resource=? AND head=? AND seq=?',(q['head'],q['seq'],resource,q['previous_head'],q['previous_seq']))
            if d.execute('SELECT changes()').fetchone()[0]!=1:raise Denied('RACE')
            d.execute('INSERT INTO events(resource,actor,kind,head,generation) VALUES(?,?,?,?,?)',(resource,'writer','bind',q['head'],None))
            d.execute('COMMIT')
            return {'ok':True,'head':q['head'],'seq':q['seq']}
        except BaseException:
            if d.in_transaction:d.execute('ROLLBACK')
            raise
        finally:d.close()
