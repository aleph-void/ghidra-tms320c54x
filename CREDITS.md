# Credits

- Upstream: https://github.com/gabtremblay/ghidra-tms320c54x, commit 4581c53b50251c71acaa89f1f0c07b1ec9e346be
  ("Initial release for Ghidra 12.2", 2026-10-25), license Apache-2.0 (LICENSE).
- Original author: Gabriel Tremblay (@gabtremblay), the only commit author.
- Upstream's generator took the instruction encodings from the opcode table of GNU binutils
  (opcodes/tic54x-opc.c, GPL), as its docstring, per-line opcode/mask comments, README and NOTICE said. Ghidra-Rare
  replaced them with a clean-room table: `tools/c54x_encodings.py` was written from Texas Instruments' manuals only,
  SPRU172C (TMS320C54x DSP Reference Set Vol. 2, Mnemonic Instruction Set: chapter 4 opcode boxes, Table 1-2,
  Appendix A conditions, Appendix B status bits) and SPRU131G (Vol. 1, CPU and Peripherals: section 5.5 addressing
  fields, Table 3-3 memory-mapped registers), with the SPRU172C page of every form. `tools/fetch-ti-docs.sh` fetches
  both PDFs from ti.com pinned by SHA-256 (they are not redistributed). No binutils or other GPL source (opcode
  table, header, disassembler) was read; GNU objdump and gas were used only as black boxes, and only to compare
  against or to settle what the manuals leave open (the position of the long-offset word, see GHIDRA-RARE.md).
  The table was complete (and checked against an automatic extraction of the opcode boxes) before the generator's
  old patterns were opened; they were then only paired with table entries by mnemonic to rewrite the constructors.
  `make_slaspec.py` now generates every instruction pattern, and the condition/COND4/CMPR/MVMM subtables, from that
  table; the per-line binutils comments are removed. The earlier commits in this history still carry the
  binutils-derived encodings.
- Ghidra-Rare changes: see the commits on branch `ghidra-rare` and GHIDRA-RARE.md.
- Test tools: GNU binutils 2.45 (objdump `-m tms320c54x`, gas built for tic54x-coff) used as black boxes; TI manuals as references.
