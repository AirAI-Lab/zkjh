import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/soc-t23/common/clk/clk_cgu.c"
s=io.open(p,encoding="utf-8").read()
if "static int t23zn_absent_cgu" not in s:
    anchor="#include <soc/cpm.h>"
    i=s.find(anchor)
    guard='\n/* T23ZN-DEFENSE: SSI absent on T23ZN silicon; central guard for ALL CGU access paths */\nextern void prom_putstr(char *s);\nstatic int t23zn_absent_cgu(int no)\n{\n\treturn no == CGU_SSI;\n}\n'
    s=s[:i+len(anchor)]+guard+s[i+len(anchor):]
    io.open(p,"w",encoding="utf-8").write(s)
    print("guard inserted after includes")
else: print("exists")
