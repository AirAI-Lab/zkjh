import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/soc-t23/common/clk/clk_gate.c"
s=io.open(p,encoding="utf-8").read()
if "R7" not in s:
    if "extern void prom_putstr" not in s:
        s="extern void prom_putstr(char *s);\n"+s
    s=s.replace("\tint bit = CLK_GATE_BIT(clk->flags);","\tint bit = CLK_GATE_BIT(clk->flags);\n\tprom_putstr((char*)\"+\");",1)
    s=s.replace("\tclk->rate = clk_get_rate(clk->parent);\n\tif(clkgr[bit / 32]","\tprom_putstr((char*)\"p\");\n\tclk->rate = clk_get_rate(clk->parent);\n\tprom_putstr((char*)\"r\");\n\tif(clkgr[bit / 32]",1)
    s=s.replace("\tclk->ops = &clk_gate_ops;","\tprom_putstr((char*)\"g\\n\");\n\tclk->ops = &clk_gate_ops;",1)
    io.open(p,"w",encoding="utf-8").write(s); print("R7 patched")
else: print("already")
