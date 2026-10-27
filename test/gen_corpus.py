#!/usr/bin/env python3
"""Corpus of 16-byte slots (4 instruction words, big-endian, then 4 NOP words) for the TMS320C54x decode differential.

  gen_corpus.py <out.bin> [random-slots] [seed]

* every first word 0000..FFFF with four different following-word triples (zeros, all ones, two random)
* random slots
"""
import random
import struct
import sys

out = sys.argv[1]
nrand = int(sys.argv[2]) if len(sys.argv) > 2 else 100000
rnd = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 1)
NOP = struct.pack('>H', 0xF495) * 4
buf = bytearray()
n = 0
for w in range(65536):
    for v in range(4):
        if v == 0:
            t = [0, 0, 0]
        elif v == 1:
            t = [0xFFFF] * 3
        else:
            t = [rnd.randrange(65536) for _ in range(3)]
        buf += struct.pack('>4H', w, *t) + NOP
        n += 1
for _ in range(nrand):
    buf += struct.pack('>4H', *[rnd.randrange(65536) for _ in range(4)]) + NOP
    n += 1
# the 0x6Fxx family (ADD/SUB/LD/STH/STL Smem,SHIFT,...): the second word must have bits 15-10 = 000011
for w in range(0x6f00, 0x7000):
    for e in range(0x0c00, 0x1000, 7):
        buf += struct.pack('>4H', w, e, rnd.randrange(65536), rnd.randrange(65536)) + NOP
        n += 1
        if w >= 0x6f80:      # long-offset / absolute Smem: the extension word is the third word
            buf += struct.pack('>4H', w, rnd.randrange(65536), e, rnd.randrange(65536)) + NOP
            n += 1
open(out, 'wb').write(buf)
print(n, 'slots')
