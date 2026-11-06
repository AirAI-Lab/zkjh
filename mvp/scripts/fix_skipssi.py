import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/soc-t23/common/clk/clk.c"
s=io.open(p,encoding="utf-8").read()
if "SKIP-SSI" not in s:
    old="\tfor(i = 0; i < clk_srcs_size; i++) {\n\t\tclk_srcs[i].CLK_ID = i;"
    new="\tfor(i = 0; i < clk_srcs_size; i++) {\n\t\tclk_srcs[i].CLK_ID = i;\n\t\tif(i == 19){prom_putstr((char*)\"SKIP-SSI\\n\");continue;} /*SKIP-SSI: T23ZN no SSI CGU, get_rate bus-hang*/"
    if old in s:
        s=s.replace(old,new,1); io.open(p,"w",encoding="utf-8").write(s); print("SKIP-SSI patched")
    else: print("loop pattern miss")
else: print("already")
