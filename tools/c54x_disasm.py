"""Reference decoder driven only by c54x_encodings.py (TI manuals): decode(words) -> (length, text) or None.

The text uses the GNU objdump spelling conventions (lower case, no spaces after commas) only so that the existing
display normaliser (test/compare.py canon) can compare it with the module and with objdump; nothing else is shared.
"""
from c54x_encodings import (ENCODINGS, SIGNED_K, IDLE_NN, CMPR_CC, MVMM_REG, COND8_CMP, SMEM_MOD, XMOD,
                            word_pattern, fixed_mask, fields, get)
from c54x_encodings import cond8 as _cond8, cond4 as _cond4

_ENTS = []
for mnem, syn, syntax, w0, ext, page in ENCODINGS:
    m, v = fixed_mask(w0)
    xs = [(x, fixed_mask(x) if x not in ('lk', 'pmad', 'dmad', 'PA', 'pmad_lo') else None,
           fields(x) if x not in ('lk', 'pmad', 'dmad', 'PA', 'pmad_lo') else None) for x in ext]
    _ENTS.append(dict(mnem=mnem, syn=syn, syntax=syntax, mask=m, val=v, f=fields(w0), ext=xs, page=page))


def sx(v, w):
    return v - (1 << w) if v & (1 << (w - 1)) else v


def cond8(c):
    r = _cond8(c)
    return None if r is None else [x.lower() for x in r]


def cond4(c):
    r = _cond4(c)
    return None if r is None else r.lower()


def ar(n):
    return 'ar%d' % n


def smem_text(ia, words, pos, kind):
    """ia = I(1) + A(7); returns (text, words used) or None"""
    i, a = ia >> 7, ia & 0x7f
    if not i:
        if kind == 'Sind':
            return None
        return (('0x%x' if kind == 'MMR' else '@0x%x') % a, 0)
    mod, arf = a >> 3, a & 7
    if kind == 'Sind' and mod == 15:
        return None
    if kind == 'MMR' and mod >= 12:
        return None             # SPRU131G Table 5-4 note: long-offset modes not allowed for MMR addressing
    s = SMEM_MOD[mod]
    if mod >= 12:
        if pos >= len(words):
            return None
        lk = words[pos]
        s = s.replace('ARx', ar(arf)).replace('lk', '0x%x' % lk)
        return (s.lower(), 1)
    return (s.replace('ARx', ar(arf)).lower(), 0)


def xmem_text(v):
    return XMOD[v >> 2].replace('ARx', ar(2 + (v & 3))).lower()


def decode(words):
    w0 = words[0]
    cands = [e for e in _ENTS if w0 & e['mask'] == e['val']]
    res = []
    for e in cands:
        r = _try(e, words)
        if r:
            res.append((e, r))
    if not res:
        return None
    if len(res) > 1:
        names = {e['mnem'] for e, _ in res}
        # RET[D] is RC[D] with the UNC condition: the dedicated mnemonic wins
        res = [x for x in res if x[0]['mnem'] != 'RC[D]'] if names == {'RC[D]', 'RET[D]'} else res
        assert len(res) == 1, [(e['mnem'], e['syn']) for e, _ in res]
    return res[0][1] + (res[0][0],)


