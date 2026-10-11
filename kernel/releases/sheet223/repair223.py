"""S223 restricted local repair service. Access is OS DAC + dual signatures."""
import os,sys,json,socket,pathlib
from reconcile223 import reconcile
def serve(config):
    path=config['repair_socket'];p=pathlib.Path(path)
    if p.exists():raise RuntimeError('SOCKET_EXISTS')
    s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
    s.bind(path);os.chmod(path,0o600);s.listen(8)
    print('READY',flush=True)
    while True:
        c,_=s.accept()
        with c:
            try:result=reconcile(config,json.loads(c.recv(65536)))
            except Exception as e:result={'ok':False,'error':str(e)}
            c.sendall(json.dumps(result).encode())
if __name__=='__main__':serve(json.loads(pathlib.Path(sys.argv[1]).read_text()))
