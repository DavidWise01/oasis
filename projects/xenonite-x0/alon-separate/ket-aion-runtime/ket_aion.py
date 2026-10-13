#!/usr/bin/env python3
"""A.I.O.N. additive execution adapter aligned to OASIS K/E/T (not frozen runtime).

K: integrity, canonical intent, root-material validation.
E: execute actual crystal JS and/or synthetic pulse Python modules.
T: content-addressable receipts and local append-only hash-chain ledger.

Scientific limits: v1.4 output is synthetic trap spectroscopy; not real material data.
"""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib, shutil, subprocess, sys, tempfile

BASE = pathlib.Path(__file__).resolve().parent
SCHEMA = "oasis.ket.aion.adapter.v1"
CANON = {
    "parent": "K.E.T. | Kernel / Emergence / Time",
    "control_tracks": ["i:identity", "u:consequence", "u.s:lifecycle"],
    "status": "additive adapter, not upstream frozen executable or certified production kernel",
    "material": "Al23O27N5",
    "material_state": "unrelaxed representative defect-spinel; not experimentally measured",
    "pulse_state": "deterministic synthetic readout; not physical measured ALON/Si",
    "iodine": "excluded from primary substrate"
}


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hashfile(path: pathlib.Path) -> str:
    return sha(path.read_bytes())


def rel(path: pathlib.Path, root: pathlib.Path) -> str:
    return path.relative_to(root).as_posix()


def checked_process(argv, cwd):
    proc = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, check=False, timeout=120)
    if proc.returncode:
        raise RuntimeError("Module exited " + str(proc.returncode) + ": " + proc.stderr[-3000:])
    return proc.stdout


def ensure_intact_ledger(path: pathlib.Path) -> list:
    if not path.exists():
        return []
    records=[]
    prior="GENESIS"
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            raise ValueError("Ledger has a blank record; fail closed")
        record=json.loads(line)
        got=record.get("entry_hash")
        payload={k:v for k,v in record.items() if k!="entry_hash"}
        if got!=sha(canonical(payload)) or record.get("previous_hash")!=prior or record.get("sequence")!=len(records)+1:
            raise ValueError("Ledger hash-chain invalid; append denied")
        records.append(record)
        prior=got
    return records