def _try(e, words):
    f = e['f']
    w0 = words[0]
    val = {k: get(w0, v) for k, v in f.items()}
    pos = 1
    syntax = e['syntax']
    # Smem-like operand of word 0 (its long offset follows word 0)
    smem = None
    if 'I' in f:
        kind = 'Sind' if 'Sind' in syntax else 'MMR' if 'MMR' in syntax else 'Lmem' if 'Lmem' in syntax else 'Smem'
        r = smem_text((val['I'] << 7) | val['A'], words, pos, kind)
        if r is None:
            return None
        smem, used = r
        pos += used
    ext = {}
    for x, fm, ff in e['ext']:
        if pos >= len(words):
            return None
        w = words[pos]
        pos += 1
        if fm is None:
            ext[x] = w
        else:
            if w & fm[0] != fm[1]:
                return None
            for k, v in ff.items():
                val[k] = get(w, v)
    mn = e['mnem']
    if '[D]' in mn:
        mn = mn.replace('[D]', 'D' if val.get('Z') else '')
    if '[R]' in mn:
        mn = mn.replace('[R]', 'R' if val.get('R') else '')
    acc = lambda b: 'ab'[b]
    ops = []
    if mn.startswith('LD||') or mn.startswith('ST||'):
        first, second = mn.split('||')
        x, y = xmem_text(val['X']), xmem_text(val['Y'])
        if first == 'LD':
            d = val['D']
            return (pos, 'ld %s,%s || %s %s,%s' % (x, acc(d), second.lower(), y, acc(1 - d)))
        s = acc(val['S'])
        dst = 't' if 'Xmem, T' in syntax else acc(val['D'])
        return (pos, 'st %s,%s || %s %s,%s' % (s, y, second.lower(), x, dst))
    syn_ops = syntax.split(' ', 1)[1] if ' ' in syntax else ''
    toks = [t.strip(' []') for t in syn_ops.replace('[', ',').replace(']', '').split(',')]
    toks = [t for t in toks if t]
    for t in toks:
        if t in ('Smem', 'Lmem', 'Sind', 'MMR'):
            ops.append(smem)
        elif t == 'Xmem':
            ops.append(xmem_text(val['X']))
        elif t == 'Ymem':
            ops.append(xmem_text(val['Y']))
        elif t == 'src':
            ops.append(acc(val['S']))
        elif t == 'dst':
            ops.append(acc(val['D']) if 'D' in val else acc(val['S']))
        elif t in ('#lk', 'lk'):
            ops.append('#0x%x' % ext['lk'])
        elif t == 'pmad':
            ops.append('0x%x' % ext['pmad'])
        elif t == 'dmad':
            ops.append('0x%x' % ext['dmad'])
        elif t == 'PA':
            ops.append('0x%x' % ext['PA'])
        elif t == 'extpmad':
            ops.append('0x%x' % (val['G'] << 16 | ext['pmad_lo']))
        elif t == 'SHIFT':
            ops.append('%d' % sx(val['H'], 5))
        elif t == 'SHFT':
            ops.append('%d' % val['F'])
        elif t in ('16', 'TS', 'ASM', 'T', 'TRN', 'DP', 'ARP', 'A', 'B'):
            ops.append(t.lower())
        elif t in ('#K', 'K', '#k9', '#k5', '#k3'):
            if mn == 'IDLE':
                if val['Q'] not in IDLE_NN:
                    return None
                ops.append('%d' % IDLE_NN[val['Q']])
            else:
                lo, w = f['K']
                k = sx(val['K'], w) if (e['mnem'], e['syn']) in SIGNED_K else val['K']
                ops.append(('#' if t.startswith('#') else '') + '%d' % k)
        elif t == 'BITC':
            ops.append('%d' % val['B'])
        elif t == 'N':
            ops.append('%d' % val['N'])
        elif t == 'SBIT':
            ops.append('%d' % val['T'])
        elif t == 'n':
            ops.append('%d' % (val['N'] + 1))
        elif t == 'CC':
            ops.append(CMPR_CC[val['V']].lower())
        elif t == 'ARx':
            ops.append(ar(val['P']))
        elif t in ('MMRx', 'MMRy'):
            r = val['M' if t == 'MMRx' else 'W']
            if r >= len(MVMM_REG):
                return None
            ops.append(MVMM_REG[r].lower())
        elif t == 'cond':
            if 'O' in val:
                c = cond4(val['O'])
                if c is None:
                    return None
                ops.append(c)
            else:
                c = cond8(val['C'])
                if c is None:
                    return None
                ops.extend(c)
                break
        elif t == 'dst_':
            pass
        else:
            raise ValueError((e['mnem'], t))
    return (pos, (mn.lower() + ' ' + ','.join(ops)).strip())
