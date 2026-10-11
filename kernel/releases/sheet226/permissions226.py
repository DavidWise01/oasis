"""S226 permission assertions for a writer-owned, repair-readable WAL."""
import os,stat,pathlib
def verify_layout(wal_directory,wal_file,writer_uid=1,repair_gid=1):
    d=pathlib.Path(wal_directory).stat()
    w=pathlib.Path(wal_file).stat()
    assert stat.S_ISDIR(d.st_mode) and stat.S_ISREG(w.st_mode), 'BAD_TYPE'
    assert d.st_uid==writer_uid and w.st_uid==writer_uid,'OWNER'
    assert d.st_gid==repair_gid and w.st_gid==repair_gid,'GROUP'
    assert stat.S_IMODE(d.st_mode)==0o750,'DIRECTORY_MODE'
    assert stat.S_IMODE(w.st_mode)==0o640,'WAL_MODE'
    return True
