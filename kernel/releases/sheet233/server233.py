"""S233 hardened SO_PEERCRED broker with bounded and timed local requests."""
import argparse,json,os,pathlib,socket,struct,threading
from broker230 import BoundBroker
from cryptography.hazmat.primitives import serialization
MAX_BYTES=4096
TIMEOUT=1.0
CAPACITY=16
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',required=True)
 c=json.loads(pathlib.Path(p.parse_args().config).read_text());db=pathlib.Path(c['db'])
 db.parent.mkdir(parents=True,exist_ok=True);os.chmod(db.parent,0o700)
 def pub(name):return serialization.load_pem_public_key(pathlib.Path(c[name]).read_bytes())
 b=BoundBroker(db,{int(k):v for k,v in c['roles'].items()},c['wal'],pub('target_pub'),pub('floor_pub'))
 with b.connect() as d:d.execute('INSERT OR IGNORE INTO bound VALUES(?,?,?)',(c['resource'],'0'*64,0))
 os.chmod(db,0o600)
 path=pathlib.Path(c['socket']);parent=path.parent
 if not parent.exists():parent.mkdir(mode=0o710,parents=True)
 if parent.is_symlink() or parent.stat().st_uid!=os.geteuid():raise RuntimeError('SOCKET_PARENT_OWNER')
 if parent.stat().st_mode & 0o007:raise RuntimeError('SOCKET_PARENT_WORLD_ACCESS')
 os.chmod(parent,0o710)
 if os.path.lexists(path):raise RuntimeError('SOCKET_EXISTS')
 sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);sock.bind(str(path))
 os.chmod(path,0o660);sock.listen(32);slots=threading.BoundedSemaphore(CAPACITY)
 print('READY',flush=True)
 def handle(conn):
  try:
   with conn:
    try:
     conn.settimeout(TIMEOUT)
     _,uid,_=struct.unpack('3i',conn.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
     if uid not in b.uid_roles:raise ValueError('UNKNOWN_UID')
     data=b''
     while not data.endswith(b'\n'):
      chunk=conn.recv(min(1024,MAX_BYTES+1-len(data)))
      if not chunk:raise ValueError('INCOMPLETE')
      data+=chunk
      if len(data)>MAX_BYTES:raise ValueError('TOO_LARGE')
     result=b.run(uid,json.loads(data))
    except Exception as e:result={'ok':False,'error':str(e)}
    try:conn.sendall(json.dumps(result).encode()+b'\n')
    except OSError:pass
  finally:slots.release()
 try:
  while True:
   conn,_=sock.accept()
   if not slots.acquire(blocking=False):conn.close();continue
   threading.Thread(target=handle,args=(conn,),daemon=True).start()
 finally:sock.close()
if __name__=='__main__':main()
