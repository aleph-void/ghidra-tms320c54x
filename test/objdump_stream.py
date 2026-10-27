#!/usr/bin/env python3
"""Disassemble the slot corpus of gen_corpus.py with GNU objdump (-m tms320c54x) in one run.

  objdump_stream.py <corpus.bin> <out.txt>

objdump reads little-endian words, so the big-endian corpus is word-swapped first.  The 4 NOP words after each
slot's 4 instruction words keep objdump in step.  Output per slot: "<slot> <length-in-words> <text>"
(length 0 / text BAD when objdump printed (bad)).
"""
import os
import re
import subprocess
import sys
import tempfile

OBJ = os.environ.get('OBJDUMP', 'objdump')
data = open(sys.argv[1], 'rb').read()
sw = bytearray(len(data))
sw[0::2] = data[1::2]
sw[1::2] = data[0::2]
tmp = tempfile.mkdtemp(prefix='objstream.', dir=os.environ.get('TMPDIR', '/tmp'))
p = os.path.join(tmp, 's.bin')
open(p, 'wb').write(sw)
r = subprocess.run([OBJ, '-b', 'binary', '-m', 'tms320c54x', '-z', '-D', p], capture_output=True, text=True)
os.remove(p)
os.rmdir(tmp)
LINE = re.compile(r'^\s*([0-9a-f]+):\t((?:[0-9a-f]{4} )+)\s*(.*)$')
res = {}
cur = None
for l in r.stdout.split('\n'):
    m = LINE.match(l)
    if not m:
        continue
    a = int(m.group(1), 16)
    text = m.group(3).strip()
    if text == '' and cur is not None:
        res[cur][0] += len(m.group(2).split())
    elif a % 8 == 0:
        cur = a // 8
        res[cur] = [len(m.group(2).split()), text]
    else:
        cur = None
n = len(data) // 16
with open(sys.argv[2], 'w') as o:
    for i in range(n):
        k, t = res.get(i, (0, 'MISSING'))
        o.write(f'{i} {k} {t}\n')
