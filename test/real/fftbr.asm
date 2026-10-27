* Bit-reversed reordering, complex multiply and a dual-operand loop (Ghidra-Rare TMS320C54x tests, Apache-2.0).
 .mmregs
 .text
 .global begin, cmul, energy, stop
begin:
 stm #0x7ff,sp
 stm #0x100,ar2
 stm #0x200,ar3
 stm #8,ar0                ; half the FFT size
 stm #15,brc
 rptb rev_end-1
 ld *ar2+,a
 stl a,*ar3+0b
 ld *ar2+,a
 stl a,*ar3+0b
rev_end:
 call cmul
 call energy
 b stop
cmul:
 ld *ar2+,16,a
 mpy *ar3+,b
 ld *ar2-,16,a
 macr *ar3-,b
 mas *ar2,*ar3,a
 squra *ar2,b
 squrs *ar3,b
 mpya a
 ret
energy:
 stm #255,brc
 stm #0x300,ar4
 stm #0x400,ar5
 ld #0,a
 ld #0,b
 rptb en_end-1
 mac *ar4+,*ar5+,a
 macsu *ar4+,*ar5+,b
 stl a,*ar4
en_end:
 sat a
 exp a
 norm a
 sth a,*ar4
 ret
stop:
 nop
 b stop
