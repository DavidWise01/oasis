"""S243: overlap target/floor/broker SIGKILL before signed recovery, then restart."""
from pathlib import Path
base=Path(__file__).with_name('gate242.py').read_text()
base=base.replace(
 "  fserver.kill();tserver.kill();fserver.join(5);tserver.join(5)",
 """  fserver.kill();tserver.kill();broker.kill();fserver.join(5);tserver.join(5);broker.wait(timeout=5)
  check(broker.returncode is not None,'broker SIGKILL overlaps both authority outages')""")
base=base.replace(
 "  fserver=mp.get_context('fork').Process(target=serve_process,args=('floor',fport",
 """  check(not rpc(sock,{'op':'status','resource':'root'},repairuid).get('ok'),'no broker response during triple outage')
  sock.unlink()
  broker=subprocess.Popen(['setpriv','--reuid=1','--regid=1','--clear-groups',sys.executable,str(pathlib.Path(__file__).parent/'server234.py'),'--config',str(config)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  check(broker.stdout.readline().strip()=='READY','broker restarted before receipt delivery')
  fserver=mp.get_context('fork').Process(target=serve_process,args=('floor',fport""")
base=base.replace('S242 overlapping authority failures and committed WAL','S243 triple-service outage and committed WAL')
exec(compile(base,str(Path(__file__).with_name('gate242.py')),'exec'),globals())
