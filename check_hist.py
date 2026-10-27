#!/usr/bin/env python3
import os, subprocess
os.chdir(r'C:\Users\Dave\oasis')
r = subprocess.run(['git', 'show', 'HEAD:build_rome_gods.py'], capture_output=True, text=True)
with open('/tmp/head_build.txt', 'w') as f:
    f.write(r.stdout)
print('Wrote /tmp/head_build.txt')
lines = r.stdout.split('\n')
hist_keys = []
in_hist = False
for line in lines:
    if 'CANVAS_HISTORY = {' in line:
        in_hist = True
    if in_hist:
        stripped = line.strip()
        if stripped.startswith('"') and ':' in stripped:
            k = stripped.split(':', 1)[0].strip().strip('"')
            if k:
                hist_keys.append(k)
        if stripped == '}':
            break
print('HISTORY keys:', len(hist_keys))
for k in hist_keys:
    print('  ', k)
