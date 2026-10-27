#!/usr/bin/env python3
"""asm2bin.py <source.asm> <outprefix>: assemble with GNU as (tic54x-coff) and write
<outprefix>.bin (big-endian 16-bit words of .text), <outprefix>.lst ("<word addr hex> <objdump text>" per instruction),
<outprefix>.entries ("<label> <word addr hex>" for every text label).  Environment: TIC54X_AS, OBJDUMP."""
import os
import re
import shutil
import struct
import subprocess
import sys

AS = os.environ.get('TIC54X_AS') or shutil.which('tic54x-coff-as')
OBJ = os.environ.get('OBJDUMP') or shutil.which('objdump')
NM = os.path.join(os.path.dirname(OBJ), 'nm') if os.path.dirname(OBJ) else 'nm'
src, pre = sys.argv[1], sys.argv[2]
subprocess.run([AS, src, '-o', pre + '.o'], check=True)
d = subprocess.run([OBJ, '-z', '-d', pre + '.o'], capture_output=True, text=True, check=True).stdout
wd, lst, last = {}, {}, None
for l in d.split('\n'):
    m = re.match(r'^\s*([0-9a-f]+):\t((?:[0-9a-f]{4} )+)\s*(.*)$', l)
    if m:
        a = int(m.group(1), 16)
        for q, x in enumerate(m.group(2).split()):
            wd[a + q] = int(x, 16)
        if m.group(3).strip():
            lst[a] = m.group(3).strip()
open(pre + '.bin', 'wb').write(b''.join(struct.pack('>H', wd[a]) for a in range(max(wd) + 1)))
with open(pre + '.lst', 'w') as f:
    for a in sorted(lst):
        f.write('%x %s\n' % (a, lst[a]))
nm = subprocess.run([NM, pre + '.o'], capture_output=True, text=True, check=True).stdout
with open(pre + '.entries', 'w') as f:
    for l in nm.split('\n'):
        m = re.match(r'^([0-9a-f]+) T (\w+)$', l.strip())
        if m and not m.group(2).startswith('.'):
            f.write('%s %s\n' % (m.group(2), m.group(1)))
os.remove(pre + '.o')
