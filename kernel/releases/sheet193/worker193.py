import json,os,pathlib,sys,time
state,ready=map(pathlib.Path,sys.argv[1:]);fd=os.open(state,os.O_CREAT|os.O_WRONLY|os.O_TRUNC,0o600)
try:os.write(fd,b'{"status":"BOUND_PENDING_FLOOR","generation":3}');os.fsync(fd)
finally:os.close(fd)
ready.write_text('ready');fd=os.open(ready,os.O_RDONLY);os.fsync(fd);os.close(fd)
while True:time.sleep(1)
