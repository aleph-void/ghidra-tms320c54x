#!/usr/bin/env bash
# Fetch the TI manuals the encoding table (tools/c54x_encodings.py) was transcribed from, pinned by SHA-256.
# The PDFs are TI's and are not redistributed here.     tools/fetch-ti-docs.sh <dir>
set -euo pipefail
D=${1:?usage: fetch-ti-docs.sh <dir>}; mkdir -p "$D"
fetch() { # name sha256
	local f="$D/$1.pdf"
	[[ -f $f ]] || curl -fsSL -A 'Mozilla/5.0' -o "$f" "https://www.ti.com/lit/ug/$1/$1.pdf"
	echo "$2  $f" | sha256sum -c -
}
fetch spru172c c4f89ce4a774a76de1d93a2413e882a71b82d236fc2c52af63f3159368a37e75   # Vol. 2 Mnemonic Instruction Set
fetch spru131g d9ea0e695859d605d1f94dabeede327c0e343099102cfd7e224f6f53375a3fa2   # Vol. 1 CPU and Peripherals
