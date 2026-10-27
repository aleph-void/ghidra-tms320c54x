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

Status after the Ghidra-Rare verification (details and numbers: [GHIDRA-RARE.md](GHIDRA-RARE.md); prebuilt zips for Ghidra 12.1.3, 12.1.4 and 12.2 are on the fork's Releases page):

- RPT/RPTZ: **fixed**. The repeated instruction is inlined by `delayslot()` in a p-code loop that runs it RC+1 times. RPTB/RPTBD: **remains**: the loop-back at the end address (REA) is done by an address comparator, not by an instruction, so no constructor can express it; RSA/REA/BRAF are set.
- Accumulator results: **fixed**. ADD/SUB/NEG/ABS/MAC... wrap to 40 bits, set OVA/OVB, saturate to 32 bits with OVM=1, honour SXM, and set C as in SPRU131G table 4-1; rounding (R suffix) clears bits 15-0. FIRS, LMS, ABDST, SQDST, POLY, EXP, NORM, SAT, CMPS are real p-code (no more pcodeops).
- Circular (BK) and bit-reversed (AR0, reverse carry) addressing: **fixed** (SPRU131G 5.5.3.4 / 5.5.3.5; the manual's bit-reversed example is a test).
- Far branches/calls/returns: **fixed**: the 7-bit page is shown (`FB 0x2:0x1234`), written to XPC, and FCALL/FRET push/pop XPC and the return address.
- XC is a conditional branch over the next 1 or 2 words (correct); delay-slot instructions are prefixed `_` by Ghidra.
- ST0/ST1: **fixed for direct PSHM/POPM/LDM/STLM/STM/MVDM/MVMD**: the registers are assembled from / split into the flag registers. **Remains**: data memory 0x00-0x1F is not aliased to the CPU registers for ordinary data accesses (e.g. `LD @6,A`), and a write to ST1 does not change the CPL context bit the listing uses.
- Dual 16-bit mode (C16=1) of DADD/DSUB/DRSUB/DADST/DSADT/DSUBT: **fixed** (the C16=0 forms of DADST/DSADT/DSUBT had the wrong operand and are corrected).
- Parallel ST||ADD/SUB/LD/MAC...: **fixed** (store of src << (ASM-16); ST||ADD/SUB use the other accumulator).
- IDLE K encodings, BIO condition polarity, MAX/MIN carry, SUBC carry, indirect addressing of the MMR instructions: **fixed** (see GHIDRA-RARE.md).
- **Remains**: 3-word 0x6Fxx forms (ADD/SUB/LD/STH/STL Smem,SHIFT) with a long-offset/absolute Smem do not decode when the offset word lies in 0x0C00-0x0FFF (cause not found in the SLEIGH decision tree); compatibility mode (CMPT=1, ARP updates) is not modelled; XPC-extended program space beyond 64K words is not modelled.

## Install

Copy this folder to `%APPDATA%\ghidra\ghidra_12.2_PUBLIC\Extensions\TMS320C54x`, or zip it with
the folder named `TMS320C54x` at the top and use **File → Install Extensions → +**. Restart Ghidra.
Headless `-processor` checks languages before it loads user extensions, so for headless work run
`C54xImportBootImage` as a post-script on any program; it creates the C54x program itself.

## Use

1. Open any program (or none) and run **C54xImportBootImage**; choose the decrypted boot-table file.
2. Open the new program, run **C54xSeedFunctions**, then **Analysis → Auto Analyze**.

## Tests

`test/run-tests.sh` (see its header); results in [GHIDRA-RARE.md](GHIDRA-RARE.md).

## Regenerate

`python make_slaspec.py` rewrites the `.slaspec`; Ghidra recompiles it on the next start (or run
`support/sleigh.bat data/languages/TMS320C54x.slaspec`).

## License

Apache License 2.0, see [LICENSE](LICENSE). [NOTICE](NOTICE) lists what is derived from other projects.
