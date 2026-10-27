# Ghidra-Rare notes: TMS320C54x

Language `TMS320C54x:BE:16:default` (unchanged from upstream). Source of truth: `make_slaspec.py` (the .slaspec is generated and checked in;
the .sla is built by Ghidra and not tracked). Credits: CREDITS.md. Tests: `test/run-tests.sh [workdir] [--real]`.

## Results (Ghidra 12.1.3 for the runs; compile also checked on 12.1.4 and 12.2 by the release build)

| Area | Result |
|---|---|
| Build | .slaspec compiles on 12.1.3, 12.1.4, 12.2; .sla about 40 KB |
| Decode | vs GNU objdump 2.45 `-m tms320c54x`, 418,592 slots (every first word x 4 following-word patterns, 100,000 random, 56,448 for the 0x6Fxx family): 359,501 agree after display normalisation, 47,437 both invalid, 11,654 explained (below), 0 unexplained |
| Assembler round trip | module text re-assembled by gas (tic54x): of 6,000 sampled instructions 5,808 identical words, 99 differ only in the unused ARx field of `*(lk)`, 26 another encoding of the same instruction (SHIFT=0 forms), 2 differ, the rest rejected by gas (far mode, MMR range) |
| Every entry | 676/678 constructors reached by the decode corpora; the other two (`*SP(dma)` operands, context CPL=1) are reached by the emulator case `direct_sp_cpl` |
| Semantics | 93 emulator cases pass (Ghidra EmulatorHelper), 1 deliberately wrong expectation is detected (`XFAIL_add_wrong`); expectations from the SPRU172C/SPRU131G examples (ADD, ADDC, NEG, ABS, SAT, SUBB, SUBC, MAX, SFTA, ROL, ROR, LD\|\|MAC, ST\|\|ADD, ST\|\|SUB, bit-reversed sequence, circular rules) and hand-computed cases (flags, OVM/SXM, dual 16-bit, RPT loops, ST0/ST1, far call/return, delayed call/return, conditions) |
| Real code | no freely licensed third-party C54x binary was found; two programs written for the tests (`test/real/*.asm`, Apache-2.0) assembled with gas: 115 instructions, 13 functions, 0 bad-instruction/error bookmarks, 0 decompile failures, all 115 instructions identical to objdump |

Explained difference classes (all against SPRU172C / SPRU131G): condition fields that are not a table A-2 combination (objdump accepts any bit pattern);
objdump prints `??` for undefined 4-bit conditions; BANZ with direct or absolute addressing (only Sind is defined); MMR instructions with I=1
(objdump reads the mode bits as an MMR address, the manual says they are indirect addressing of page 0; gas encodes them the module's way); IDLE NN=11.

## Bugs fixed in the module (all found by these tests)
0x6Fxx three-word forms (ADD/SUB/LD/STH/STL Smem,SHIFT) with a long-offset Smem did not decode when the offset word looked like an extension word: the S and L forms shared a root pattern that the decision tree could not separate; they now have disjoint word-0 patterns (`ind=0 | mod<12` versus `ind=1 & mod>=12`).
Wrong IDLE 2/3 encodings; BIO/NBIO polarity inverted (SPRU172C: BIO means the pin is low); MAX/MIN carry inverted; SUBC without carry; no carry/overflow/saturation/SXM
handling anywhere; R-suffix rounding did not clear bits 15-0; DADST/DSADT/DSUBT used T instead of T:T and had no dual 16-bit mode; parallel ST||ADD/SUB used the wrong
accumulator and did not apply ASM; return addresses pushed as byte offsets (and +2 too far for delayed calls); FCALL/FRET did not handle XPC; ASM stored zero-extended;
circular and bit-reversed addressing approximated; MMR instructions only decoded the direct form; ST0/ST1 were dead registers; PORTR/PORTW operands printed with a PA prefix;
SACCD/SRCCD/STRCD accepted the undefined UNC condition; FIRS/LMS/ABDST/SQDST/POLY/EXP/NORM/SAT/CMPS were pcodeops.

## Confirmed reference-tool bugs (binutils 2.45 objdump -m tms320c54x)
MMR instructions (LDM, STLM, STM, MVDM, MVMD, PSHM, POPM) with I=1 are shown as an MMR address although they are indirect addressing (the same binutils's gas encodes them as indirect).
Everything else in the "explained" list is leniency about reserved encodings.

## Doesn't work
- RPTB/RPTBD loop-back (hardware address comparator); `LD @n` style accesses to data 0x00-0x1F do not alias the CPU registers (registers live in Ghidra's register space; SLEIGH cannot overlay register space on a RAM space); ST1 writes do not change the CPL context bit.
- Compatibility mode (CMPT=1, ARP updates) and extended program space (XPC pages beyond 64K words) are not modelled. The ELF/COFF loader opinion is absent (TI COFF for C54x stores little-endian words).

## Unverified
Only the manuals and objdump/gas (same opcode table as the upstream generator) were available: there is no independent C54x simulator, no TI toolchain, no real third-party code. Peripheral map in the pspec (C5402/C5409/C5416) and the cspec calling convention are upstream's, untested.
