import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/soc-t23/common/clk/clk.c"
s=io.open(p,encoding="utf-8").read()
if "CGU5:" not in s:
    old="""	if (clk->flags & CLK_FLG_PARENT) {
		id = CLK_PARENT(clk->flags);
		clk->parent = get_clk_from_id(id);
	} else {
		clk->parent = cgu_get_parent(clk);
	}
	no = CLK_CGU_NO(clk->flags);
	cgu_clks[no].cache = 0;
	clk->rate = cgu_get_rate(clk);
	if(cgu_is_enabled(clk)) {
		clk->flags |= CLK_FLG_ENABLE;
	}
"""
    new="""	{char cc[2];cc[0]=(char)(65+CLK_CGU_NO(clk->flags));cc[1]=0;prom_putstr(cc);}
	if (clk->flags & CLK_FLG_PARENT) {
		id = CLK_PARENT(clk->flags);
		clk->parent = get_clk_from_id(id);
	} else {
		clk->parent = cgu_get_parent(clk);
	}
	no = CLK_CGU_NO(clk->flags);
	prom_putstr((char*)"1");
	cgu_clks[no].cache = 0;
	prom_putstr((char*)"2");
	clk->rate = cgu_get_rate(clk);
	prom_putstr((char*)"3");
	if(cgu_is_enabled(clk)) {
		clk->flags |= CLK_FLG_ENABLE;
	}
	prom_putstr((char*)"4\\n");
"""
    if old in s:
        s=s.replace(old,new,1); io.open(p,"w",encoding="utf-8").write(s); print("round5 patched")
    else:
        print("init_cgu_clk pattern miss")
else: print("already")
