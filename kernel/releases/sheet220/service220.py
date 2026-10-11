"""S220 local Unix socket: signed input provenance required for every append."""
import os,json,socket,pathlib,sys
from cryptography.hazmat.primitives import serialization
from writer219 import FencedWriter

def serve(config):
    pub=serialization.load_pem_public_key(pathlib.Path(config['input_issuer_public']).read_bytes())
    writer=FencedWriter(config,pub)
    sock=config['socket']
    pathlib.Path(sock).parent.mkdir(parents=True,exist_ok=True)
    if os.path.lexists(sock):
        raise RuntimeError('SOCKET_EXISTS')
    s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
    s.bind(sock)
    os.chmod(sock,0o600)
    s.listen(8)
    print('READY',flush=True)
    while True:
        c,_=s.accept()
        with c:
            try:
                data=c.recv(4096)
                req=json.loads(data)
                result=writer.append(req)
            except Exception as ex:
                result={'ok':False,'error':str(ex)}
            c.sendall(json.dumps(result).encode())

if __name__=='__main__':
    serve(json.loads(pathlib.Path(sys.argv[1]).read_text()))
