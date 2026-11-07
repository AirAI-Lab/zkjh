import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/soc-t23/common/clk/clk_cgu.c"
s=io.open(p,encoding="utf-8").read()
s=s.replace("static int t23zn_absent_cgu(int no)\n{\n\treturn no == CGU_SSI;\n}",
"static int t23zn_absent_cgu(int no)\n{\n\treturn no == 2; /* CGU_SSI enum value: ISP=0,CIM=1,SSI=2 (clk.h) */\n}",1)
io.open(p,"w",encoding="utf-8").write(s)
print("hardcoded 2")
