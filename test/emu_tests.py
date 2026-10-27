#!/usr/bin/env python3
"""Assemble the TMS320C54x p-code test cases of emu_cases.py (GNU as, tic54x-coff target, used only as an
assembler) into emu.bin (big-endian 16-bit words, program space word address 0) and tests.txt for EmuCheck.java.

  emu_tests.py <workdir>          environment: TIC54X_AS (default: tic54x-coff-as on PATH), OBJDUMP
"""
import os
import re
import shutil
import subprocess
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emu_cases  # noqa: E402

BASE = 0x100
STRIDE = 0x40
AS = os.environ.get('TIC54X_AS') or shutil.which('tic54x-coff-as')
OBJ = os.environ.get('OBJDUMP') or shutil.which('objdump')


def assemble(work, n, asm):
    src = os.path.join(work, f'c{n}.asm')
    off = BASE + n * STRIDE
    lines = [' .text'] + [' nop'] * off + [l for l in asm.split('\n')] + ['_end_:', ' nop']
    open(src, 'w').write('\n'.join(lines) + '\n')
    r = subprocess.run([AS, src, '-o', src + '.o'], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f'case {n} {emu_cases.CASES[n][0]}: {r.stderr}')
    d = subprocess.run([OBJ, '-d', src + '.o'], capture_output=True, text=True).stdout
    words = []
    for l in d.split('\n'):
        m = re.match(r'^\s*([0-9a-f]+):\t((?:[0-9a-f]{4} )+)', l)
        if m:
            words += [int(x, 16) for x in m.group(2).split()]
    os.remove(src)
    os.remove(src + '.o')
    return words[off:]


def conv(items):
    """test item list: registers in hex; data#2:addr=val -> data#2:addr=val (EmuCheck syntax)"""
    return items if items else '-'


def main():
    work = os.path.abspath(sys.argv[1])
    os.makedirs(work, exist_ok=True)
    image = {}
    tests = []
    for n, (name, asm, init, expect) in enumerate(emu_cases.CASES):
        words = assemble(work, n, asm)
        start = BASE + n * STRIDE
        assert len(words) <= STRIDE, (name, len(words))
        for i, w in enumerate(words):
            image[start + i] = w
        stop = start + len(words) - 1       # the trailing nop of the case
        tests.append(f'{name} {start:x} {stop:x} {conv(init)} {conv(expect)}')
    top = max(image) + 1
    buf = bytearray(top * 2)
    for a, w in image.items():
        buf[a * 2:a * 2 + 2] = struct.pack('>H', w)
    open(os.path.join(work, 'emu.bin'), 'wb').write(buf)
    open(os.path.join(work, 'tests.txt'), 'w').write('\n'.join(tests) + '\n')
    print(len(tests), 'cases,', top, 'words')


if __name__ == '__main__':
    main()
