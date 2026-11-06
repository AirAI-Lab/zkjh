import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/soc-t23/common/clk/clk.c"
s=io.open(p,encoding="utf-8").read()
if "TOPHEX" not in s:
    # remove old tail hex (48-63)
    s=s.replace("\t\tif(i>=48&&i<64){char hx[2];hx[0]=(char)(i<58?48+i-48:87+i-58);hx[1]=0;prom_putstr(hx);}\n\t\tif(i%16==0){prom_putstr((char*)\".\");}","\t\tif(i%16==0){prom_putstr((char*)\".\");}",1)
    # add top hex for ALL i (compact: only i>=33)
    s=s.replace("\tfor(i = 0; i < clk_srcs_size; i++) {\n\t\tclk_srcs[i].CLK_ID = i;\n\t\tif(i == 19){","\tfor(i = 0; i < clk_srcs_size; i++) {\n\t\tclk_srcs[i].CLK_ID = i;\n\t\tif(i>=33){char tx[2];tx[0]=(char)(i<58?48+i-48:87+i-58);tx[1]=0;prom_putstr(tx);} /*TOPHEX*/\n\t\tif(i == 19){",1)
    io.open(p,"w",encoding="utf-8").write(s); print("TOPHEX patched")
else: print("already")
