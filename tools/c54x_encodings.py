"""TMS320C54x instruction encodings, transcribed clean-room from Texas Instruments documentation.

Sources (fetched by tools/fetch-ti-docs.sh, pinned by SHA-256; not redistributed):
  SPRU172C  TMS320C54x DSP Reference Set, Volume 2: Mnemonic Instruction Set (March 2001)
            chapter 4 instruction pages ("Opcode" boxes), Table 1-2 (opcode symbols), Appendix A (conditions)
  SPRU131G  TMS320C54x DSP Reference Set, Volume 1: CPU and Peripherals (March 2001)
            section 5.4/5.5 (Figures 5-3, 5-7, 5-11; Tables 5-2 to 5-8: Smem/Xmem/Ymem fields)

Nothing in this file was taken from GNU binutils or any other tool's opcode table.  The table was typed from the
opcode boxes and then checked against an automatic extraction of the same boxes from the PDF text
(tools/extract_opcode_boxes.py + tools/check_transcription.py: 193 of 193 forms agree; the one deliberate difference
is XORM, see its entry).

Every entry: (mnemonic, syntax number on the page, syntax as printed, word-0 pattern, extension words, page).
The page is the printed SPRU172C page that holds the opcode box.

Word-0 patterns are 16 characters, bit 15 first ('0'/'1' fixed; spaces are ignored). The letters are this file's own
names for the fields of SPRU172C Table 1-2 (single letters so that every field has a width):
  S   src accumulator (S=0 A, S=1 B)            D   dst accumulator (D=0 A, D=1 B)
  R   rounding suffix R                         Z   delayed form (suffix D)
  I A I=0: direct (A = 7-bit dma); I=1: indirect, A = MOD(4) ARF(3)   (SPRU131G Fig. 5-3, 5-7, Table 5-4)
      the operand the page names decides the role: Smem, Lmem (32-bit), Sind (indirect only, BANZ), MMR
  X Y Xmem / Ymem: Xmod(2) Xar(2) / Ymod(2) Yar(2)       (SPRU131G Fig. 5-11, Tables 5-7, 5-8)
  K   short immediate (width = run of K; signedness from the page's Operands line, see SIGNED_K)
  H   SHIFT, 5-bit two's complement (-16..15)   F   SHFT, 4-bit (0..15)
  C   8-bit condition (cond list, BC/CC/RC/XC)  O   4-bit COND (SACCD/SRCCD/STRCD)
  B   BITC (4)    T   SBIT (4)    N   single bit N (status register for SSBX/RSBX, n-1 for XC)
  Q   NN (IDLE)   V   CC (CMPR, 2 bits)   P   ARX (3)   M   MMRX (4)   W   MMRY (4)
  G   pmad(22-16) of FB/FCALL (7 bits)
Extension words (in order after word 0; a long-offset Smem adds one more word, see LONG_OFFSET_ORDER):
  'lk' 16-bit constant, 'pmad', 'dmad', 'PA', 'pmad_lo' (pmad(15-0) of FB/FCALL), or a 16-character pattern.
"""

