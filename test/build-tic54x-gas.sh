#!/usr/bin/env bash
# Build GNU as for tic54x-coff from the binutils 2.45 release tarball (black box assembler for the tests; its source is not read).
#   build-tic54x-gas.sh <prefix>      then: export PATH=<prefix>/bin:$PATH
set -euo pipefail
P=$(readlink -m "$1"); D=$(mktemp -d); cd "$D"
curl -sL https://ftp.gnu.org/gnu/binutils/binutils-2.45.tar.xz -o b.tar.xz
tar xf b.tar.xz; mkdir build; cd build
../binutils-2.45/configure --target=tic54x-coff --disable-nls --disable-gdb --disable-sim --disable-gprof --disable-ld --disable-gold --disable-binutils --prefix="$P"
make -j"$(nproc)" all-gas && make -C gas install
