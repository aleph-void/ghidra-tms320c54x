#!/usr/bin/env python3
"""Re-assemble the module's disassembly with GNU as (tic54x target) and compare the bytes with the original words.

  asm_roundtrip.py <ghidra.txt> <objdump.txt> <corpus.bin> <sample-size> <seed> [--show N]

The module's text of each sampled instruction is assembled; the words must equal the corpus words.  Lines the
assembler rejects are bucketed by mnemonic (the assembler is a second implementation of the instruction syntax).
Environment: TIC54X_AS, OBJDUMP, TMPDIR.
"""
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import importlib.util
from collections import Counter, defaultdict

spec = importlib.util.spec_from_file_location('compare', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'compare.py'))
cmp_ = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cmp_)
AS = os.environ.get('TIC54X_AS') or shutil.which('tic54x-coff-as')
OBJ = os.environ.get('OBJDUMP') or shutil.which('objdump')


def main():
    gh = [l.rstrip('\n').split(' ', 2) for l in open(sys.argv[1])]
    ob = [l.rstrip('\n').split(' ', 2) for l in open(sys.argv[2])]
    corpus = open(sys.argv[3], 'rb').read()
    n, seed = int(sys.argv[4]), int(sys.argv[5])
    show = int(sys.argv[sys.argv.index('--show') + 1]) if '--show' in sys.argv else 5
    rnd = random.Random(seed)
    cand = [i for i, (_, ln, t) in enumerate(gh) if t != 'BAD' and int(ln) > 0]
    pick = sorted(rnd.sample(cand, min(n, len(cand))))
    tmp = tempfile.mkdtemp(prefix='asmrt.', dir=os.environ.get('TMPDIR', '/tmp'))
    lines = {i: gh[i][2] for i in pick}
    rejected = {}
    while True:
        keep = [i for i in pick if i not in rejected]
        src = os.path.join(tmp, 'rt.asm')
        with open(src, 'w') as f:
            f.write(' .mmregs\n .text\n')
            for i in keep:
                f.write('l%d:\n %s\n' % (i, lines[i]))
        r = subprocess.run([AS, src, '-o', os.path.join(tmp, 'rt.o')], capture_output=True, text=True)
        bad = {int(m.group(1)) for m in re.finditer(r'rt\.asm:(\d+): Error', r.stderr)}
        if not bad:
            break
        for ln in bad:
            if 3 <= ln < 3 + 2 * len(keep) and ln % 2 == 0:
                rejected[keep[(ln - 4) // 2]] = re.search(r'rt\.asm:%d: Error: (.*)' % ln, r.stderr).group(1)
        if not any(3 <= ln < 3 + 2 * len(keep) for ln in bad):
            print(r.stderr[:2000])
            sys.exit(1)
    d = subprocess.run([OBJ, '-z', '-d', os.path.join(tmp, 'rt.o')], capture_output=True, text=True).stdout
    wd = {}
    txt = {}
    for l in d.split('\n'):
        m = re.match(r'^\s*([0-9a-f]+):\t((?:[0-9a-f]{4} )+)\s*(.*)$', l)
        if m:
            if m.group(3).strip():
                txt[int(m.group(1), 16)] = m.group(3).strip()
            for q, x in enumerate(m.group(2).split()):
                wd[int(m.group(1), 16) + q] = int(x, 16)
    words = [wd.get(a, -1) for a in range(max(wd) + 1)]
    addr = {}
    nm = subprocess.run([OBJ.replace('objdump', 'nm'), os.path.join(tmp, 'rt.o')], capture_output=True, text=True).stdout
    for l in nm.split('\n'):
        m = re.match(r'^([0-9a-f]+) \w l(\d+)$', l.strip())
        if m:
            addr[int(m.group(2))] = int(m.group(1), 16)
    shutil.rmtree(tmp)
    same = diff = absmode = altenc = 0
    ex = defaultdict(list)
    cnt = Counter()
    for j, i in enumerate(keep):
        k = int(gh[i][1])
        want = [int.from_bytes(corpus[i * 16 + 2 * q:i * 16 + 2 * q + 2], 'big') for q in range(k)]
        a0 = addr[i]
        a1 = addr[keep[j + 1]] if j + 1 < len(keep) else len(words)
        got = words[a0:a1]
        if got == want:
            same += 1
            continue
        mn = lines[i].split()[0]
        if len(got) == len(want) and got[1:] == want[1:] and (want[0] & 0xf8) == 0xf8 and (got[0] & ~7) == (want[0] & ~7):
            absmode += 1                       # *(lk) absolute mode: the ARx field is not used
        elif len(got) == len(want) and got[0] >> 8 == want[0] >> 8 and (want[0] & 0xf8) == 0xf8 and (got[0] & 0xf8) == 0xf8:
            absmode += 1
        elif a0 in txt and cmp_.canon(txt[a0]) == cmp_.canon(ob[i][2]):
            altenc += 1                        # the assembler picked another encoding of the same instruction
        else:
            diff += 1
            cnt[mn] += 1
            if len(ex[mn]) < show:
                ex[mn].append(f'slot {i}: {lines[i]!r} words {[hex(x) for x in want]} reassembled {[hex(x) for x in got]} (objdump: {ob[i][2]!r} / {txt.get(a0)!r})')
    print(f'   sampled {len(pick)}: reassembled to identical words {same}, *(lk) with a different unused ARx field {absmode}, another encoding of the same instruction {altenc}, DIFFERENT {diff}, rejected by the assembler {len(rejected)}')
    rc = Counter(l.split()[0] for l in (lines[i] for i in rejected))
    print('   rejected by mnemonic:', dict(rc.most_common(12)))
    why = Counter(re.sub(r"'[^']*'", "'..'", m) for m in rejected.values())
    for m, c in why.most_common(8):
        print(f'      {c:6d} {m}')
    for mn, c in cnt.most_common(15):
        print(f'   differs: {mn} {c}')
        for e in ex[mn]:
            print('      ', e)
    sys.exit(0)


if __name__ == '__main__':
    main()
