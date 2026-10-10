"""S218 independent execution strictly from trusted ledger."""
from execution217 import verify_execution
def verify_bound(wal,common,ledger):
 record=ledger.get(common['resource'],common['nonce'])
 return verify_execution(wal,common,record['op'],record['input'])
