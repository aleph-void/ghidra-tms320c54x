#!/usr/bin/env python3
"""Compare DumpWords output (module) with objdump_stream.py output (GNU objdump -m tms320c54x), slot by slot.

  compare.py <ghidra.txt> <objdump.txt> <corpus.bin> <module.slaspec> [--show N]

Both texts are reduced to (mnemonic, operands) with numbers as integers and the spelling differences removed
(@n vs DP+n, #-0x3e45 vs #-15941, MMR(n) vs n, an omitted destination equal to the source accumulator).
Classes: agree, both invalid, and every difference bucketed.  Exit status 1 when a bucket that is not
explained is not empty.
"""
import re
import sys
from collections import Counter, defaultdict


MMR = {'imr': 0, 'ifr': 1, 'st0': 6, 'st1': 7, 'al': 8, 'ah': 9, 'ag': 10, 'bl': 11, 'bh': 12, 'bg': 13, 't': 14, 'trn': 15,
       'ar0': 16, 'ar1': 17, 'ar2': 18, 'ar3': 19, 'ar4': 20, 'ar5': 21, 'ar6': 22, 'ar7': 23, 'sp': 24, 'bk': 25,
       'brc': 26, 'rsa': 27, 'rea': 28, 'pmst': 29, 'xpc': 30}
MMR_INSNS = {'ldm', 'stlm', 'stm', 'mvdm', 'mvmd', 'mvmm', 'pshm', 'popm'}


def num(m):
    s = m.group(0)
    neg = s.startswith('-')
    s = s.lstrip('-')
    v = int(s, 16) if s.lower().startswith('0x') else int(s)
    return str((-v if neg else v) & 0xffff)


def canon(t):
    t = t.strip()
    if t == 'BAD' or t == '???' or t.startswith('(bad') or t == '':
        return None
    t = re.sub(r'\s*<[^>]*>', '', t).lower()
    parts = []
    for p in t.split('||'):
        p = p.strip()
        m = re.match(r'(\S+)\s*(.*)$', p)
        mn, rest = m.group(1), m.group(2).replace(' ', '')
        if mn in ('fb', 'fbd', 'fcall', 'fcalld'):      # extended address: module page:offset, objdump the 23-bit value
            mm = re.fullmatch(r'0x([0-9a-f]+):0x([0-9a-f]+)|0x([0-9a-f]+)', rest)
            v = (int(mm.group(1), 16) << 16 | int(mm.group(2), 16)) if mm.group(1) else int(mm.group(3), 16)
            parts.append((mn, (str(v),)))
            continue
        rest = re.sub(r'\bpa(\d+)', r'\1', rest)
        rest = re.sub(r'(^|,)@', r'\1dp+', rest)
        rest = re.sub(r'mmr\((\w+)\)', r'\1', rest)
        rest = re.sub(r'\bm([0-9a-f]{2})\b', r'0x\1', rest)
        rest = re.sub(r'^st[01],', '', rest) if mn in ('ssbx', 'rsbx') else rest
        rest = re.sub(r'-?0x[0-9a-f]+|-?\b\d+\b', num, rest)
        rest = rest.replace('#', '')
        ops = [x for x in rest.split(',') if x != ''] if rest else []
        if mn in MMR_INSNS:
            ops = [str(MMR[x]) if x in MMR else x for x in ops]
            pos = {'ldm': [0], 'stlm': [1], 'stm': [1], 'mvdm': [1], 'mvmd': [0], 'pshm': [0], 'popm': [0]}.get(mn, [])
            for k in pos:
                # peripheral registers above 0x1f: objdump prints the C5402 names, the module the address
                if k < len(ops) and (not ops[k].isdigit() or int(ops[k]) >= 0x20):
                    ops[k] = 'PERIPH'
        # omitted fields: a shift of 0 and a destination equal to the source accumulator
        ACC = ('a', 'b')
        if mn in ('add', 'sub', 'and', 'or', 'xor', 'ld', 'mac', 'mas', 'macr', 'masr', 'dadd', 'dsub', 'adds', 'subs') \
                and len(ops) >= 3 and ops[1] == '0' and ops[2] in ACC:
            del ops[1]
        if mn in ('add', 'sub', 'and', 'or', 'xor', 'mac', 'mas', 'macr', 'masr', 'dadd', 'dsub', 'sfta', 'sftl') \
                and len(ops) >= 3 and ops[-1] in ACC and ops[-2] in ACC and ops[-1] == ops[-2]:
            ops.pop()
        if mn in ('add', 'sub', 'and', 'or', 'xor') and len(ops) == 2 and ops[0] in ACC and ops[0] == ops[1]:
            ops.pop()
        if mn in ('add', 'sub', 'and', 'or', 'xor', 'ld') and len(ops) == 3 and ops[0] in ACC and ops[0] == ops[2]:
            ops.pop()
        if mn in ('sfta', 'sftl') and len(ops) == 3 and ops[0] == ops[2]:
            ops.pop()
        if mn in ('neg', 'abs', 'cmpl', 'norm', 'rnd', 'macar', 'maca', 'masa', 'masar', 'ld') and len(ops) >= 2 \
                and ops[-1] in ACC and ops[0] != 't' and ops[-1] == ops[0] or \
                mn in ('macar', 'maca', 'masa', 'masar') and len(ops) == 3 and ops[1] == ops[2]:
            ops.pop()
        if mn == 'ld' and len(ops) == 3 and ops[1] == 'asm' and ops[0] == ops[2]:
            ops.pop()
        if mn in ('maca', 'masa', 'macar', 'masar') and len(ops) == 1:
            ops.append('b')   # MACA Smem[,B]: B is the only accumulator that can be the destination
        parts.append((mn, tuple(ops)))
    return tuple(parts)


