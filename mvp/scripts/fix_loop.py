import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/soc-t23/common/clk/clk_gate.c"
s=io.open(p,encoding="utf-8").read()
if "GATELOOP" not in s:
    s=s.replace("\tprom_putstr((char*)\"+\");\n\tif (clk->flags & CLK_FLG_PARENT) {",
"\tprom_putstr((char*)\"+\");\n\t{static int gc=0; if(gc++%4==0){char n0[4];int k;for(k=0;k<3&&clk->name[k];k++)n0[k]=clk->name[k];n0[k]=0;prom_putstr(n0);prom_putstr((char*)\"|\");}} /*GATELOOP*/\n\tif (clk->flags & CLK_FLG_PARENT) {",1)
    io.open(p,"w",encoding="utf-8").write(s); print("GATELOOP name-print patched")
else: print("already")
