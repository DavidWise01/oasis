"""S246: TLS-transparent loopback transport isolation and connection restoration."""
import socket,threading,select
class PartitionProxy:
 def __init__(self,upstream):
  self.upstream=upstream;self.isolated=threading.Event();self.isolated.set();self.stop=threading.Event()
  self.listener=socket.socket();self.listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
  self.listener.bind(('127.0.0.1',0));self.listener.listen(32);self.listener.settimeout(.2)
  self.port=self.listener.getsockname()[1];self.denied=0;self.forwarded=0
  self.thread=threading.Thread(target=self._run,daemon=True);self.thread.start()
 def _run(self):
  while not self.stop.is_set():
   try:c,_=self.listener.accept()
   except socket.timeout:continue
   except OSError:break
   if self.isolated.is_set():
    self.denied+=1;c.shutdown(socket.SHUT_RDWR);c.close();continue
   self.forwarded+=1;threading.Thread(target=self._relay,args=(c,),daemon=True).start()
 def _relay(self,c):
  try:
   with c,socket.create_connection(('127.0.0.1',self.upstream),timeout=3) as s:
    c.settimeout(4);s.settimeout(4)
    while not self.stop.is_set():
     ready,_,_=select.select([c,s],[],[],.1)
     for src in ready:
      try:b=src.recv(65536)
      except OSError:return
      if not b:return
      (s if src is c else c).sendall(b)
  except OSError:pass
 def heal(self):self.isolated.clear()
 def close(self):self.stop.set();self.listener.close();self.thread.join(2)
