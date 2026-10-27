# Credits

- Upstream: https://github.com/gabtremblay/ghidra-tms320c54x, commit 4581c53b50251c71acaa89f1f0c07b1ec9e346be
  ("Initial release for Ghidra 12.2", 2026-10-25), license Apache-2.0 (LICENSE).
- Original author: Gabriel Tremblay (@gabtremblay), the only commit author.
- Upstream states that the encodings in the SLEIGH spec were taken from the opcode table of GNU binutils
  (opcodes/tic54x-opc.c, GPL). Ghidra-Rare did not read that table; Ghidra-Rare's generator changes use only the TI manuals
  SPRU172C (instruction set) and SPRU131G (CPU and peripherals). The licensing of tables derived from GPL data is the
  upstream author's claim and is flagged to the maintainers.
- Ghidra-Rare changes: see the commits on branch `ghidra-rare` and GHIDRA-RARE.md.
- Test tools: GNU binutils 2.45 (objdump `-m tms320c54x`, gas built for tic54x-coff) used as black boxes; TI manuals as references.
