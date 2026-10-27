* FIR filter, block copy, divide and a small interrupt routine, written for the Ghidra-Rare TMS320C54x tests.
* Copyright 2026 Ghidra-Rare contributors, Apache-2.0.  Assembled with GNU as (tic54x), never run on hardware.
 .mmregs
 .text
 .global reset, isr_timer, start, fir_init, fir32, divide, copy_block, cond_demo, done
reset:
 b start
 nop
 nop
isr_timer:                         ; vector at 0x0004
 pshm st0
 pshm st1
 pshm ar1
 ld @0,a
 add #1,a
 stl a,@0
 popm ar1
 popm st1
 popm st0
 rete
start:
 stm #0x7ff,sp
 ssbx intm
 rsbx cpl
 ssbx sxm
 ssbx frct
 stm #0x2000,ar2          ; coefficients
 stm #0x2100,ar3          ; delay line (circular, 32 words)
 stm #31,bk
 stm #1,ar0
 call fir_init
 stm #16,brc
 rptb loop_end-1
 ld *ar3,16,a
 macp *ar2+,0x3000,a
 stl a,*ar3+%
loop_end:
 call fir32
 b done
fir_init:
 stm #31,ar4
 ld #0,a
fi_loop:
 stl a,*ar3+%
 banz fi_loop,*ar4-
 ret
fir32:
 frame -2
 stm #0x2200,ar5
 stm #31,brc
 rptz a,#31
 mac *ar2+,*ar3+0%,a
 sth a,*ar5+
 sftl a,-4
 bit *ar5,15
 bc neg,tc
 nop
neg:
 neg a
 frame 2
 ret
divide:                              ; 16-bit unsigned division by repeated SUBC
 ld @8,16,a
 rpt #15
 subc @9,a
 stl a,@10
 sth a,@11
 ret
copy_block:
 stm #0x1000,ar1
 stm #0x1800,ar2
 rpt #63
 mvkd 0x1000,*ar2+
 mvdd *ar2+,*ar3+
 mvpd 0x4000,*ar2+
 reada *ar2+
 writa *ar1+
 ret
cond_demo:
 ld *ar1,a
 xc 1,agt
 neg a
 xc 2,aeq
 ld #1,b
 add #2,b
 bcd loop_end,anov
 nop
 nop
 calld fir_init
 nop
 nop
 retd
 nop
 nop
done:
 idle 1
 b done
