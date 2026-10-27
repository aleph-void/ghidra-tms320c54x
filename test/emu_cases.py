"""Hand-computed p-code test cases for the TMS320C54x module.

Each case: (name, assembly, initial state, expected state).  Syntax of the assembly: GNU as for tic54x (used only
as an assembler to build the bytes; the expected values come from the TI manuals SPRU172C / SPRU131G, the page of
each example is noted).  State items: register=hex (A and B are 40-bit values), data#2:<addr>=<word> (data space
word), data#4:<addr>=<2 words, high word at the even address>, prog#2:<addr>=<word>.  A case whose name starts
with XFAIL_ carries a deliberately wrong expectation and must be reported as failing.
"""
CASES = [
    # --- SPRU172C examples -------------------------------------------------------------------------------------
    ("add_shift14_postinc", " add *ar3+,14,a", "A=1200,C=1,AR3=100,SXM=1,data#2:100=1500", "A=0005401200,C=0,AR3=101"),           # ADD ex.1
    ("add_acc_rshift8", " add a,-8,b", "A=1200,B=1800,C=1", "B=1812,A=1200,C=0"),                                                 # ADD ex.2
    ("add_lk_shift8", " add #4568h,8,a,b", "A=1200,B=1800,C=1", "B=457a00,C=0"),                                                  # ADD ex.3 (lk=4568h)
    ("addc_preinc_offset", " addc *+ar2(5),a", "A=13,C=1,AR2=100,data#2:105=4", "A=18,C=0,AR2=105"),                             # ADDC ex.
    ("neg_a_b", " neg a,b", "A=ffffffF228,B=1234,OVA=0", "B=dd8,OVA=0"),                                                          # NEG ex.1
    ("neg_b_a", " neg b,a", "A=1234,B=0080000000,OVB=0", "A=ff80000000,OVB=0"),                                                  # NEG ex.2
    ("neg_overflow_ovm0", " neg a", "A=8000000000,OVA=0,OVM=0", "A=8000000000,OVA=1"),                                            # NEG ex.3
    ("neg_overflow_ovm1", " neg a", "A=8000000000,OVA=0,OVM=1", "A=007fffffff,OVA=1"),                                            # NEG ex.4
    ("abs_a_b", " abs a,b", "A=ffffffffcb,B=fffffffc18", "B=35,A=ffffffffcb"),                                                    # ABS ex.1
    ("abs_ovm1", " abs a", "A=0312345678,OVM=1", "A=007fffffff"),                                                                 # ABS ex.2
    ("abs_ovm0", " abs a", "A=0312345678,OVM=0", "A=0312345678"),                                                                 # ABS ex.3
    ("sat_b_pos", " sat b", "B=7123456789,OVB=0", "B=007fffffff,OVB=1"),                                                          # SAT ex.1
    ("sat_a_neg", " sat a", "A=f812345678,OVA=0", "A=ff80000000,OVA=1"),                                                          # SAT ex.2
    ("sat_b_none", " sat b", "B=0000123456,OVB=1", "B=123456,OVB=0"),                                                             # SAT ex.3
    ("subb_borrow", " subb 5,a", "A=6,C=0,DP=8,data#2:405=6", "A=ffffffffff,C=0"),                                                # SUBB ex.1
    ("subb_ovm", " subb *ar1+,b", "B=ff80000006,C=1,OVM=1,AR1=405,data#2:405=6", "B=ff80000000,C=1,AR1=406"),                    # SUBB ex.2
    ("subc_once", " subc 2,a", "A=4,C=1,DP=6,data#2:302=1", "A=8,C=0"),                                                           # SUBC ex.1
    ("subc_x16", " subc *ar1,b\n" * 16, "B=41,AR1=1000,data#2:1000=7", "B=20009,C=1"),                                            # SUBC ex.2 (RPT #15)
    ("max_a_ge_b", " max a", "A=fffffffff6,B=ffffffffcb,C=1", "A=fffffffff6,C=0"),                                                # MAX ex.1
    ("min_b_lt_a", " min a", "A=5,B=1,C=0", "A=1,C=1"),
    ("sfta_right5", " sfta a,-5,b", "A=ff87650055,B=0043211234,SXM=1", "B=fffc3b2802,C=1"),                                       # SFTA ex.1
    ("sfta_left5_nocarry_check", " sfta b,5", "B=80aa001234,SXM=0,OVM=0", "B=1540024680"),                                        # SFTA ex.2 (value)
    ("rol_a", " rol a", "A=5fb0001234,C=0", "A=0060002468,C=1"),                                                                  # ROL ex.
    ("ror_a", " ror a", "A=7fb0001235,C=0", "A=005800091a,C=1"),                                                                  # ROR ex.
    ("ld_mac_parallel", " ld *ar4+,a || mac *ar5+,b", "A=1000,B=1111,T=400,FRCT=0,AR4=100,AR5=200,data#2:100=1234,data#2:200=4321",
     "A=0012340000,B=010c9511,AR4=101,AR5=201"),                                                                                  # LD||MAC ex.1
    # --- addressing modes (SPRU131G table 5-4, section 5.5.3) ------------------------------------------------
    ("ld_sxm1", " ld *ar1,a", "AR1=100,SXM=1,data#2:100=8000", "A=ffffff8000"),
    ("ld_sxm0", " ld *ar1,a", "AR1=100,SXM=0,data#2:100=8000", "A=0000008000"),
    ("ld_ts_negative_t", " ld *ar1,ts,a", "AR1=100,T=fffc,SXM=1,data#2:100=0100", "A=10"),
    ("bitrev_x3", " mar *ar2+0b\n mar *ar2+0b\n mar *ar2+0b", "AR2=60,AR0=8", "AR2=6c"),                                          # example 5-1
    ("bitrev_x8", " mar *ar2+0b\n" * 8, "AR2=60,AR0=8", "AR2=61"),
    ("circ_wrap_up", " mar *ar1+%", "AR1=104,BK=5", "AR1=100"),
    ("circ_no_wrap", " mar *ar1+%", "AR1=102,BK=5", "AR1=103"),
    ("circ_wrap_down", " mar *ar1-%", "AR1=100,BK=5", "AR1=104"),
    ("circ_add_ar0", " mar *ar1+0%", "AR1=104,AR0=3,BK=5", "AR1=102"),
    ("circ_bk0_plain_add", " mar *ar1+%", "AR1=104,BK=0", "AR1=105"),     # BK=0: no circular modification
    ("ind_predec_store", " st #1234h,*+ar3(2)", "AR3=100", "AR3=102,data#2:102=1234"),
    ("direct_dp", " ld @5,a", "DP=2,SXM=1,data#2:105=7", "A=7"),
    ("direct_sp_cpl", " ssbx cpl\n .word 1003h", "SP=200,SXM=1,data#2:203=9", "A=9"),
    ("abs_addr", " ld *(300h),a", "SXM=1,data#2:300=ffff", "A=ffffffffff"),
    ("dld_dst", " dld *ar1,a", "AR1=100,SXM=1,data#2:100=1234,data#2:101=5678", "A=12345678"),
    ("dst_store", " dst a,*ar1", "AR1=100,A=0012345678", "data#2:100=1234,data#2:101=5678"),
    # --- arithmetic with OVM / SXM / flags ----------------------------------------------------------------------
    ("add_overflow_ovm1", " add *ar1,a", "AR1=100,A=007fffffff,OVM=1,OVA=0,SXM=1,data#2:100=1", "A=007fffffff,OVA=1,C=0"),
    ("add_overflow_ovm0_keeps40", " add *ar1,a", "AR1=100,A=007fffffff,OVM=0,OVA=0,SXM=1,data#2:100=1", "A=0080000000,OVA=0"),
    ("add_carry_out", " add *ar1,a", "AR1=100,A=00ffffffff,SXM=0,C=0,data#2:100=1", "A=0100000000,C=1"),
    ("sub_borrow_clears_c", " sub *ar1,a", "AR1=100,A=0,SXM=1,C=1,data#2:100=1", "A=ffffffffff,C=0"),
    ("sub_no_borrow_sets_c", " sub *ar1,a", "AR1=100,A=5,SXM=1,C=0,data#2:100=1", "A=4,C=1"),
    ("mpy_frct0", " mpy *ar1,a", "AR1=100,T=100,FRCT=0,data#2:100=200", "A=20000"),
    ("mpy_frct1", " mpy *ar1,a", "AR1=100,T=100,FRCT=1,data#2:100=200", "A=40000"),
    ("mpyr_clears_low16", " mpyr *ar1,a", "AR1=100,T=3,FRCT=0,data#2:100=5", "A=0"),                                              # MPY[R]: +2^15, bits 15-0 cleared
    ("macr_rounds", " macr *ar1,a", "AR1=100,T=2,FRCT=0,A=0,data#2:100=4000", "A=10000"),
    ("sftl_right4", " sftl a,-4", "A=0080000001", "A=0008000000,C=0"),
    ("exp_one", " exp a", "A=1", "T=1e"),
    ("exp_32bit_norm", " exp a", "A=007fffffff", "T=0"),
    ("exp_zero", " exp a", "A=0,T=77", "T=0"),
    ("norm_by_t", " norm a", "A=1,T=4", "A=10"),
    ("cmps_hi_greater", " cmps a,*ar1", "AR1=100,A=0000050003,TRN=1", "data#2:100=5,TRN=2,TC=0"),                                 # CMPS
    ("cmps_lo_greater", " cmps a,*ar1", "AR1=100,A=0000030007,TRN=1", "data#2:100=7,TRN=3,TC=1"),
    ("sqdst", " sqdst *ar2,*ar3", "AR2=100,AR3=101,A=0000030000,B=1,FRCT=0,data#2:100=9,data#2:101=4", "B=a,A=0000050000"),
    ("lms", " lms *ar2,*ar3", "AR2=100,AR3=101,A=0,B=0,FRCT=0,SXM=1,data#2:100=3,data#2:101=4", "A=0000030000,B=c"),
    ("poly", " poly *ar1", "AR1=100,A=0000020000,B=10000,T=3,FRCT=0,SXM=1,data#2:100=7", "B=70000,A=10000"),
    # --- control flow ---------------------------------------------------------------------------------------------
    ("banz_loop", " stm #3,ar3\nl: add #1,a\n banz l,*ar3-", "A=0,SXM=1", "A=4,AR3=ffff"),
    ("call_ret", " call sub1\n b done\nsub1: ld #7,a\n ret\ndone: nop", "SP=200,A=0", "A=7,SP=200"),
    ("calld_delay_slots", " calld sub1\n ld #3,b\n nop\n b done\nsub1: ld #7,a\n retd\n nop\n nop\ndone: nop", "SP=200", "A=7,B=3,SP=200"),
    ("bc_taken_on_c", " bc tgt,c\n ld #1,a\n b done\ntgt: ld #2,a\ndone: nop", "C=1,SXM=1", "A=2"),
    ("bc_not_taken", " bc tgt,c\n ld #1,a\n b done\ntgt: ld #2,a\ndone: nop", "C=0,SXM=1", "A=1"),
    ("bc_bio_low", " bc tgt,bio\n ld #1,a\n b done\ntgt: ld #2,a\ndone: nop", "BIO=0", "A=2"),
    ("bc_bio_high", " bc tgt,bio\n ld #1,a\n b done\ntgt: ld #2,a\ndone: nop", "BIO=1", "A=1"),
    ("bc_aov_clears_ov", " bc tgt,aov\n nop\ntgt: nop", "OVA=1", "OVA=0"),
    ("xc_skips_one", " xc 1,aeq\n ld #5,b\n ld #6,a", "A=1,B=0,SXM=1", "B=0,A=6"),
    ("xc_executes", " xc 1,aeq\n ld #5,b\n ld #6,a", "A=0,B=0,SXM=1", "B=5,A=6"),

    ("pshm_popm", " pshm ar1\n popm ar2", "SP=200,AR1=1234", "AR2=1234,SP=200,data#2:1ff=1234"),
    ("frame", " frame -4", "SP=200", "SP=1fc"),
    ("rptb_sets", " rptb endl-1\n nop\nendl: nop", "", "BRAF=1"),
    ("ssbx_rsbx_ovm", " ssbx ovm\n rsbx sxm", "OVM=0,SXM=1", "OVM=1,SXM=0"),
    ("ld_asm_k", " ld #-3,asm", "", "ASM=fd"),   # ASM is kept sign-extended (a 5-bit field in ST1)
    ("ld_smem_asm", " ld *ar1,asm", "AR1=100,data#2:100=ffff", "ASM=ff"),
    ("ld_dp_k", " ld #1ffh,dp", "", "DP=1ff"),
    # --- repeat, dual 16-bit mode, status registers, far calls ------------------------------------------------------
    ("rpt_add_loop", " rpt #4\n add #1,a", "A=0,SXM=1", "A=5,RC=0"),                       # RPT #n: the next instruction runs n+1 times
    ("rpt_mac_postinc", " rpt #2\n mac *ar2+,*ar3+,a",
     "A=0,AR2=100,AR3=200,FRCT=0,data#2:100=1,data#2:101=2,data#2:102=3,data#2:200=10,data#2:201=20,data#2:202=30", "A=e0,AR2=103,AR3=203"),
    ("rptz_clears_acc", " rptz a,#1\n add #3,a", "A=ff,SXM=1", "A=6"),
    ("dadd_double", " dadd *ar1,a,b", "AR1=100,A=1,C16=0,SXM=1,data#2:100=0001,data#2:101=ffff", "B=20000"),
    ("dadd_dual16", " dadd *ar1,a,b", "AR1=100,A=0000030005,C16=1,SXM=1,data#2:100=1000,data#2:101=0009", "B=001003000e"),
    ("dsub_double", " dsub *ar1,a", "AR1=100,A=20000,C16=0,SXM=1,data#2:100=0001,data#2:101=ffff", "A=1"),
    ("dsubt_double", " dsubt *ar1,a", "AR1=100,T=2,C16=0,SXM=1,data#2:100=0003,data#2:101=0004", "A=00010002"),   # Lmem - T:T
    ("dadst_dual16", " dadst *ar1,a", "AR1=100,T=5,C16=1,SXM=1,data#2:100=0010,data#2:101=0020", "A=0000150001b".replace("0000150001b", "000015001b")),
    ("pshm_st0", " .mmregs\n pshm st0", "SP=200,TC=1,C=0,OVA=1,OVB=0,DP=12,ARP=0", "SP=1ff,data#2:1ff=1412"),         # ST0 = TC<<12 | OVA<<10 | DP
    ("popm_st1_sets_flags", " .mmregs\n popm st1", "SP=1ff,data#2:1ff=0b00", "SP=200,OVM=1,SXM=1,INTM=1"),            # ST1 bits 11, 9, 8
    ("stm_st0_dp", " .mmregs\n stm #1ffh,st0", "DP=0", "DP=1ff"),
    ("ldm_st1_a", " .mmregs\n ldm st1,a", "SXM=1,OVM=1,A=ffff", "A=300"),
    ("far_call_ret", " .word 0f981h, sub1\n b done\nsub1: ld #7,a\n .word 0f4e4h\ndone: nop", "SP=200,XPC=5", "A=7,SP=200,XPC=5"),
    ("far_branch_sets_xpc", " .word 0f882h, tgt\n ld #1,a\ntgt: ld #9,a", "XPC=0", "A=9,XPC=2"),
    ("st_add_parallel", " st a,*ar3 || add *ar5+0%,b", "A=ff84211000,B=1111,ASM=1,SXM=1,OVM=0,AR0=2,AR3=200,AR5=300,data#2:200=101,data#2:300=8001",
     "B=ff04221000,data#2:200=842,AR5=302,AR3=200"),                                                                             # ST||ADD example
    ("st_sub_parallel", " st a,*ar3- || sub *ar5+0%,b", "A=ff84210000,B=1000000001,ASM=1,SXM=1,AR0=2,AR3=1ff,AR5=300,data#2:1ff=1111,data#2:300=8001",
     "B=fffbe00000,data#2:1ff=842,AR5=302,AR3=1fe"),                                                                             # ST||SUB example
    # --- deliberately wrong (must be reported) ------------------------------------------------------------------
    ("XFAIL_add_wrong", " add *ar3+,14,a", "A=1200,C=1,AR3=100,SXM=1,data#2:100=1500", "A=0540001201"),
]
