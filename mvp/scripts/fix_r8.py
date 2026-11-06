import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/soc-t23/common/clk/clk_cpccr.c"
s=io.open(p,encoding="utf-8").read()
if "R8P" not in s:
    if "extern void prom_putstr" not in s: s="extern void prom_putstr(char *s);\n"+s
    s=s.replace("\tunsigned long cpccr = cpm_inl(CPM_CPCCR);","\tunsigned long cpccr = cpm_inl(CPM_CPCCR);\n\t{char c8[2];c8[0]=(char)(80+CLK_CPCCR_NO(clk->flags)%16);c8[1]=0;prom_putstr(c8);}",1)
    s=s.replace("\tclk->rate = cpccr_get_rate(clk);","\tprom_putstr((char*)\"R8P1\\n\");\n\tclk->rate = cpccr_get_rate(clk);\n\tprom_putstr((char*)\"R8P2\\n\");",1)
    io.open(p,"w",encoding="utf-8").write(s); print("R8 patched")
else: print("already")
