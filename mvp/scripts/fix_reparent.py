import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/soc-t23/common/clk/clk_sources.c"
s=io.open(p,encoding="utf-8").read()
old="DEF_CLK(SSI0,       GATE(6) | PARENT(CGU_SSI)),"
new="DEF_CLK(SSI0,       GATE(6) | PARENT(EXT1)), /*T23ZN: CGU_SSI absent; reparent to safe EXT1 to protect ops-enable path too*/"
if old in s:
    s=s.replace(old,new,1); io.open(p,"w",encoding="utf-8").write(s); print("SSI0 reparented to EXT1")
else: print("pattern miss")
