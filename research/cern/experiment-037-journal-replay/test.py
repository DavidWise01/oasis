import json
from pathlib import Path
def simulate(crash_at, receiver_durable=True):
 ids=[f'{i//3}:{i%3}' for i in range(60)]
 journal=[];seen=set();delivered=[];attempts=0
 for ident in ids:
  journal.extend([('ACCEPT',ident),('EGRESS_INTENT',ident)])
  if ident==crash_at[0] and crash_at[1]=='intent':break
  attempts+=1
  if not receiver_durable or ident not in seen:delivered.append(ident)
  seen.add(ident)
  if ident==crash_at[0] and crash_at[1]=='delivery':break
  journal.append(('ACK',ident))
  if ident==crash_at[0] and crash_at[1]=='ack':break
 accepted={v for op,v in journal if op=='ACCEPT'}
 acked={v for op,v in journal if op=='ACK'}
 for ident in ids:
  if ident not in accepted:journal.extend([('ACCEPT',ident),('EGRESS_INTENT',ident)]);accepted.add(ident)
  if ident not in acked:
   attempts+=1
   if not receiver_durable or ident not in seen:delivered.append(ident)
   seen.add(ident);journal.append(('ACK',ident));acked.add(ident)
 assert len(acked)==len(accepted)==60
 return dict(unique=len(set(delivered)),duplicates=len(delivered)-len(set(delivered)),attempts=attempts)
def main():
 rows=[]
 for ident in ['0:0','7:1','19:2']:
  for stage in ['intent','delivery','ack']:
   safe=simulate((ident,stage),True);unsafe=simulate((ident,stage),False)
   assert safe['unique']==60 and safe['duplicates']==0
   rows.append(dict(id=ident,stage=stage,safe=safe,unsafe=unsafe))
 assert sum(r['unsafe']['duplicates'] for r in rows)==3
 Path(__file__).with_name('results.json').write_text(json.dumps(rows,indent=2))
 print('PASS: 9/9 restart cases; 60 logical deliveries each')
if __name__=='__main__':main()