def run(selection: str, out: pathlib.Path) -> dict:
    out=out.resolve()
    if out==BASE or BASE in out.parents:
        # Protect source tree from accidental output replacement.
        raise ValueError("Select a separate output directory outside the source tree")
    out.mkdir(parents=True,exist_ok=True)
    source_files=[BASE/'ket_aion.py', BASE/'crystal'/'bridge.mjs',
                  BASE/'crystal'/'alon-reference.json',BASE/'pulse'/'aion_v14.py']
    upstream=BASE.parent/'material-build'/'alon-crystal.mjs'
    actual_crystal_source=upstream if upstream.is_file() else BASE/'crystal'/'alon-crystal.mjs'
    source_files.append(actual_crystal_source)
    if not all(p.is_file() for p in source_files):
        raise FileNotFoundError("One or more versioned source files are absent")
    sources={(rel(p,BASE) if p.is_relative_to(BASE) else '../material-build/alon-crystal.mjs'):hashfile(p) for p in source_files}
    descriptor={"schema":SCHEMA,"mode":selection,"source_sha256":sources,"canonical":CANON}
    event_id=sha(canonical(descriptor))
    outputs={}
    checks=[]
    tracks={"i":{"state":"verified","event_id":event_id,"sources":sources},
            "u":{"state":"pending","modules":{}},"u.s":{"state":"pending"}}
    with tempfile.TemporaryDirectory(prefix="aion-ket-") as sandbox:
        tmp=pathlib.Path(sandbox)
        if selection in ('crystal','all'):
            node=shutil.which('node')
            if not node:
                raise RuntimeError('Node.js executable required for crystal module')
            crystal=tmp/'crystal';crystal.mkdir()
            std=checked_process([node,str(BASE/'crystal'/'bridge.mjs'),str(crystal)],BASE)
            summary=json.loads(std.strip().splitlines()[-1])
            reference=json.loads((BASE/'crystal'/'alon-reference.json').read_text(encoding='utf-8'))
            generated=json.loads((crystal/'alon-cell.json').read_text(encoding='utf-8'))
            # Compare chemistry, coordinates and bond endpoints to reference (no mutating freeze).
            assert generated['sites']==reference['sites']
            assert generated['bonds']==reference['bonds']
            assert generated['counts']==reference['counts']
            assert summary['occupied']==55 and summary['bonds']==122 and summary['boundary_links']==42
            assert summary['formal_ionic_charge']==0
            for file in crystal.iterdir():
                destination=out/file.name
                shutil.copy2(file,destination)
                outputs[file.name]=hashfile(destination)
            checks.extend(['crystal_sites_55','crystal_bonds_122','crystal_periodic_42','crystal_charge_0',
                           'crystal_coordinates_match_reference','crystal_bonds_match_reference'])
            tracks['u']['modules']['crystal']={**summary,'state':'executed','outputs':['alon-cell.json','alon-cell.cif','alon-cell.xyz']}
        if selection in ('pulse','all'):
            pulse=tmp/'pulse';pulse.mkdir()
            shutil.copy2(BASE/'pulse'/'aion_v14.py',pulse/'aion_v14.py')
            std=checked_process([sys.executable,str(pulse/'aion_v14.py')],pulse)
            console=json.loads(std)
            runresult=json.loads((pulse/'aion-v14-results.json').read_text(encoding='utf-8'))
            with (pulse/'aion-v14-synthetic-pulses.csv').open(encoding='utf-8') as fh:
                nrows=sum(1 for _ in fh)-1
            assert runresult['schema']=='aion.v1.4.pulse-identifiability.v1'
            assert console['total_observations']==nrows==700
            assert console['fit_runs']==15
            assert len(runresult['protocols'])==5
            assert runresult['truth']['fast']['release_s']==.15 and runresult['truth']['slow']['release_s']==1.6
            for fn in ['aion-v14-results.json','aion-v14-synthetic-pulses.csv',
                       'aion-v14-fit-ranking.csv','aion-v14-model-predictions.csv']:
                destination=out/fn
                shutil.copy2(pulse/fn,destination)
                outputs[fn]=hashfile(destination)
            checks.extend(['pulse_synthetic_700','pulse_fits_15','pulse_5_protocols',
                           'pulse_known_trap_times','pulse_noise_seeded'])
            tracks['u']['modules']['pulse']={"state":"executed","observations":nrows,
                "model_fits":15,"protocols":5,"synthetic":True,"outputs":[
                'aion-v14-results.json','aion-v14-synthetic-pulses.csv',
                'aion-v14-fit-ranking.csv','aion-v14-model-predictions.csv']}
    tracks['u']['state']='executed'
    previous=ensure_intact_ledger(out/'ket-aion-ledger.jsonl')
    if previous and previous[-1]['event_id']==event_id:
        # Idempotence is allowed only for byte-for-byte reproducible output.
        if previous[-1]['outputs_sha256'] != outputs:
            raise ValueError('Same event inputs produced different outputs; quarantined')
        idempotent=True
        seq=previous[-1]['sequence'];entry_hash=previous[-1]['entry_hash']
    else:
        idempotent=False
        seq=len(previous)+1
        payload={"sequence":seq,"previous_hash": previous[-1]['entry_hash'] if previous else 'GENESIS',
                 "event_id":event_id,"mode":selection,"outputs_sha256":outputs}
        entry_hash=sha(canonical(payload))
        record={**payload,"entry_hash":entry_hash}
        with (out/'ket-aion-ledger.jsonl').open('a',encoding='utf-8',newline='\n') as f:
            f.write(json.dumps(record,sort_keys=True,separators=(',',':'))+'\n')
            f.flush();os.fsync(f.fileno())
    tracks['u.s']={"state":"recorded","ledger_sequence":seq,"entry_hash":entry_hash,
                   "idempotent_replay":idempotent,"ledger":"ket-aion-ledger.jsonl"}
    result={"schema":SCHEMA,"event_id":event_id,"mode":selection,"checks_passed":len(checks),
            "checks":checks,"tracks":tracks,"outputs_sha256":outputs,"limits":CANON,
            "scientific_status":"synthetic computational integration only; no experimental validation",
            "upstream_frozen_files_modified":False}
    (out/'ket-aion-receipt.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return result


def main():
    parser=argparse.ArgumentParser(description='K.E.T.-aligned A.I.O.N. additive adapter')
    parser.add_argument('--module',choices=['crystal','pulse','all'],default='all')
    parser.add_argument('--out',default='./aion-run')
    args=parser.parse_args()
    try:
        report=run(args.module,pathlib.Path(args.out))
    except (Exception,AssertionError) as e:
        print(json.dumps({'state':'QUARANTINED','error':str(e),'schema':SCHEMA}),file=sys.stderr)
        raise SystemExit(1)
    print(json.dumps({'state':'VERIFIED_EXECUTION','event_id':report['event_id'],
                      'checks_passed':report['checks_passed'],
                      'modules':list(report['tracks']['u']['modules']),
                      'ledger_sequence':report['tracks']['u.s']['ledger_sequence'],
                      'idempotent':report['tracks']['u.s']['idempotent_replay'],
                      'output':str(pathlib.Path(args.out).resolve())},indent=2))

if __name__=='__main__':main()
