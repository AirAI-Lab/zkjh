import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/soc-t23/common/clk/clk_cgu.c"
s=io.open(p,encoding="utf-8").read()
if "CCGU5" not in s:
    anchor="void __init init_cgu_clk(struct clk *clk)\n{\n\tint no;\n\tint id;"
    if anchor not in s:
        print("anchor miss"); raise SystemExit
    inject=anchor+"""
	{char cc[2];cc[0]=(char)(65+CLK_CGU_NO(clk->flags));cc[1]=0;prom_putstr(cc);}"""
    s=s.replace(anchor,inject,1)
    s=s.replace("\tno = CLK_CGU_NO(clk->flags);\n\tcgu_clks[no].cache = 0;\n\tclk->rate = cgu_get_rate(clk);\n\tif(cgu_is_enabled(clk)) {",
"\tno = CLK_CGU_NO(clk->flags);\n\tprom_putstr((char*)\"1\");\n\tcgu_clks[no].cache = 0;\n\tprom_putstr((char*)\"2\");\n\tclk->rate = cgu_get_rate(clk);\n\tprom_putstr((char*)\"3\");\n\tif(cgu_is_enabled(clk)) {",1)
    s=s.replace("\t\tclk->flags |= CLK_FLG_ENABLE;\n\t}\n\n\tif(no == CGU_MSC_MUX)",
"\t\tclk->flags |= CLK_FLG_ENABLE;\n\t}\n\tprom_putstr((char*)\"4\\n\");\n\n\tif(no == CGU_MSC_MUX)",1)
    io.open(p,"w",encoding="utf-8").write(s); print("r5 patched clk_cgu.c")
else: print("already")
