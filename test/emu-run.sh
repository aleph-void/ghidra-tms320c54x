#!/usr/bin/env bash
# emu-run.sh <workdir>: build the emulator cases and run them; prints the result file, exit 1 on any failure
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
W=$(readlink -m "${1:?workdir}")
mkdir -p "$W"
python3 "$HERE/emu_tests.py" "$W"
"$HERE/ghidra-script.sh" raw "${LANG_ID:-TMS320C54x:BE:16:default}" "$W/emu.bin" EmuCheck.java "$W/tests.txt" "$W/emu-results.txt"
cat "$W/emu-results.txt" | grep -v '^PASS' || true
tail -1 "$W/emu-results.txt"
! grep -q '^FAIL' "$W/emu-results.txt"
