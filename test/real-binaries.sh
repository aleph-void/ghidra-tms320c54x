#!/usr/bin/env bash
# Real-code check: assemble test/real/*.asm with GNU as (tic54x-coff, built from binutils 2.45), import each as a raw
# program, create functions at the global labels, analyse, decompile; compare the listing with objdump at the same addresses.
#   real-binaries.sh <workdir>
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
W=$(readlink -m "$1"); mkdir -p "$W/real"
L=${LANG_ID:-TMS320C54x:BE:16:default}
for p in fir fftbr; do
  python3 "$HERE/asm2bin.py" "$HERE/real/$p.asm" "$W/real/$p"
  "$HERE/ghidra-script.sh" raw "$L" "$W/real/$p.bin" RealCheck.java "$W/real/$p.sum" "$W/real/$p.gh" 50 "$W/real/$p.entries" analyze
  cat "$W/real/$p.sum"
  python3 "$HERE/real_compare.py" "$W/real/$p.gh" "$W/real/$p.lst"
done
