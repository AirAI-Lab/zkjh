import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/soc-t23/common/clk/clk_cgu.c"
s=io.open(p,encoding="utf-8").read()
# 1. get_parent: move guard after decls
s=s.replace("static struct clk * cgu_get_parent(struct clk *clk)\n{\n\tif(t23zn_absent_cgu(CLK_CGU_NO(clk->flags))) return NULL; /*T23ZN-DEFENSE*/\n\tunsigned int no,cgu,idx,pidx;\n\n\tno = CLK_CGU_NO(clk->flags);",
"static struct clk * cgu_get_parent(struct clk *clk)\n{\n\tunsigned int no,cgu,idx,pidx;\n\n\tno = CLK_CGU_NO(clk->flags);\n\tif(t23zn_absent_cgu(no)) return NULL; /*T23ZN-DEFENSE*/",1)
# 2. init_cgu_clk: guard after decls (keep R5 letter too)
s=s.replace("void __init init_cgu_clk(struct clk *clk)\n{\n\tif(t23zn_absent_cgu(CLK_CGU_NO(clk->flags))){prom_putstr((char*)\"DEF-SSI\\n\");return;} /*T23ZN-DEFENSE*/\n\tint no;\n\tint id;\n\t{char cc[2];cc[0]=(char)(65+CLK_CGU_NO(clk->flags));cc[1]=0;prom_putstr(cc);}",
"void __init init_cgu_clk(struct clk *clk)\n{\n\tint no;\n\tint id;\n\t{char cc[2];cc[0]=(char)(65+CLK_CGU_NO(clk->flags));cc[1]=0;prom_putstr(cc);}\n\tif(t23zn_absent_cgu(CLK_CGU_NO(clk->flags))){prom_putstr((char*)\"DEF-SSI\\n\");return;} /*T23ZN-DEFENSE*/",1)
io.open(p,"w",encoding="utf-8").write(s)
print("c90 fixed")
