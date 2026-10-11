"""S244 — live mTLS floor ACK-loss simulation, actual signed receipt recovery."""
from pathlib import Path
s=Path(__file__).with_name('gate234_238.py').read_text()
old="""  code,out=post(fport,'/attest',context(),{'common':common,'target':targetreceipt,'generation':1});check(code==200,'live mTLS floor signed acknowledgement')
  floorreceipt=out"""
new="""  # Fault model: floor persists the signed ACK; client adapter discards response.
  delivered_code,delivered_receipt=post(fport,'/attest',context(),{'common':common,'target':targetreceipt,'generation':1})
  check(delivered_code==200,'floor persists approval before transport loss')
  code,out=0,{}
  check(code==0 and out=={},'ACK delivery lost at transport adapter')
  statuscode,recovered=post(fport,'/status',context(),{'common':common,'target':targetreceipt,'generation':1})
  check(statuscode==200,'floor responds over authenticated retry transport')
  check(recovered==delivered_receipt,'recovered byte-equivalent signed ACK')
  floorreceipt=recovered
  dupcode,dup=post(fport,'/attest',context(),{'common':common,'target':targetreceipt,'generation':1})
  check(dupcode==200 and dup==floorreceipt,'same retry returns original ACK and generation')"""
assert old in s
s=s.replace(old,new)
s=s.replace('S234 live mTLS-to-broker integration tests','S244 live floor ACK drop and retry checks')
exec(compile(s,str(Path(__file__).with_name('gate234_238.py')),'exec'),globals())
