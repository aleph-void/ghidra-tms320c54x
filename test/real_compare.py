#!/usr/bin/env python3
"""real_compare.py <ghidra listing> <objdump listing>: every instruction Ghidra disassembled must match objdump's text at the same word address."""
import os, sys, importlib.util
spec = importlib.util.spec_from_file_location('compare', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'compare.py'))
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
ob = {}
for l in open(sys.argv[2]):
    a, t = l.rstrip('\n').split(' ', 1); ob[int(a, 16)] = __import__('re').sub(r'(?<![\w.])([0-9a-f]+)(?= <)', r'0x\1', t)
n = ok = 0; bad = []
for l in open(sys.argv[1]):
    a, ln, t = l.rstrip('\n').split(' ', 2); a = int(a, 16); n += 1
    t = t.lstrip('_')
    if a in ob and c.canon(t) == c.canon(ob[a]): ok += 1
    else: bad.append((hex(a), t, ob.get(a)))
print(f'   {n} instructions, {ok} identical to objdump after display normalisation, {len(bad)} differ')
for b in bad[:15]: print('     ', b)
sys.exit(1 if bad else 0)
