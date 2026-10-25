# TMS320C54x: Ghidra language for TI C54x DSPs

A Ghidra 12.2 extension that adds the language **`TMS320C54x:BE:16:default`** (stock Ghidra has no
C54x support), plus scripts to import a C54x boot table and find code that flow analysis misses.
It was made for the GRE PSR-500/600 DSP firmware but covers the whole C54x instruction set.

## What's in it

- `data/languages/TMS320C54x.slaspec`: the instruction spec, **generated** by `make_slaspec.py`
  from the encodings in GNU binutils' `opcodes/tic54x-opc.c` (213 instruction forms plus the 13
  parallel forms, 67 condition-code combinations, every status bit, the memory-mapped registers).
- Word-addressed `prog`, `data` and `io` spaces (16-bit big-endian words). Accumulators A/B are
  40-bit values in 64-bit registers with `AL`/`AH`/`AG` views; status bits are separate registers.
- Direct addressing follows `CPL`: after `SSBX CPL` the operands read `*SP(n)`, after `RSBX CPL`
  `@n` (DP-relative). The setting flows with the code through a context bit.
- `TMS320C54x.pspec`: CPU memory-mapped registers (data 0x00-0x1F) and the C5402/C5409/C5416
  peripheral map (McBSP0-2, timer, wait states, HPI, GPIO, DMA, clock), labelled in data space.
- `TMS320C54x.cspec`: TI C compiler conventions (first argument and result in A, stack arguments,
  one-word return address, AR1/AR6/AR7 preserved).
- Scripts (Script Manager, category **C54x**):
  - `C54xImportBootImage`: imports a 16-bit boot table (`0x08AA` keyword, optionally after a
    version word and a 2-byte file prefix) as a new program. Each block goes to program space, and
    blocks in on-chip RAM (0x0080-0x7FFF) are mirrored into data space for the OVLY=1 overlay.
  - `C54xSeedFunctions`: names the interrupt handlers in the vector table and tries every raw
    `CALL`/`CALLD` target, keeping only those that disassemble without errors.
- `c54x_boot.py`: converts a boot table to a flat 64K-word program image, for other tools.

## Validation

On the PSR-500/600 DSP firmware the spec decodes 7,217 instructions (75 different mnemonics,
81% of the image). An independent decoder built straight from the binutils table agrees on
**every** instruction's mnemonic and length. Instruction forms this firmware doesn't use come from
the same table but haven't been exercised against real code.

## Modelling limits

- RPT/RPTB/RPTZ only set the repeat registers; the decompiler doesn't model the repetition.
- Loads into an accumulator sign-extend (SXM=1). OVM saturation, rounding details, circular and
  bit-reversed addressing are simplified. FIRS, LMS, ABDST, SQDST, POLY, EXP, NORM, SAT and CMPS
  appear as named operations (`firs(...)`) rather than arithmetic.
- Far branches/calls (FB, FCALL, ...) ignore the 7-bit page: program space is 64K words.
- `XC` skips the next 1 or 2 words when its condition is false (modelled as a conditional branch).
- Ghidra prefixes instructions that sit in a delay slot with `_` (e.g. `_LD`).

## Install

Copy this folder to `%APPDATA%\ghidra\ghidra_12.2_PUBLIC\Extensions\TMS320C54x`, or zip it with
the folder named `TMS320C54x` at the top and use **File → Install Extensions → +**. Restart Ghidra.
Headless `-processor` checks languages before it loads user extensions, so for headless work run
`C54xImportBootImage` as a post-script on any program; it creates the C54x program itself.

## Use

1. Open any program (or none) and run **C54xImportBootImage**; choose the decrypted boot-table file.
2. Open the new program, run **C54xSeedFunctions**, then **Analysis → Auto Analyze**.

## Regenerate

`python make_slaspec.py` rewrites the `.slaspec`; Ghidra recompiles it on the next start (or run
`support/sleigh.bat data/languages/TMS320C54x.slaspec`).

## License

Apache License 2.0, see [LICENSE](LICENSE). [NOTICE](NOTICE) lists what is derived from other projects.
