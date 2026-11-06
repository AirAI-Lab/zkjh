import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/soc-t23/common/clk/clk.c"
s=io.open(p,encoding="utf-8").read()
if "R6:" not in s:
    # loop1 tail: idx 48-63 hex chars
    old1="\t\tif(i%16==0){prom_putstr((char*)\".\");}\n\t}"
    new1="\t\tif(i>=48&&i<64){char hx[2];hx[0]=(char)(i<58?48+i-48:87+i-58);hx[1]=0;prom_putstr(hx);}\n\t\tif(i%16==0){prom_putstr((char*)\".\");}\n\t}"
    if old1 in s: s=s.replace(old1,new1,1)
    else: print("loop1-tail pattern miss")
    # loop2: every parent-init call logs hex index
    old2="\t\tif(clk_srcs[i].parent && clk_srcs[i].init_state)\n\t\t\tinit_clk_parent(clk_srcs[i].parent);\n\t\tif(i%16==0){prom_putstr((char*)\"o\");}"
    new2="\t\tif(clk_srcs[i].parent && clk_srcs[i].init_state){char hx2[2];hx2[0]=(char)(i<58?48+i-48:87+i-58);hx2[1]=0;prom_putstr(hx2);init_clk_parent(clk_srcs[i].parent);prom_putstr((char*)\" \");}\n\t\tif(i%16==0){prom_putstr((char*)\"o\");}"
    if old2 in s: s=s.replace(old2,new2,1)
    else: print("loop2 pattern miss")
    s=s.replace("\tprom_putstr((char*)\"\\nK2:loop1-done\\n\");","\tprom_putstr((char*)\"\\nR6:loop1-done\\n\");",1)
    io.open(p,"w",encoding="utf-8").write(s); print("R6 patched")
else: print("already")
