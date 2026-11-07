import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/soc-t23/common/clk/clk_cgu.c"
s=io.open(p,encoding="utf-8").read()
if "T23ZN-DEFENSE" not in s:
    guard = '''
/* T23ZN-DEFENSE: SSI unit absent on T23ZN silicon; any CGU reg access bus-hangs.
 * Central guard replaces per-callsite skips - protects kernel init AND drivers. */
#include <linux/clk.h>
extern void prom_putstr(char *s);
static int t23zn_absent_cgu(int no)
{
	return no == CGU_SSI;
}
'''
    s = guard + s
    # guard cgu_get_rate
    s=s.replace("static unsigned long cgu_get_rate(struct clk *clk)\n{",
"static unsigned long cgu_get_rate(struct clk *clk)\n{\n\tif(t23zn_absent_cgu(CLK_CGU_NO(clk->flags))) return 0; /*T23ZN-DEFENSE*/",1)
    # guard cgu_get_parent
    s=s.replace("static struct clk * cgu_get_parent(struct clk *clk)\n{",
"static struct clk * cgu_get_parent(struct clk *clk)\n{\n\tif(t23zn_absent_cgu(CLK_CGU_NO(clk->flags))) return NULL; /*T23ZN-DEFENSE*/",1)
    # guard init_cgu_clk
    s=s.replace("void __init init_cgu_clk(struct clk *clk)\n{",
"void __init init_cgu_clk(struct clk *clk)\n{\n\tif(t23zn_absent_cgu(CLK_CGU_NO(clk->flags))){prom_putstr((char*)\"DEF-SSI\\n\");return;} /*T23ZN-DEFENSE*/",1)
    io.open(p,"w",encoding="utf-8").write(s)
    print("T23ZN-DEFENSE patched")
else:
    print("already")
