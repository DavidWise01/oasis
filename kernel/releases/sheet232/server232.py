"""S232 real UNIX broker with SO_PEERCRED verified Linux UID and private SQLite."""
import argparse,json,os,pathlib,socket,struct,threading
from broker230 import BoundBroker
from cryptography.hazmat.primitives import serialization
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',required=True);c=json.loads(pathlib.Path(p.parse_args().config).read_text())
 db=pathlib.Path(c['db']);db.parent.mkdir(parents=True,exist_ok=True);os.chmod(db.parent,0o700)
 def pub(key):return serialization.load_pem_public_key(pathlib.Path(c[key]).read_bytes())
 broker=BoundBroker(db,{int(k):v for k,v in c['roles'].items()},c['wal'],pub('target_pub'),pub('floor_pub'))
 with broker.connect() as conn:conn.execute('INSERT OR IGNORE INTO bound VALUES(?,?,?)',(c['resource'],'0'*64,0))
 os.chmod(db,0o600)
 sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);sock.bind(c['socket']);os.chmod(c['socket'],0o666);sock.listen(32)
 print('READY',flush=True)
 def handle(conn):
  with conn:
   try:
    _,uid,_=struct.unpack('3i',conn.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
    data=b''
    while not data.endswith(b'\n') and len(data)<16384:
     part=conn.recv(16384-len(data))
     if not part:break
     data+=part
    if len(data)>=16384 or not data.endswith(b'\n'):raise ValueError('FRAMING')
    result=broker.run(uid,json.loads(data))
   except Exception as exc:result={'ok':False,'error':str(exc)}
   conn.sendall(json.dumps(result).encode()+b'\n')
 while True:
  conn,_=sock.accept();threading.Thread(target=handle,args=(conn,),daemon=True).start()
if __name__=='__main__':main()
