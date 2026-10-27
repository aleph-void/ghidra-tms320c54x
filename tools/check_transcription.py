#!/usr/bin/env python3
"""Cross-check the hand-typed table (c54x_encodings.py) against extract_opcode_boxes.py output, and list the encodings
that overlap (expected: the 0x6Fxx family, told apart by its second word; BC/FB and CC/FCALL, told apart by bit 7;
RC UNC = RET).   check_transcription.py <tools dir> <boxes.json>"""
import json, sys, itertools
sys.path.insert(0, sys.argv[1])
from c54x_encodings import ENCODINGS, word_pattern, fixed_mask
raw = json.load(open(sys.argv[2]))
def norm(p):  # compare only fixed bits; field letters differ between the manual and this table
    return ''.join(c if c in '01' else '.' for c in p)
rawset = {}
for e in raw:
    w = e['words'][0]
    if w.startswith('RAW:'):
        toks = w[4:].split()
        w = ''.join(toks[:9]) + 'GGGGGGG'   # FB/FCALL: 9 bits then the 7-bit pmad field
    rawset.setdefault((e['page'], norm(w)), e)
bad = 0
seen = set()
for m, syn, s, w0, ext, page in ENCODINGS:
    k = (page, norm(word_pattern(w0)))
    if k not in rawset:
        print('NO MATCH IN EXTRACTION', m, syn, w0, page); bad += 1; continue
    seen.add(k)
    e = rawset[k]
    rawext = e['words'][1:]
    rext = ['lk' if 'constant' in x or 'Port address' in x else norm(x) for x in rawext if x != 'RAW:Opcode']
    mext = ['lk' if x in ('lk', 'pmad', 'dmad', 'PA', 'pmad_lo') else norm(word_pattern(x)) for x in ext]
    if rext != mext:
        print('EXT DIFF', m, syn, page, ext, rawext); bad += 1
for k, e in rawset.items():
    if k not in seen: print('EXTRACTED BUT NOT IN TABLE', k, e['syntax']); bad += 1
# overlaps between distinct entries (word 0 only; ext-word-discriminated forms reported separately)
ents = [(m, syn, fixed_mask(w0), ext) for m, syn, s, w0, ext, page in ENCODINGS]
for a, b in itertools.combinations(ents, 2):
    (ma, va), (mb, vb) = a[2], b[2]
    if (va ^ vb) & ma & mb == 0:
        print('OVERLAP', a[0], a[1], b[0], b[1], 'ext:', a[3], b[3])
print('entries', len(ENCODINGS), 'extracted', len(rawset), 'problems', bad)
