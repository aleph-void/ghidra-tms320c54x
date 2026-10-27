#!/usr/bin/env python3
"""Decode every corpus slot with the clean-room table (tools/c54x_disasm.py, built only from tools/c54x_encodings.py)
and compare it with the module (DumpWords output) and with GNU objdump; bucket every difference.

  cleanroom_diff.py <corpus.bin> <module.txt> <objdump.txt> [--show N]

Display spellings go through compare.py's canon(); SSBX/RSBX operands are reduced to (status register, bit) first.
Exit status 1 when a difference is not in a known bucket."""
import os
import re
import struct
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
sys.path.insert(0, HERE)
from compare import canon as _canon        # noqa: E402
from c54x_disasm import decode             # noqa: E402

# SPRU172C Appendix B, Figures B-2 (ST0) and B-3 (ST1)
SBITS = {'tc': (0, 12), 'c': (0, 11), 'ova': (0, 10), 'ovb': (0, 9), 'braf': (1, 15), 'cpl': (1, 14), 'xf': (1, 13),
         'hm': (1, 12), 'intm': (1, 11), 'ovm': (1, 9), 'sxm': (1, 8), 'c16': (1, 7), 'frct': (1, 6), 'cmpt': (1, 5)}


def canon(t):
    m = re.match(r'\s*(ssbx|rsbx)\s+(.*)$', t, re.I)
    if m:
        ops = [x.strip().lower() for x in m.group(2).split(',')]
        if len(ops) == 1:
            n, b = SBITS[ops[0]]
        else:
            n = int(ops[0].replace('st', ''))
            b = SBITS[ops[1]][1] if ops[1] in SBITS else int(ops[1], 0)
        t = '%s %d' % (m.group(1).lower(), n * 16 + b)
    return _canon(t)


MMRF = ('ldm', 'stlm', 'stm', 'mvdm', 'mvmd', 'pshm', 'popm')


def reason(who, mine, other):
    mn = other.split()[0].lower() if other.split() else ''
    if who == 'module':
        return None                      # the module must agree with the table everywhere
    if mn in ('bc', 'bcd', 'cc', 'ccd', 'rc', 'rcd', 'xc') and mine is None:
        return 'reserved: 8-bit condition that is no SPRU172C 4-18 / Table A-2 combination'
    if mn in ('saccd', 'srccd', 'strcd') and mine is None:
        return 'reserved: 4-bit condition not in the SACCD/SRCCD/STRCD table (SPRU172C 4-152); objdump prints ??'
    if mn == 'mvmm' and mine is None:
        return 'reserved: MVMM register field 9-15 (SPRU172C 4-116; gas rejects these registers)'
    if mn in ('banz', 'banzd') and mine is None:
        return 'reserved: BANZ[D] with I=0 or *(lk): Sind is single indirect addressing (SPRU172C 4-16)'
    if mn in MMRF and mine is None:
        return 'reserved: MMR operand in a long-offset/absolute mode (SPRU131G Table 5-4 note)'
    if mn in MMRF:
        return 'objdump bug: MMR operand with I=1 shown as an MMR address (SPRU131G 5.5; gas encodes it as indirect)'
    if mn == 'estop' and mine is None:
        return 'not in the TI manuals: ESTOP (F4F0), objdump only'
    if mn == 'idle' and mine is None:
        return 'reserved: IDLE NN=11 (SPRU172C 4-63 lists 00/10/01; gas assembles IDLE 3 as F5E1)'
    return None


def main():
    corpus = open(sys.argv[1], 'rb').read()
    gh = open(sys.argv[2]).read().split('\n')
    ob = open(sys.argv[3]).read().split('\n')
    show = int(sys.argv[sys.argv.index('--show') + 1]) if '--show' in sys.argv else 3
    cnt = {'module': Counter(), 'objdump': Counter()}
    ex = defaultdict(list)
    for i in range(len(corpus) // 16):
        ws = list(struct.unpack('>4H', corpus[i * 16:i * 16 + 8]))
        r = decode(ws)
        mine = canon(r[1]) if r else None
        for who, lines in (('module', gh), ('objdump', ob)):
            si, sl, st = lines[i].split(' ', 2)
            assert int(si) == i
            o = canon(st)
            if mine is None and o is None:
                k = 'both invalid'
            elif mine is not None and o is not None and int(sl) == r[0] and mine == o:
                k = 'agree'
            else:
                k = reason(who, mine, st) or 'UNEXPLAINED %s' % (
                    'length' if mine and o else 'table rejects' if o else 'table decodes')
                if len(ex[(who, k)]) < show:
                    ex[(who, k)].append('slot %d %s: table %r  %s %r' % (
                        i, ' '.join('%04x' % w for w in ws), r[1] if r else None, who, st))
            cnt[who][k] += 1
    bad = 0
    for who in ('module', 'objdump'):
        print('   clean-room table vs %s:' % who)
        for k, v in sorted(cnt[who].items(), key=lambda kv: -kv[1]):
            print('      %-100s %8d' % (k, v))
            if k.startswith('UNEXPLAINED'):
                bad += v
                for e in ex[(who, k)]:
                    print('          ', e)
    print('   unexplained', bad)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
