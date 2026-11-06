import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/soc-t23/common/clk/clk_gate.c"
s=io.open(p,encoding="utf-8").read()
s=s.replace("\tint bit = CLK_GATE_BIT(clk->flags);\n\tprom_putstr((char*)\"+\");","\tint bit = CLK_GATE_BIT(clk->flags);",1)
s=s.replace("\tif (clk->flags & CLK_FLG_PARENT) {","\tprom_putstr((char*)\"+\");\n\tif (clk->flags & CLK_FLG_PARENT) {",1)
io.open(p,"w",encoding="utf-8").write(s)
print("moved")