def valid_conditions(slaspec):
    t = open(slaspec).read()
    cc8 = {int(x, 16) for x in re.findall(r'^cond: .*? is cc8=0x([0-9a-f]+)', t, re.M)}
    cc4 = {int(x) for x in re.findall(r'^cond4: .*? is cc4=(\d+)', t, re.M)}
    return cc8, cc4


COND8 = {'bc', 'bcd', 'cc', 'ccd', 'rc', 'rcd', 'xc'}
COND4 = {'saccd', 'srccd', 'strcd'}
MMR_FAMILY = {'ldm', 'stlm', 'stm', 'mvdm', 'mvmd', 'pshm', 'popm'}


def explain(gt, mt, w0, cc8, cc4):
    """label for a difference that is a reference-tool quirk or a reserved encoding, else None"""
    mn = mt.split()[0].lower() if mt.split() else ''
    g_ok = canon(gt) is not None
    if '??' in mt:
        return 'objdump prints ?? for a condition code that SPRU172C does not define'
    if mn in COND8 and not g_ok and (w0 & 0xff) not in cc8:
        return 'condition field is not a SPRU172C table A-2 combination (objdump accepts any bit pattern)'
    if mn in COND4 and not g_ok and (w0 & 0xf) not in cc4:
        return 'condition field is not one of the 12 conditions the conditional stores allow (SPRU172C)'
    if mn in ('banz', 'banzd') and not g_ok and (w0 & 0xf8) == 0xf8:
        return 'BANZ[D] *(lk): absolute addressing has no auxiliary register to test (manual: Sind), objdump accepts it'
    if mn in ('banz', 'banzd') and not g_ok and not (w0 & 0x80):
        return 'BANZ[D] with direct addressing: the manual allows only Sind (indirect), objdump accepts it'
    if mn in MMR_FAMILY and (w0 & 0x80):
        return 'objdump reads the I bit and mode bits as an MMR address; SPRU172C: I=1 is indirect addressing (page 0)'
    if mn == 'idle' and (w0 >> 8) & 3 == 3 and not g_ok:
        return 'IDLE with NN=11 is not defined (SPRU172C IDLE)'
    return None


def main():
    gh = [l.rstrip('\n').split(' ', 2) for l in open(sys.argv[1])]
    ob = [l.rstrip('\n').split(' ', 2) for l in open(sys.argv[2])]
    corpus = open(sys.argv[3], 'rb').read()
    cc8, cc4 = valid_conditions(sys.argv[4])
    show = int(sys.argv[sys.argv.index('--show') + 1]) if '--show' in sys.argv else 5
    assert len(gh) == len(ob), (len(gh), len(ob))
    cnt = Counter()
    ex = defaultdict(list)
    for (i, gl, gt), (j, ml, mt) in zip(gh, ob):
        g, m = canon(gt), canon(mt)
        w0 = int.from_bytes(corpus[int(i) * 16:int(i) * 16 + 2], 'big')
        if g is None and m is None:
            k = 'both invalid'
        elif g is None:
            k = 'objdump decodes, module rejects: ' + mt.split()[0]
        elif m is None:
            k = 'module decodes, objdump rejects: ' + gt.split()[0]
        elif int(gl) != int(ml):
            k = 'length differs: ' + mt.split()[0]
        else:
            k = 'agree' if g == m else 'text differs: ' + mt.split()[0]
        if k not in ('agree', 'both invalid'):
            e = explain(gt, mt, w0, cc8, cc4)
            if e:
                k = 'explained: ' + e
        cnt[k] += 1
        if len(ex[k]) < show:
            ex[k].append(f'slot {i}: module {gt!r}  objdump {mt!r}')
    tot = sum(cnt.values())
    for k, v in sorted(cnt.items(), key=lambda kv: -kv[1]):
        print(f'   {k:70s} {v:8d}  ({100 * v / tot:.3f}%)')
        if k not in ('agree', 'both invalid') and not k.startswith('explained'):
            for e in ex[k]:
                print('      ', e)
    bad = sum(v for k, v in cnt.items() if k not in ('agree', 'both invalid') and not k.startswith('explained'))
    print(f'   total {tot}, differences {bad}')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
