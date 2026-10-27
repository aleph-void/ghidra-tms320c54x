# Ghidra-Rare notes: TMS320C54x

Language `TMS320C54x:BE:16:default` (unchanged from upstream). Source of truth: `make_slaspec.py` (the .slaspec is generated and checked in;
the .sla is built by Ghidra and not tracked). Instruction encodings: `tools/c54x_encodings.py` (clean-room, from the TI manuals, see below).
Credits: CREDITS.md. Tests: `test/run-tests.sh [workdir] [--real]` (set `C54X_DOCS=<dir>` to also check the table against the manual's opcode boxes).

## Encoding provenance (clean-room)
Upstream took its encodings from GNU binutils' GPL opcode table, which also made the objdump/gas comparison circular. Ghidra-Rare
re-derived every encoding from SPRU172C (chapter 4 opcode boxes, Table 1-2, Appendices A and B) and SPRU131G (5.5 addressing fields,
Table 3-3) without reading any binutils source, and the module's patterns are now generated from that table (`tools/c54x_encodings.py`,
SPRU172C page per form; PDFs fetched by `tools/fetch-ti-docs.sh`, pinned by SHA-256, not redistributed).
- Transcription check: an automatic extraction of the 193 opcode boxes from the PDF text matches the hand-typed table on all 193 forms.
  XORM's box (4-203) prints only word 0; the same page's Operands (lk) and Words (2 words) give the constant word, so the table has it.
- One fact the manuals leave open: where the long-offset/absolute Smem word sits relative to an instruction's own extension word.
  Settled with gas as a black box: directly after word 0 (`ADD *AR1(5),3,B,A` = 6FE1 0005 0C03, `ADDM #1234h,*(55h)` = 6BF8 0055 1234).
- Diff of the table (`tools/c54x_disasm.py`) against the module before regeneration, 418,592 slots: 360,112 agree, 57,493 both invalid,
  987 different, all module issues: 981 MVMM with a register field 9-15 (module bug, fixed) and 6 ESTOP (F4F0, not in either manual;
  dropped). Transcription errors found: 0. Manual errata needed: 0.
- Diff of the table against objdump (black box), same slots: 358,514 agree, 47,437 both invalid, and 12,641 differences, every one in
  a bucket: reserved encodings objdump accepts (8-bit conditions that are no Table A-2 combination 5,554; 4-bit conditions outside the
  SACCD/SRCCD/STRCD table 1,399; BANZ with direct or `*(lk)` Sind 1,501; MMR operands in long-offset/absolute modes 1,598; MVMM
  registers 9-15 981; IDLE NN=11 4), an objdump display bug (MMR operand with I=1, 1,598: SPRU131G says indirect and gas encodes
  `STLM A,*AR3+` as 8893, which objdump shows as `stlm a,ar3`), and ESTOP (6, objdump only).
- After regeneration the module decodes every slot exactly as before except ESTOP; with the MVMM fix it agrees with the table on all
  418,592 slots (`test/cleanroom_diff.py`, part of run-tests.sh: 360,112 agree, 58,480 both invalid, 0 different).

## Results (Ghidra 12.1.3 for the runs; compile also checked on 12.1.4 and 12.2 by the release build)

| Area | Result |
|---|---|
| Build | .slaspec compiles on 12.1.3, 12.1.4, 12.2 (release zips built with Ghidra-Rare's tools/build-module.sh for all three); .sla about 48 KB |
| Clean-room table | module = table on all 418,592 slots (0 different); table vs objdump 0 unexplained (buckets above) |
| Decode | vs GNU objdump 2.45 `-m tms320c54x`, 418,592 slots (every first word x 4 following-word patterns, 100,000 random, 56,448 for the 0x6Fxx family): 358,514 agree after display normalisation, 47,437 both invalid, 12,641 explained (below), 0 unexplained |
| Assembler round trip | module text re-assembled by gas (tic54x): of 6,000 sampled instructions 5,835 identical words, 91 differ only in the unused ARx field of `*(lk)`, 25 another encoding of the same instruction (SHIFT=0 forms), 0 differ, 49 rejected by gas (far mode) |
| Every entry | 661/663 constructors reached by the decode corpora; the other two (`*SP(dma)` operands, context CPL=1) are reached by the emulator case `direct_sp_cpl` |
| Semantics | 93 emulator cases pass (Ghidra EmulatorHelper), 1 deliberately wrong expectation is detected (`XFAIL_add_wrong`); expectations from the SPRU172C/SPRU131G examples (ADD, ADDC, NEG, ABS, SAT, SUBB, SUBC, MAX, SFTA, ROL, ROR, LD\|\|MAC, ST\|\|ADD, ST\|\|SUB, bit-reversed sequence, circular rules) and hand-computed cases (flags, OVM/SXM, dual 16-bit, RPT loops, ST0/ST1, far call/return, delayed call/return, conditions) |
| Real code | no freely licensed third-party C54x binary was found; two programs written for the tests (`test/real/*.asm`, Apache-2.0) assembled with gas: 115 instructions, 13 functions, 0 bad-instruction/error bookmarks, 0 decompile failures, all 115 instructions identical to objdump |

Explained difference classes (all against SPRU172C / SPRU131G): condition fields that are not a table A-2 combination (objdump accepts any bit pattern);
objdump prints `??` for undefined 4-bit conditions; BANZ with direct or absolute addressing (only Sind is defined); MMR instructions with I=1
(objdump reads the mode bits as an MMR address, the manual says they are indirect addressing of page 0; gas encodes them the module's way); IDLE NN=11;
MVMM register fields 9-15 (SPRU172C allows AR0-AR7, SP; gas rejects the others); ESTOP (F4F0), which neither TI manual documents.

## Bugs fixed in the module (all found by these tests)
MVMM decoded register fields 9-15 (found by the clean-room table diff); ESTOP was decoded although no TI manual defines it (removed with the clean-room encodings).
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
The encodings are now independent of the binutils table (clean-room from the TI manuals), so the objdump/gas comparison is a real cross-check for decode; semantics still rest on the manuals alone: there is no independent C54x simulator, no TI toolchain, no real third-party code. Peripheral map in the pspec (C5402/C5409/C5416) and the cspec calling convention are upstream's, untested.
