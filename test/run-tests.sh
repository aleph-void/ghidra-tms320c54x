#!/usr/bin/env bash
# TMS320C54x module test suite.
#   GHIDRA_INSTALL_DIR=<scratch Ghidra 12.1.x with this module symlinked at Ghidra/Processors/TMS320C54x> test/run-tests.sh [workdir] [--real]
# Needs: GNU binutils objdump built with -m tms320c54x (OBJDUMP), tic54x-coff-as (TIC54X_AS, binutils 2.45 configured with
# --target=tic54x-coff, gas only), PROJ_DIR (a path without a dot component).
# 1. generator reproduces the checked-in .slaspec; the spec compiles (.sla < 16 MB)
# 2. decode differential vs objdump (compare.py) on 418,592 slots, 0 unexplained differences required
# 2b. the same slots decoded by the clean-room table (cleanroom_diff.py): module must agree everywhere, objdump
#     differences must be in known buckets; 2c (C54X_DOCS set, needs pdftotext): table vs the manual's opcode boxes
# 3. every constructor reached (reach_check.py)
# 4. as round trip of the module's own text (asm_roundtrip.py, informational counts)
# 5. emulator cases incl. a deliberately wrong expectation (emu-run.sh)
# --real: assembled programs through headless import/analysis/decompile (real-binaries.sh)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); MOD=$(cd "$HERE/.." && pwd)
: "${GHIDRA_INSTALL_DIR:?}"; : "${OBJDUMP:?}"
REAL=0; ARGS=(); for a in "$@"; do [[ $a == --real ]] && REAL=1 || ARGS+=("$a"); done
W=$(readlink -m "${ARGS[0]:-${TMPDIR:-/tmp}/c54x-tests}"); mkdir -p "$W"; export TMPDIR=$W PROJ_DIR=${PROJ_DIR:-$W}
L=TMS320C54x:BE:16:default
echo "== 1. generator + compile"
C54X_OUT="$W/regen.slaspec" python3 "$MOD/make_slaspec.py" >/dev/null; cmp "$W/regen.slaspec" "$MOD/data/languages/TMS320C54x.slaspec"
"$GHIDRA_INSTALL_DIR/support/sleigh" -a "$MOD/data/languages" 2>&1 | grep -E "^ERROR|^Error" && exit 1 || true
sz=$(stat -c %s "$MOD/data/languages/TMS320C54x.sla"); echo "   .sla $sz bytes"; ((sz < 16*1024*1024))
echo "== 2. decode differential vs objdump"
python3 "$HERE/gen_corpus.py" "$W/all.bin" 100000 7
python3 "$HERE/objdump_stream.py" "$W/all.bin" "$W/obj.txt"
JOBS=${JOBS:-4} "$HERE/decode-corpus.sh" $L "$W/all.bin" "$W/gh.txt" 16
python3 "$HERE/compare.py" "$W/gh.txt" "$W/obj.txt" "$W/all.bin" "$MOD/data/languages/TMS320C54x.slaspec" --show 3 | tee "$W/compare.txt"
echo "== 2b. clean-room encoding table (tools/c54x_encodings.py) vs module and objdump"
python3 "$HERE/cleanroom_diff.py" "$W/all.bin" "$W/gh.txt" "$W/obj.txt" | tee "$W/cleanroom.txt"
if [[ -n ${C54X_DOCS:-} ]]; then
	echo "== 2c. table transcription vs the SPRU172C opcode boxes (C54X_DOCS: directory for the TI PDFs)"
	"$MOD/tools/fetch-ti-docs.sh" "$C54X_DOCS"
	pdftotext -layout "$C54X_DOCS/spru172c.pdf" "$W/spru172c.txt"
	python3 "$MOD/tools/extract_opcode_boxes.py" "$W/spru172c.txt" "$W/boxes.json"
	python3 "$MOD/tools/check_transcription.py" "$MOD/tools" "$W/boxes.json" | tee "$W/transcription.txt"
	grep -q "problems 1$" "$W/transcription.txt"     # the one known difference: XORM's box omits its constant word
fi
echo "== 3. every constructor reached"
JOBS=${JOBS:-4} "$HERE/decode-corpus.sh" $L "$W/all.bin" "$W/reach.txt" 16 Reach.java
python3 "$HERE/reach_check.py" "$MOD/data/languages/TMS320C54x.slaspec" "$W/reach.txt"
echo "== 4. assembler round trip"
python3 "$HERE/asm_roundtrip.py" "$W/gh.txt" "$W/obj.txt" "$W/all.bin" 6000 1 | head -20
echo "== 5. emulator cases"
"$HERE/emu-run.sh" "$W/emu"
if ((REAL)); then echo "== real code"; "$HERE/real-binaries.sh" "$W"; fi
echo "all checks passed"