ENCODINGS = [
    # mnem        syn  syntax as printed                              word 0                ext                         page
    ('ABDST',     0, 'ABDST Xmem, Ymem',                        '1110 0011 XXXX YYYY', [],                          '4-2'),
    ('ABS',       0, 'ABS src [, dst ]',                        '1111 01SD 1000 0101', [],                          '4-3'),
    ('ADD',       1, 'ADD Smem, src',                           '0000 000S IAAA AAAA', [],                          '4-4'),
    ('ADD',       2, 'ADD Smem, TS, src',                       '0000 010S IAAA AAAA', [],                          '4-4'),
    ('ADD',       3, 'ADD Smem, 16, src [, dst ]',              '0011 11SD IAAA AAAA', [],                          '4-4'),
    ('ADD',       4, 'ADD Smem [, SHIFT], src [, dst ]',        '0110 1111 IAAA AAAA', ['0000 11SD 000H HHHH'],     '4-4'),
    ('ADD',       5, 'ADD Xmem, SHFT, src',                     '1001 000S XXXX FFFF', [],                          '4-4'),
    ('ADD',       6, 'ADD Xmem, Ymem, dst',                     '1010 000D XXXX YYYY', [],                          '4-4'),
    ('ADD',       7, 'ADD #lk [, SHFT], src [, dst ]',          '1111 00SD 0000 FFFF', ['lk'],                      '4-4'),
    ('ADD',       8, 'ADD #lk, 16, src [, dst ]',               '1111 00SD 0110 0000', ['lk'],                      '4-5'),
    ('ADD',       9, 'ADD src [, SHIFT], [, dst ]',             '1111 01SD 000H HHHH', [],                          '4-5'),
    ('ADD',      10, 'ADD src, ASM [, dst ]',                   '1111 01SD 1000 0000', [],                          '4-5'),
    ('ADDC',      0, 'ADDC Smem, src',                          '0000 011S IAAA AAAA', [],                          '4-8'),
    ('ADDM',      0, 'ADDM #lk, Smem',                          '0110 1011 IAAA AAAA', ['lk'],                      '4-9'),
    ('ADDS',      0, 'ADDS Smem, src',                          '0000 001S IAAA AAAA', [],                          '4-10'),
    ('AND',       1, 'AND Smem, src',                           '0001 100S IAAA AAAA', [],                          '4-11'),
    ('AND',       2, 'AND #lk [, SHFT ], src [, dst ]',         '1111 00SD 0011 FFFF', ['lk'],                      '4-11'),
    ('AND',       3, 'AND #lk, 16, src [, dst ]',               '1111 00SD 0110 0011', ['lk'],                      '4-11'),
    ('AND',       4, 'AND src [, SHIFT ], [, dst ]',            '1111 00SD 100H HHHH', [],                          '4-11'),
    ('ANDM',      0, 'ANDM #lk, Smem',                          '0110 1000 IAAA AAAA', ['lk'],                      '4-13'),
    ('B[D]',      0, 'B[D] pmad',                               '1111 00Z0 0111 0011', ['pmad'],                    '4-14'),
    ('BACC[D]',   0, 'BACC[D] src',                             '1111 01ZS 1110 0010', [],                          '4-15'),
    ('BANZ[D]',   0, 'BANZ[D] pmad, Sind',                      '0110 11Z0 IAAA AAAA', ['pmad'],                    '4-16'),
    ('BC[D]',     0, 'BC[D] pmad, cond [, cond [, cond ] ]',    '1111 10Z0 CCCC CCCC', ['pmad'],                    '4-18'),
    ('BIT',       0, 'BIT Xmem, BITC',                          '1001 0110 XXXX BBBB', [],                          '4-21'),
    ('BITF',      0, 'BITF Smem, #lk',                          '0110 0001 IAAA AAAA', ['lk'],                      '4-22'),
    ('BITT',      0, 'BITT Smem',                               '0011 0100 IAAA AAAA', [],                          '4-23'),
    ('CALA[D]',   0, 'CALA[D] src',                             '1111 01ZS 1110 0011', [],                          '4-25'),
    ('CALL[D]',   0, 'CALL[D] pmad',                            '1111 00Z0 0111 0100', ['pmad'],                    '4-27'),
    ('CC[D]',     0, 'CC[D] pmad, cond [, cond [, cond ] ]',    '1111 10Z1 CCCC CCCC', ['pmad'],                    '4-29'),
    ('CMPL',      0, 'CMPL src [, dst ]',                       '1111 01SD 1001 0011', [],                          '4-32'),
    ('CMPM',      0, 'CMPM Smem, #lk',                          '0110 0000 IAAA AAAA', ['lk'],                      '4-33'),
    ('CMPR',      0, 'CMPR CC, ARx',                            '1111 01VV 1010 1PPP', [],                          '4-34'),
    ('CMPS',      0, 'CMPS src, Smem',                          '1000 111S IAAA AAAA', [],                          '4-35'),
    ('DADD',      0, 'DADD Lmem, src [, dst ]',                 '0101 00SD IAAA AAAA', [],                          '4-37'),
    ('DADST',     0, 'DADST Lmem, dst',                         '0101 101D IAAA AAAA', [],                          '4-39'),
    ('DELAY',     0, 'DELAY Smem',                              '0100 1101 IAAA AAAA', [],                          '4-41'),
    ('DLD',       0, 'DLD Lmem, dst',                           '0101 011D IAAA AAAA', [],                          '4-42'),
    ('DRSUB',     0, 'DRSUB Lmem, src',                         '0101 100S IAAA AAAA', [],                          '4-43'),
    ('DSADT',     0, 'DSADT Lmem, dst',                         '0101 111D IAAA AAAA', [],                          '4-45'),
    ('DST',       0, 'DST src, Lmem',                           '0100 111S IAAA AAAA', [],                          '4-47'),
    ('DSUB',      0, 'DSUB Lmem, src',                          '0101 010S IAAA AAAA', [],                          '4-48'),
    ('DSUBT',     0, 'DSUBT Lmem, dst',                         '0101 110D IAAA AAAA', [],                          '4-50'),
    ('EXP',       0, 'EXP src',                                 '1111 010S 1000 1110', [],                          '4-52'),
    ('FB[D]',     0, 'FB[D] extpmad',                           '1111 10Z0 1GGG GGGG', ['pmad_lo'],                 '4-53'),
    ('FBACC[D]',  0, 'FBACC[D] src',                            '1111 01ZS 1110 0110', [],                          '4-54'),
    ('FCALA[D]',  0, 'FCALA[D] src',                            '1111 01ZS 1110 0111', [],                          '4-55'),
    ('FCALL[D]',  0, 'FCALL[D] extpmad',                        '1111 10Z1 1GGG GGGG', ['pmad_lo'],                 '4-57'),
    ('FIRS',      0, 'FIRS Xmem, Ymem, pmad',                   '1110 0000 XXXX YYYY', ['pmad'],                    '4-59'),
    ('FRAME',     0, 'FRAME K',                                 '1110 1110 KKKK KKKK', [],                          '4-60'),
    ('FRET[D]',   0, 'FRET[D]',                                 '1111 01Z0 1110 0100', [],                          '4-61'),
    ('FRETE[D]',  0, 'FRETE[D]',                                '1111 01Z0 1110 0101', [],                          '4-62'),
    ('IDLE',      0, 'IDLE K',                                  '1111 01QQ 1110 0001', [],                          '4-63'),
    ('INTR',      0, 'INTR K',                                  '1111 0111 110K KKKK', [],                          '4-65'),
    ('LD',        1, 'LD Smem, dst',                            '0001 000D IAAA AAAA', [],                          '4-66'),
    ('LD',        2, 'LD Smem, TS, dst',                        '0001 010D IAAA AAAA', [],                          '4-66'),
    ('LD',        3, 'LD Smem, 16, dst',                        '0100 010D IAAA AAAA', [],                          '4-66'),
    ('LD',        4, 'LD Smem [, SHIFT ], dst',                 '0110 1111 IAAA AAAA', ['0000 110D 010H HHHH'],     '4-66'),
    ('LD',        5, 'LD Xmem, SHFT, dst',                      '1001 010D XXXX FFFF', [],                          '4-66'),
    ('LD',        6, 'LD #K, dst',                              '1110 100D KKKK KKKK', [],                          '4-66'),
    ('LD',        7, 'LD #lk [, SHFT ], dst',                   '1111 000D 0010 FFFF', ['lk'],                      '4-67'),
    ('LD',        8, 'LD #lk, 16, dst',                         '1111 000D 0110 0010', ['lk'],                      '4-67'),
    ('LD',        9, 'LD src, ASM [, dst ]',                    '1111 01SD 1000 0010', [],                          '4-67'),
    ('LD',       10, 'LD src [, SHIFT ], dst',                  '1111 01SD 010H HHHH', [],                          '4-67'),
    ('LD',       11, 'LD Smem, T',                              '0011 0000 IAAA AAAA', [],                          '4-70'),  # page 4-70 syntax 1
    ('LD',       12, 'LD Smem, DP',                             '0100 0110 IAAA AAAA', [],                          '4-70'),  # syntax 2
    ('LD',       13, 'LD #k9, DP',                              '1110 101K KKKK KKKK', [],                          '4-70'),  # syntax 3
    ('LD',       14, 'LD #k5, ASM',                             '1110 1101 000K KKKK', [],                          '4-70'),  # syntax 4
    ('LD',       15, 'LD #k3, ARP',                             '1111 0100 1010 0KKK', [],                          '4-70'),  # syntax 5
    ('LD',       16, 'LD Smem, ASM',                            '0011 0010 IAAA AAAA', [],                          '4-70'),  # syntax 6
    ('LDM',       0, 'LDM MMR, dst',                            '0100 100D IAAA AAAA', [],                          '4-73'),
    ('LD||MAC[R]', 0, 'LD Xmem, dst || MAC[R] Ymem [, dst_ ]',  '1010 10RD XXXX YYYY', [],                          '4-74'),
    ('LD||MAS[R]', 0, 'LD Xmem, dst || MAS[R] Ymem [, dst_ ]',  '1010 11RD XXXX YYYY', [],                          '4-76'),
    ('LDR',       0, 'LDR Smem, dst',                           '0001 011D IAAA AAAA', [],                          '4-78'),
    ('LDU',       0, 'LDU Smem, dst',                           '0001 001D IAAA AAAA', [],                          '4-79'),
    ('LMS',       0, 'LMS Xmem, Ymem',                          '1110 0001 XXXX YYYY', [],                          '4-80'),
    ('LTD',       0, 'LTD Smem',                                '0100 1100 IAAA AAAA', [],                          '4-81'),
    ('MAC[R]',    1, 'MAC[R] Smem, src',                        '0010 10RS IAAA AAAA', [],                          '4-82'),
    ('MAC[R]',    2, 'MAC[R] Xmem, Ymem, src [, dst ]',         '1011 0RSD XXXX YYYY', [],                          '4-82'),
    ('MAC',       3, 'MAC #lk, src [, dst ]',                   '1111 00SD 0110 0111', ['lk'],                      '4-82'),
    ('MAC',       4, 'MAC Smem, #lk, src [, dst ]',             '0110 01SD IAAA AAAA', ['lk'],                      '4-82'),
    ('MACA[R]',   1, 'MACA[R] Smem [, B ]',                     '0011 01R1 IAAA AAAA', [],                          '4-85'),
    ('MACA[R]',   2, 'MACA[R] T, src [, dst ]',                 '1111 01SD 1000 100R', [],                          '4-85'),
    ('MACD',      0, 'MACD Smem, pmad, src',                    '0111 101S IAAA AAAA', ['pmad'],                    '4-87'),
    ('MACP',      0, 'MACP Smem, pmad, src',                    '0111 100S IAAA AAAA', ['pmad'],                    '4-89'),
    ('MACSU',     0, 'MACSU Xmem, Ymem, src',                   '1010 011S XXXX YYYY', [],                          '4-91'),
    ('MAR',       0, 'MAR Smem',                                '0110 1101 IAAA AAAA', [],                          '4-92'),
    ('MAS[R]',    1, 'MAS[R] Smem, src',                        '0010 11RS IAAA AAAA', [],                          '4-94'),
    ('MAS[R]',    2, 'MAS[R] Xmem, Ymem, src [, dst ]',         '1011 1RSD XXXX YYYY', [],                          '4-94'),
    ('MASA',      1, 'MASA Smem [, B ]',                        '0011 0011 IAAA AAAA', [],                          '4-97'),
    ('MASA[R]',   2, 'MASA[R] T, src [, dst ]',                 '1111 01SD 1000 101R', [],                          '4-97'),
    ('MAX',       0, 'MAX dst',                                 '1111 010D 1000 0110', [],                          '4-99'),
    ('MIN',       0, 'MIN dst',                                 '1111 010D 1000 0111', [],                          '4-100'),
    ('MPY[R]',    1, 'MPY[R] Smem, dst',                        '0010 00RD IAAA AAAA', [],                          '4-101'),
    ('MPY',       2, 'MPY Xmem, Ymem, dst',                     '1010 010D XXXX YYYY', [],                          '4-101'),
    ('MPY',       3, 'MPY Smem, #lk, dst',                      '0110 001D IAAA AAAA', ['lk'],                      '4-101'),
    ('MPY',       4, 'MPY #lk, dst',                            '1111 000D 0110 0110', ['lk'],                      '4-101'),
    ('MPYA',      1, 'MPYA Smem',                               '0011 0001 IAAA AAAA', [],                          '4-104'),
    ('MPYA',      2, 'MPYA dst',                                '1111 010D 1000 1100', [],                          '4-104'),
    ('MPYU',      0, 'MPYU Smem, dst',                          '0010 010D IAAA AAAA', [],                          '4-106'),
    ('MVDD',      0, 'MVDD Xmem, Ymem',                         '1110 0101 XXXX YYYY', [],                          '4-107'),
    ('MVDK',      0, 'MVDK Smem, dmad',                         '0111 0001 IAAA AAAA', ['dmad'],                    '4-108'),
    ('MVDM',      0, 'MVDM dmad, MMR',                          '0111 0010 IAAA AAAA', ['dmad'],                    '4-110'),
    ('MVDP',      0, 'MVDP Smem, pmad',                         '0111 1101 IAAA AAAA', ['pmad'],                    '4-111'),
    ('MVKD',      0, 'MVKD dmad, Smem',                         '0111 0000 IAAA AAAA', ['dmad'],                    '4-113'),
    ('MVMD',      0, 'MVMD MMR, dmad',                          '0111 0011 IAAA AAAA', ['dmad'],                    '4-115'),
    ('MVMM',      0, 'MVMM MMRx, MMRy',                         '1110 0111 MMMM WWWW', [],                          '4-116'),
    ('MVPD',      0, 'MVPD pmad, Smem',                         '0111 1100 IAAA AAAA', ['pmad'],                    '4-117'),
    ('NEG',       0, 'NEG src [, dst ]',                        '1111 01SD 1000 0100', [],                          '4-119'),
    ('NOP',       0, 'NOP',                                     '1111 0100 1001 0101', [],                          '4-121'),
    ('NORM',      0, 'NORM src [, dst ]',                       '1111 01SD 1000 1111', [],                          '4-122'),
    ('OR',        1, 'OR Smem, src',                            '0001 101S IAAA AAAA', [],                          '4-123'),
    ('OR',        2, 'OR #lk [, SHFT ], src [, dst ]',          '1111 00SD 0100 FFFF', ['lk'],                      '4-123'),
    ('OR',        3, 'OR #lk, 16, src [, dst ]',                '1111 00SD 0110 0100', ['lk'],                      '4-123'),
    ('OR',        4, 'OR src [, SHIFT ], [, dst ]',             '1111 00SD 101H HHHH', [],                          '4-123'),
    ('ORM',       0, 'ORM #lk, Smem',                           '0110 1001 IAAA AAAA', ['lk'],                      '4-125'),
    ('POLY',      0, 'POLY Smem',                               '0011 0110 IAAA AAAA', [],                          '4-126'),
    ('POPD',      0, 'POPD Smem',                               '1000 1011 IAAA AAAA', [],                          '4-127'),
    ('POPM',      0, 'POPM MMR',                                '1000 1010 IAAA AAAA', [],                          '4-128'),
    ('PORTR',     0, 'PORTR PA, Smem',                          '0111 0100 IAAA AAAA', ['PA'],                      '4-129'),
    ('PORTW',     0, 'PORTW Smem, PA',                          '0111 0101 IAAA AAAA', ['PA'],                      '4-130'),
    ('PSHD',      0, 'PSHD Smem',                               '0100 1011 IAAA AAAA', [],                          '4-131'),
    ('PSHM',      0, 'PSHM MMR',                                '0100 1010 IAAA AAAA', [],                          '4-132'),
    ('RC[D]',     0, 'RC[D] cond [, cond [, cond ] ]',          '1111 11Z0 CCCC CCCC', [],                          '4-133'),
    ('READA',     0, 'READA Smem',                              '0111 1110 IAAA AAAA', [],                          '4-136'),
    ('RESET',     0, 'RESET',                                   '1111 0111 1110 0000', [],                          '4-138'),
    ('RET[D]',    0, 'RET[D]',                                  '1111 11Z0 0000 0000', [],                          '4-139'),
    ('RETE[D]',   0, 'RETE[D]',                                 '1111 01Z0 1110 1011', [],                          '4-140'),
    ('RETF[D]',   0, 'RETF[D]',                                 '1111 01Z0 1001 1011', [],                          '4-141'),
    ('RND',       0, 'RND src [, dst ]',                        '1111 01SD 1001 1111', [],                          '4-142'),
    ('ROL',       0, 'ROL src',                                 '1111 010S 1001 0001', [],                          '4-143'),
    ('ROLTC',     0, 'ROLTC src',                               '1111 010S 1001 0010', [],                          '4-144'),
    ('ROR',       0, 'ROR src',                                 '1111 010S 1001 0000', [],                          '4-145'),
    ('RPT',       1, 'RPT Smem',                                '0100 0111 IAAA AAAA', [],                          '4-146'),
    ('RPT',       2, 'RPT #K',                                  '1110 1100 KKKK KKKK', [],                          '4-146'),
    ('RPT',       3, 'RPT #lk',                                 '1111 0000 0111 0000', ['lk'],                      '4-146'),
    ('RPTB[D]',   0, 'RPTB[D] pmad',                            '1111 00Z0 0111 0010', ['pmad'],                    '4-148'),
    ('RPTZ',      0, 'RPTZ dst, #lk',                           '1111 000D 0111 0001', ['lk'],                      '4-150'),
    ('RSBX',      0, 'RSBX N, SBIT',                            '1111 01N0 1011 TTTT', [],                          '4-151'),
    ('SACCD',     0, 'SACCD src, Xmem, cond',                   '1001 111S XXXX OOOO', [],                          '4-152'),
    ('SAT',       0, 'SAT src',                                 '1111 010S 1000 0011', [],                          '4-154'),
    ('SFTA',      0, 'SFTA src, SHIFT [, dst ]',                '1111 01SD 011H HHHH', [],                          '4-155'),
    ('SFTC',      0, 'SFTC src',                                '1111 010S 1001 0100', [],                          '4-157'),
    ('SFTL',      0, 'SFTL src, SHIFT [, dst ]',                '1111 00SD 111H HHHH', [],                          '4-158'),
    ('SQDST',     0, 'SQDST Xmem, Ymem',                        '1110 0010 XXXX YYYY', [],                          '4-160'),
    ('SQUR',      1, 'SQUR Smem, dst',                          '0010 011D IAAA AAAA', [],                          '4-161'),
    ('SQUR',      2, 'SQUR A, dst',                             '1111 010D 1000 1101', [],                          '4-161'),
    ('SQURA',     0, 'SQURA Smem, src',                         '0011 100S IAAA AAAA', [],                          '4-163'),
    ('SQURS',     0, 'SQURS Smem, src',                         '0011 101S IAAA AAAA', [],                          '4-164'),
    ('SRCCD',     0, 'SRCCD Xmem, cond',                        '1001 1101 XXXX OOOO', [],                          '4-165'),
    ('SSBX',      0, 'SSBX N, SBIT',                            '1111 01N1 1011 TTTT', [],                          '4-166'),
    ('ST',        1, 'ST T, Smem',                              '1000 1100 IAAA AAAA', [],                          '4-167'),
    ('ST',        2, 'ST TRN, Smem',                            '1000 1101 IAAA AAAA', [],                          '4-167'),
    ('ST',        3, 'ST #lk, Smem',                            '0111 0110 IAAA AAAA', ['lk'],                      '4-167'),
    ('STH',       1, 'STH src, Smem',                           '1000 001S IAAA AAAA', [],                          '4-169'),
    ('STH',       2, 'STH src, ASM, Smem',                      '1000 011S IAAA AAAA', [],                          '4-169'),
    ('STH',       3, 'STH src, SHFT, Xmem',                     '1001 101S XXXX FFFF', [],                          '4-169'),
    ('STH',       4, 'STH src [, SHIFT ], Smem',                '0110 1111 IAAA AAAA', ['0000 110S 011H HHHH'],     '4-169'),
    ('STL',       1, 'STL src, Smem',                           '1000 000S IAAA AAAA', [],                          '4-172'),
    ('STL',       2, 'STL src, ASM, Smem',                      '1000 010S IAAA AAAA', [],                          '4-172'),
    ('STL',       3, 'STL src, SHFT, Xmem',                     '1001 100S XXXX FFFF', [],                          '4-172'),
    ('STL',       4, 'STL src [, SHIFT], Smem',                 '0110 1111 IAAA AAAA', ['0000 110S 100H HHHH'],     '4-172'),
    ('STLM',      0, 'STLM src, MMR',                           '1000 100S IAAA AAAA', [],                          '4-175'),
    ('STM',       0, 'STM #lk, MMR',                            '0111 0111 IAAA AAAA', ['lk'],                      '4-176'),
    ('ST||ADD',   0, 'ST src, Ymem || ADD Xmem, dst',           '1100 00SD XXXX YYYY', [],                          '4-177'),
    ('ST||LD',    1, 'ST src, Ymem || LD Xmem, dst',            '1100 10SD XXXX YYYY', [],                          '4-178'),
    ('ST||LD',    2, 'ST src, Ymem || LD Xmem, T',              '1110 01S0 XXXX YYYY', [],                          '4-178'),
    ('ST||MAC[R]', 0, 'ST src, Ymem || MAC[R] Xmem, dst',       '1101 0RSD XXXX YYYY', [],                          '4-180'),
    ('ST||MAS[R]', 0, 'ST src, Ymem || MAS[R] Xmem, dst',       '1101 1RSD XXXX YYYY', [],                          '4-182'),
    ('ST||MPY',   0, 'ST src, Ymem || MPY Xmem, dst',           '1100 11SD XXXX YYYY', [],                          '4-184'),
    ('ST||SUB',   0, 'ST src, Ymem || SUB Xmem, dst',           '1100 01SD XXXX YYYY', [],                          '4-185'),
    ('STRCD',     0, 'STRCD Xmem, cond',                        '1001 1100 XXXX OOOO', [],                          '4-186'),
    ('SUB',       1, 'SUB Smem, src',                           '0000 100S IAAA AAAA', [],                          '4-187'),
    ('SUB',       2, 'SUB Smem, TS, src',                       '0000 110S IAAA AAAA', [],                          '4-187'),
    ('SUB',       3, 'SUB Smem, 16, src [, dst ]',              '0100 00SD IAAA AAAA', [],                          '4-187'),
    ('SUB',       4, 'SUB Smem [, SHIFT ], src [, dst ]',       '0110 1111 IAAA AAAA', ['0000 11SD 001H HHHH'],     '4-187'),
    ('SUB',       5, 'SUB Xmem, SHFT, src',                     '1001 001S XXXX FFFF', [],                          '4-187'),
    ('SUB',       6, 'SUB Xmem, Ymem, dst',                     '1010 001D XXXX YYYY', [],                          '4-187'),
    ('SUB',       7, 'SUB #lk [, SHFT ], src [, dst ]',         '1111 00SD 0001 FFFF', ['lk'],                      '4-187'),
    ('SUB',       8, 'SUB #lk, 16, src [, dst ]',               '1111 00SD 0110 0001', ['lk'],                      '4-188'),
    ('SUB',       9, 'SUB src [, SHIFT ], [, dst ]',            '1111 01SD 001H HHHH', [],                          '4-188'),
    ('SUB',      10, 'SUB src, ASM [, dst ]',                   '1111 01SD 1000 0001', [],                          '4-188'),
    ('SUBB',      0, 'SUBB Smem, src',                          '0000 111S IAAA AAAA', [],                          '4-191'),  # box letters the bit D; the operand is src
    ('SUBC',      0, 'SUBC Smem, src',                          '0001 111S IAAA AAAA', [],                          '4-192'),
    ('SUBS',      0, 'SUBS Smem, src',                          '0000 101S IAAA AAAA', [],                          '4-194'),
    ('TRAP',      0, 'TRAP K',                                  '1111 0100 110K KKKK', [],                          '4-195'),
    ('WRITA',     0, 'WRITA Smem',                              '0111 1111 IAAA AAAA', [],                          '4-196'),
    ('XC',        0, 'XC n, cond [, cond [, cond ] ]',          '1111 11N1 CCCC CCCC', [],                          '4-198'),
    ('XOR',       1, 'XOR Smem, src',                           '0001 110S IAAA AAAA', [],                          '4-201'),
    ('XOR',       2, 'XOR #lk [, SHFT], src [, dst ]',          '1111 00SD 0101 FFFF', ['lk'],                      '4-201'),
    ('XOR',       3, 'XOR #lk, 16, src [, dst ]',               '1111 00SD 0110 0101', ['lk'],                      '4-201'),
    ('XOR',       4, 'XOR src [, SHIFT] [, dst ]',              '1111 00SD 110H HHHH', [],                          '4-201'),
    # 4-203: the opcode box prints only word 0; the same page's Operands (0 <= lk <= 65535) and Words (2 words) give the lk word.
    ('XORM',      0, 'XORM #lk, Smem',                          '0110 1010 IAAA AAAA', ['lk'],                      '4-203'),
]

