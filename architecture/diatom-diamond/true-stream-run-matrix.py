import subprocess,json,datetime,sys,os
from pathlib import Path
out=Path(__file__).parent
exe=out/'true-stream-benchmark.mjs'
cases=[
 ('warmup',2048,0,'none'),
 ('steady_20k',20000,0,'none'),
 ('sustained_100k',100000,0,'none'),
 ('slow_sink_20k',20000,5,'none'),
 ('hash_none_20k',20000,0,'none'),
 ('hash_sha256_20k',20000,0,'sha256'),
 ('hash_sha256d_20k',20000,0,'sha256d'),
 ('hash_tagged_20k',20000,0,'tagged'),
 ('hash_none_repeat_20k',20000,0,'none'),
]
allowed=os.getenv('ONLY_CASES','').split(',') if os.getenv('ONLY_CASES') else None
existing=out/'true-stream-results.json'
rows=json.loads(existing.read_text()).get('cases',[]) if existing.exists() else []
for name,n,delay,mode in cases:
 if allowed and name not in allowed: continue
 if any(r['label']==name for r in rows): continue
 print('BEGIN',name,n,delay,mode,flush=True)
 p=subprocess.run(['node',str(exe),f'--tokens={n}',f'--delay={delay}',f'--mode={mode}'],capture_output=True,text=True,timeout=110)
 if p.returncode:print(p.stderr,flush=True);raise RuntimeError(name+' failed')
 row=json.loads(p.stdout);row['label']=name;rows.append(row)
 r=row['case']; print('END',name,'tok/s',round(r['throughputTokensPerSecond']),'sec',round(r['elapsedMs']/1000,2),'maxLead',r['maxGeneratedAheadTokens'],'pause',r['readablePauseEvents'],'heapgrowthMiB',round(r['sampledHeapGrowthBytes']/1048576,2),flush=True)
 existing.write_text(json.dumps({'dateUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'purpose':'bounded true streaming, NOT neural inference','cases':rows},indent=2)+'\n')
print('DONE',len(rows),flush=True)
