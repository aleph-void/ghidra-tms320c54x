#!/usr/bin/env python3
"""classes.py <corpus.bin> <ghidra.txt> <objdump.txt> <kind>: list the distinct first words (grouped) of one difference kind."""
import struct, sys, importlib.util, os
spec = importlib.util.spec_from_file_location('compare', os.path.join(os.path.dirname(__file__), 'compare.py'))
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
d = open(sys.argv[1], 'rb').read()
g = [l.rstrip('\n').split(' ', 2) for l in open(sys.argv[2])]
o = [l.rstrip('\n').split(' ', 2) for l in open(sys.argv[3])]
kind = sys.argv[4]
seen = {}
for i, (x, y) in enumerate(zip(g, o)):
    a, b = c.canon(x[2]), c.canon(y[2])
    if a is None and b is None or a == b and int(x[1]) == int(y[1]):
        continue
    k = ('rej ' if a is None else 'text ') + y[2].split()[0] if b is not None and a is None else ('text ' if a and b else 'extra ') + (y[2].split() or ['?'])[0]
    if k != kind and kind != 'all':
        continue
    w = struct.unpack('>H', d[i * 16:i * 16 + 2])[0]
    seen.setdefault(w, (x[2], y[2]))
ws = sorted(seen)
print(len(ws), 'distinct first words')
step = max(1, len(ws) // 25)
for w in ws[::step]:
    print(f'{w:04x}  module {seen[w][0]!r}  objdump {seen[w][1]!r}')
