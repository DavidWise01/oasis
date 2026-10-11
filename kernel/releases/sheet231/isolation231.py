"""S231 broker-private control database directory layout (Linux POSIX DAC)."""
import os,pathlib,stat
def initialize_private(directory,broker_uid,broker_gid):
 p=pathlib.Path(directory);p.mkdir(mode=0o700,parents=True,exist_ok=True)
 os.chown(p,broker_uid,broker_gid);os.chmod(p,0o700)
 return p/'control.sqlite'
def check_layout(directory,broker_uid):
 p=pathlib.Path(directory)
 assert p.stat().st_uid==broker_uid
 assert stat.S_IMODE(p.stat().st_mode)==0o700
 for f in p.iterdir():
  st=f.lstat()
  assert st.st_uid==broker_uid,(f,'OWNER')
  assert not (stat.S_IMODE(st.st_mode)&0o077),(f,'EXCESS_PERMISSIONS')
 return True