# Signed short immediates (Operands lines): FRAME -128..127 (4-60), LD #k5,ASM -16..15 (4-70).
# Unsigned: LD #K,dst 0..255 (4-66), LD #k9,DP 0..511, LD #k3,ARP 0..7 (4-70), RPT #K 0..255 (4-146), INTR/TRAP 0..31.
SIGNED_K = {('FRAME', 0), ('LD', 14)}

# IDLE K -> NN (4-63): K=1 -> 00, K=2 -> 10, K=3 -> 01; NN=11 is not listed.
IDLE_NN = {0b00: 1, 0b10: 2, 0b01: 3}
# XC n -> N (4-198): n=1 -> N=0, n=2 -> N=1.
# CMPR CC (4-34): 00 EQ, 01 LT, 10 GT, 11 NEQ.
CMPR_CC = ['EQ', 'LT', 'GT', 'NEQ']
# MVMM MMRX/MMRY (4-116): 0000-0111 AR0-AR7, 1000 SP; 1001-1111 not listed.
MVMM_REG = ['AR0', 'AR1', 'AR2', 'AR3', 'AR4', 'AR5', 'AR6', 'AR7', 'SP']

# 8-bit conditions (BC page 4-18, same table on CC 4-29, RC 4-133, XC 4-198; groupings Appendix A Table A-2):
#   bit 7 = 0; bit 6 = 1 group 1 (accumulator), 0 group 2.
#   group 1: bits 5-4 overflow (11 OV, 10 NOV, 00 none); bit 3 accumulator (0 A, 1 B);
#            bits 2-0 compare (101 EQ, 100 NEQ, 110 GT, 010 GEQ, 011 LT, 111 LEQ, 000 none)
#   group 2: bits 5-4 TC (11 TC, 10 NTC, 00 none); bits 3-2 C (11 C, 10 NC); bits 1-0 BIO (11 BIO, 10 NBIO)
#   0000 0000 = UNC.
COND8_CMP = {0b101: 'EQ', 0b100: 'NEQ', 0b110: 'GT', 0b010: 'GEQ', 0b011: 'LT', 0b111: 'LEQ'}
# 4-bit COND (SACCD 4-152, SRCCD 4-165, STRCD 4-186): bit 3 accumulator, bits 2-0 compare as above; no UNC/OV.


