"""S245: transparent local TLS/TCP relay; reset after floor's durable ACK."""
import socket,threading,select,time,sqlite3
class DropReplyProxy:
 def __init__(self,target_port,floor_db):
  self.floor_db=str(floor_db);self.target_port=target_port
  self.listener=socket.socket();self.listener.bind(('127.0.0.1',0));self.listener.listen(1)
  self.port=self.listener.getsockname()[1]
  self.done=threading.Event();self.dropped=threading.Event()
  self.th=threading.Thread(target=self._run,daemon=True);self.th.start()
 def _run(self):
  try:
   client,_=self.listener.accept()
   server=socket.create_connection(('127.0.0.1',self.target_port),timeout=5)
   with client,server:
    client.setblocking(False);server.setblocking(False)
    deadline=time.monotonic()+8
    while time.monotonic()<deadline:
     readable,_,_=select.select([client,server],[],[],0.01)
     for src in readable:
      try:data=src.recv(65536)
      except BlockingIOError:continue
      if not data:return
      if src is client:server.sendall(data)
      else:
       if self._committed():self.dropped.set();return
       client.sendall(data)
     if self._committed():self.dropped.set();return
  finally:self.done.set();self.listener.close()
 def _committed(self):
  try:
   with sqlite3.connect(self.floor_db,timeout=0.05) as d:
    return d.execute('SELECT count(*) FROM signed_ack').fetchone()[0]>0
  except (sqlite3.OperationalError,FileNotFoundError):return False
