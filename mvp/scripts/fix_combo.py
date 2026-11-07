import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/soc-t23/common/clk/clk.c"
s=io.open(p,encoding="utf-8").read()
old="\t\t/* per-item skip removed: T23ZN-DEFENSE in clk_cgu.c handles centrally */"
new="\t\tif(i == 54){prom_putstr((char*)\"SKIP-SSI0\\n\");continue;} /*SSI0 gate: parent CGU_SSI absent, gate-init path still hangs (defense covers CGU only)*/"
if old in s:
    s=s.replace(old,new,1); io.open(p,"w",encoding="utf-8").write(s); print("skip54 restored")
else: print("anchor miss")
