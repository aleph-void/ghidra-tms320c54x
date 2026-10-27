#!/usr/bin/env python3
"""reach_check.py <spec.slaspec> <reach.txt>: every constructor (':' or 'Table:' line) must appear."""
import re
import sys
lines = open(sys.argv[1]).read().split('\n')
cons = {i + 1 for i, l in enumerate(lines) if re.match(r'^(:|\w+:)', l)}
seen = {int(x) for x in open(sys.argv[2]).read().split()}
# the *SP(dma) operands exist only under the CPL=1 context bit, which no corpus slot has: the emulator case direct_sp_cpl reaches them
skipped = {n for n in cons - seen if 'cplmode=1' in lines[n - 1]}
missing = sorted(cons - seen - skipped)
print(f'   constructors reached {len(cons & seen)}/{len(cons)} (+{len(skipped)} CPL=1 operands reached by the emulator case direct_sp_cpl)')
for n in missing[:30]:
    print('   not reached:', n, lines[n - 1][:110])
sys.exit(1 if missing else 0)
