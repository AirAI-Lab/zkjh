import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/soc-t23/common/clk/clk.c"
s=io.open(p,encoding="utf-8").read()
s=s.replace("\t\tif(i == 19){prom_putstr((char*)\"SKIP-SSI\\n\");continue;} /*SKIP-SSI: T23ZN no SSI CGU, get_rate bus-hang*/",
"\t\tif(i == 19 || i == 54){prom_putstr((char*)\"SKIP-SSI\\n\");continue;} /*SKIP SSI CGU(id19)+SSI0 gate(id54): T23ZN no SSI unit, any access bus-hangs*/",1)
io.open(p,"w",encoding="utf-8").write(s)
print("v2 skip")
