#!/usr/bin/env python3
"""Convert a TMS320C54x 16-bit boot table into a flat program-memory image for Ghidra.

  python c54x_boot.py firmware/PSR-500-600_DSP_v1.4_decrypted.bin -o dsp_prog.bin

The input is a decrypted DSP image: the 2-byte file prefix, then big-endian words. An optional
version word may precede the 0x08AA (16-bit) keyword. The header is SWWSR, BSCR, entry XPC,
entry PC, then blocks of (size, XPC, address, size words) ending with a zero size.

The output is 64K big-endian words (128 KB): program page 0 with every block placed at its
load address and unused words zero. Import it in Ghidra as Raw Binary with the
TMS320C54x:BE:16:default language at base address 0. A JSON summary of the blocks is printed.
"""
import argparse
import json
import struct
import sys


def parse(data):
    if len(data) % 2:
        data = data[:-1]
    w = struct.unpack(">%dH" % (len(data) // 2), data)
    i = next((k for k in range(min(4, len(w))) if w[k] == 0x08AA), None)
    if i is None:
        raise SystemExit("no 16-bit boot table keyword 0x08AA in the first words")
    hdr = {"version_word": "0x%04X" % w[0] if i else None, "swwsr": "0x%04X" % w[i + 1],
           "bscr": "0x%04X" % w[i + 2], "entry": "0x%X" % ((w[i + 3] << 16) | w[i + 4])}
    i += 5
    blocks = []
    while i < len(w) and w[i]:
        n, xpc, addr = w[i], w[i + 1], w[i + 2]
        blocks.append((xpc, addr, list(w[i + 3:i + 3 + n])))
        i += 3 + n
    return hdr, blocks


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("image", help="decrypted DSP image (with the 2-byte prefix)")
    ap.add_argument("-o", "--output", required=True, help="flat program image to write")
    ap.add_argument("--no-prefix", action="store_true", help="input has no 2-byte prefix")
    args = ap.parse_args(argv)

    raw = open(args.image, "rb").read()
    hdr, blocks = parse(raw if args.no_prefix else raw[2:])
    mem = [0] * 0x10000
    for xpc, addr, data in blocks:
        if xpc:
            raise SystemExit("block at XPC %d: only program page 0 is supported" % xpc)
        mem[addr:addr + len(data)] = data
    open(args.output, "wb").write(struct.pack(">65536H", *mem))
    hdr["blocks"] = [{"start": "0x%04X" % a, "end": "0x%04X" % (a + len(d) - 1), "words": len(d)}
                     for _, a, d in blocks]
    json.dump(hdr, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