def cond8(c):
    """condition names of an 8-bit condition field, None when it is not a SPRU172C combination"""
    if c == 0:
        return ['UNC']
    if c & 0x80:
        return None
    if c & 0x40:
        ov, acc, cmp_ = (c >> 4) & 3, 'AB'[(c >> 3) & 1], c & 7
        if ov == 1 or cmp_ == 1 or (ov == 0 and cmp_ == 0):
            return None
        out = []
        if cmp_:
            out.append(acc + COND8_CMP[cmp_])
        if ov:
            out.append(acc + ('OV' if ov == 3 else 'NOV'))
        return out
    out = []
    for sh, (t, f) in ((4, ('TC', 'NTC')), (2, ('C', 'NC')), (0, ('BIO', 'NBIO'))):
        x = (c >> sh) & 3
        if x == 1:
            return None
        if x:
            out.append(t if x == 3 else f)
    return out


def cond4(c):
    """name of a 4-bit COND field, None when undefined"""
    if c & 7 not in COND8_CMP:
        return None
    return 'AB'[(c >> 3) & 1] + COND8_CMP[c & 7]

# Smem with I=1 (SPRU131G Table 5-4): MOD 0-11 one word; MOD 12 *ARx(lk), 13 *+ARx(lk), 14 *+ARx(lk)%, 15 *(lk)
# add one word (SPRU172C 1-11 "Words": "long-offset modifiers ... require one additional word"; SPRU131G 5-5).
SMEM_MOD = ['*ARx', '*ARx-', '*ARx+', '*+ARx', '*ARx-0B', '*ARx-0', '*ARx+0', '*ARx+0B',
            '*ARx-%', '*ARx-0%', '*ARx+%', '*ARx+0%', '*ARx(lk)', '*+ARx(lk)', '*+ARx(lk)%', '*(lk)']
