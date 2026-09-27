#!/usr/bin/env python3
"""PAL-ZIP v110 frozen: clean higher-recovery prefix MERGE2 authorization."""
MEMBERS=("T0","T1","T2")
THRESHOLD=2
MERGE_LABEL='CLEAN-HIGHER-RECOVERY-RANK-PREFIX-MERGE2'
CERT_LABEL='CLEAN-HIGHER-RECOVERY-PREFIX-MERGE-PARENT-CERT'
AUTH_LABEL='AUTHORIZED-CLEAN-HIGHER-RECOVERY-PREFIX-MERGE2'
def _lp(s:str)->str: return f"{len(s)}:{s}"
def merge2(parent_a,parent_b):
    if parent_a==parent_b: raise ValueError("MERGE2 requires distinct exact v109 parents")
    a,b=sorted((parent_a,parent_b)); return MERGE_LABEL+"|"+_lp(a)+"|"+_lp(b)
def cert_binds(cert,parent,peer,merge_id,auth_epoch):
    prefix=CERT_LABEL+"|"+_lp(parent)+"|"+_lp(peer)+"|"+_lp(merge_id)+"|"+_lp(auth_epoch)+"|"+_lp(str(THRESHOLD))+"|"
    return cert.startswith(prefix)
