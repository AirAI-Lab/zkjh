import io, re
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/soc-t23/common/clk/clk_cgu.c"
s=io.open(p,encoding="utf-8").read()
# 1. remove header guard block
hdr=re.search(r"/\* T23ZN-DEFENSE.*?\n\}\n", s, re.S)
if hdr:
    s=s.replace(hdr.group(0),"",1)
# 2. insert guard fn right before cgu_clks table (CGU_SSI enum visible there)
anchor=s.find("[CGU_ISP]")
tbl_start=s.rfind("static", 0, anchor)
guard='''/* T23ZN-DEFENSE: SSI absent on T23ZN; central guard for all CGU access */
extern void prom_putstr(char *s);
static int t23zn_absent_cgu(int no)
{
	return no == CGU_SSI;
}

'''
if "t23zn_absent_cgu" not in s:
    s=s[:tbl_start]+guard+s[tbl_start:]
# 3. fix C90: move guard-call after declarations in the two funcs
s=s.replace("static unsigned long cgu_get_rate(struct clk *clk)\n{\n\tif(t23zn_absent_cgu(CLK_CGU_NO(clk->flags))) return 0; /*T23ZN-DEFENSE*/\n\tunsigned long x;\n\tunsigned long flags;\n\tint no = CLK_CGU_NO(clk->flags);",
"static unsigned long cgu_get_rate(struct clk *clk)\n{\n\tunsigned long x;\n\tunsigned long flags;\n\tint no = CLK_CGU_NO(clk->flags);\n\tif(t23zn_absent_cgu(no)) return 0; /*T23ZN-DEFENSE*/",1)
io.open(p,"w",encoding="utf-8").write(s)
print("fixed")