# Xmem/Ymem (SPRU131G Tables 5-7, 5-8): Xar/Yar 00 AR2, 01 AR3, 10 AR4, 11 AR5; mod 00 *ARx, 01 *ARx-, 10 *ARx+, 11 *ARx+0%.
XMOD = ['*ARx', '*ARx-', '*ARx+', '*ARx+0%']

# Position of the long-offset word relative to the instruction's own extension words: not stated in SPRU172C/SPRU131G;
# established black-box with GNU as (tic54x-coff 2.45): the offset word follows word 0, then the instruction's own
# extension word (e.g. ADD *AR1(5),3,B,A -> 6FE1 0005 0C03; ADDM #1234h,*(55h) -> 6BF8 0055 1234).  GHIDRA-RARE.md.
LONG_OFFSET_ORDER = 'after_word0'


def word_pattern(p):
    p = p.replace(' ', '')
    assert len(p) == 16, p
    return p


def fixed_mask(p):
    p = word_pattern(p)
    m = v = 0
    for i, ch in enumerate(p):
        b = 15 - i
        if ch in '01':
            m |= 1 << b
            v |= int(ch) << b
    return m, v


def fields(p):
    """letter -> (lo bit, width), each letter one contiguous run (I and A separate)."""
    p = word_pattern(p)
    out = {}
    for i, ch in enumerate(p):
        if ch in '01':
            continue
        b = 15 - i
        lo, w = out.get(ch, (b, 0))
        out[ch] = (min(lo, b), w + 1)
    return out


def get(word, f):
    lo, w = f
    return (word >> lo) & ((1 << w) - 1)
