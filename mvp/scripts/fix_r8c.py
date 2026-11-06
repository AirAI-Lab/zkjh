import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/soc-t23/common/clk/clk_cpccr.c"
s=io.open(p,encoding="utf-8").read()
s=s.replace("static unsigned long cpccr_get_rate(struct clk *clk)\n{\n\tint sel;\n\tunsigned long cpccr = cpm_inl(CPM_CPCCR);\n\t{char c8[2];c8[0]=(char)(80+CLK_CPCCR_NO(clk->flags)%16);c8[1]=0;prom_putstr(c8);}\n\tunsigned int rate;",
"static unsigned long cpccr_get_rate(struct clk *clk)\n{\n\tint sel;\n\tunsigned long cpccr = cpm_inl(CPM_CPCCR);\n\tchar c8[2];\n\tc8[0]=(char)(80+CLK_CPCCR_NO(clk->flags)%16);c8[1]=0;prom_putstr(c8);\n\tunsigned int rate;",1)
io.open(p,"w",encoding="utf-8").write(s)
print("ok")
