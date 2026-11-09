#!/usr/bin/env python3
"""Normalize T23ZN clock defenses and remove temporary boot-time probes.

Run from WSL:
    python3 /mnt/d/github/zkjh/mvp/scripts/clean_clock_debug.py
"""
from pathlib import Path

KERNEL = Path("/home/wennu/zkjh/Software/os/kernel")
CLK = KERNEL / "arch/mips/xburst/soc-t23/common/clk"


def clean_clk_c():
    path = CLK / "clk.c"
    text = path.read_text()
    text = text.replace("extern void prom_putstr(char *s);\n", "")
    start = text.index("void __init init_all_clk(void)")
    end = text.index("\nstruct clk *clk_get", start)
    replacement = """void __init init_all_clk(void)
{
	int i;
	struct clk *clk_srcs = get_clk_from_id(0);
	int clk_srcs_size = get_clk_sources_size();

	for(i = 0; i < clk_srcs_size; i++) {
		clk_srcs[i].CLK_ID = i;
		/* T23ZN has no SSI CGU. Skip the SSI0 gate so clock-tree init
		 * cannot reach its absent parent through gate operations. */
		if(i == CLK_ID_SSI0)
			continue;
		if(clk_srcs[i].flags & CLK_FLG_CPCCR)
			init_cpccr_clk(&clk_srcs[i]);
		if(clk_srcs[i].flags & CLK_FLG_CGU)
			init_cgu_clk(&clk_srcs[i]);
		if(clk_srcs[i].flags & CLK_FLG_PLL)
			init_ext_pll(&clk_srcs[i]);
		if(clk_srcs[i].flags & CLK_FLG_NOALLOC)
			init_ext_pll(&clk_srcs[i]);
		if(clk_srcs[i].flags & CLK_FLG_GATE)
			init_gate_clk(&clk_srcs[i]);
		if(clk_srcs[i].flags & CLK_FLG_ENABLE)
			clk_srcs[i].init_state = 1;
	}

	for(i = 0; i < clk_srcs_size; i++) {
		if(clk_srcs[i].parent && clk_srcs[i].init_state)
			init_clk_parent(clk_srcs[i].parent);
	}

	register_syscore_ops(&clk_pm_ops);
	register_pm_notifier(&clk_sleep_pm_notifier);
	printk("CCLK:%luMHz L2CLK:%luMhz H0CLK:%luMHz H2CLK:%luMhz PCLK:%luMhz\\n",
			clk_srcs[CLK_ID_CCLK].rate/1000/1000,
			clk_srcs[CLK_ID_L2CLK].rate/1000/1000,
			clk_srcs[CLK_ID_H0CLK].rate/1000/1000,
			clk_srcs[CLK_ID_H2CLK].rate/1000/1000,
			clk_srcs[CLK_ID_PCLK].rate/1000/1000);
}
"""
    path.write_text(text[:start] + replacement + text[end:])


def clean_clk_cgu():
    path = CLK / "clk_cgu.c"
    text = path.read_text()
    text = text.replace(
        "\n#include <linux/clk.h>\nextern void prom_putstr(char *s);\n"
        "#include <linux/spinlock.h>",
        "#include <linux/spinlock.h>",
        1,
    )
    old_guard = """/* T23ZN-DEFENSE: SSI absent on T23ZN silicon; central guard for ALL CGU access paths */
extern void prom_putstr(char *s);
static int t23zn_absent_cgu(int no)
{
	return no == 2; /* CGU_SSI enum value: ISP=0,CIM=1,SSI=2 (clk.h) */
}
"""
    new_guard = """/* T23ZN-DEFENSE: SSI CGU is absent on this silicon. Guard every rate,
 * parent and init path so no code path can touch CPM_SSICDR. */
#define CGU_BUSY_TIMEOUT 10000000
static int t23zn_absent_cgu(int no)
{
	return no == CGU_SSI;
}

static void cgu_wait_busy(unsigned int off, unsigned int busy)
{
	int timeout = CGU_BUSY_TIMEOUT;
	while(cpm_test_bit(busy, off)) {
		if(--timeout <= 0) {
			printk("CGU busy timeout: off=0x%08x busy=%u\\n", off, busy);
			break;
		}
	}
}
"""
    if old_guard in text:
        text = text.replace(old_guard, "", 1)
    elif new_guard in text:
        text = text.replace(new_guard, "", 1)
    else:
        raise RuntimeError("expected T23ZN guard block not found")
    include_clk_h = '#include "clk.h"\n'
    if include_clk_h not in text:
        raise RuntimeError("clk.h include not found")
    text = text.replace(include_clk_h, include_clk_h + "\n" + new_guard, 1)
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")

    timeout_patterns = {
        "{int to=10000000;while(cpm_test_bit(busy,cgu_clks[no].off)) {if(--to<=0){prom_putstr((char*)\"CGU-TO1\\n\");break;}printk(\"wait stable.[%d][%s]\\n\",__LINE__,clk->name);}}":
            "cgu_wait_busy(cgu_clks[no].off, busy);",
        "{int to=10000000;while(cpm_test_bit(busy,cgu_clks[no].off)){if(--to<=0){prom_putstr((char*)\"CGU-TO2\\n\");break;}printk(\"wait stable.[%d][%s]\\n\",__LINE__,clk->name);}}":
            "cgu_wait_busy(cgu_clks[no].off, busy);",
        "{int to=10000000;while(cpm_test_bit(busy,cgu_clks[no].off)){if(--to<=0){prom_putstr((char*)\"CGU-TO3\\n\");break;}printk(\"wait stable.[%d][%s]\\n\",__LINE__,clk->name);}}":
            "cgu_wait_busy(cgu_clks[no].off, busy);",
        "{int to=10000000;while(cpm_inl(CPM_DDRCDR) & 1 << 28) {if(--to<=0){prom_putstr((char*)\"CGU-TO4\\n\");break;}serial_put_hex(cpm_inl(CPM_DDRCDR));TCSM_PCHAR('\\r');TCSM_PCHAR('\\n');}}":
            "cgu_wait_busy(CPM_DDRCDR, 28);",
    }
    for old, new in timeout_patterns.items():
        if old in text:
            text = text.replace(old, new)

    old_init_debug = """	{char cc[2];cc[0]=(char)(65+CLK_CGU_NO(clk->flags));cc[1]=0;prom_putstr(cc);}
	if(t23zn_absent_cgu(CLK_CGU_NO(clk->flags))){prom_putstr((char*)"DEF-SSI\\n");return;} /*T23ZN-DEFENSE*/"""
    new_init_debug = """	if(t23zn_absent_cgu(CLK_CGU_NO(clk->flags)))
		return; /* T23ZN-DEFENSE */"""
    if old_init_debug in text:
        text = text.replace(old_init_debug, new_init_debug, 1)
    for marker in ('"1"', '"2"', '"3"', '"4\\n"'):
        text = text.replace("\t\tprom_putstr((char*)%s);\n" % marker, "\n")
        text = text.replace("\tprom_putstr((char*)%s);\n" % marker, "\n")
    path.write_text(text)


def clean_secondary_clk_files():
    cpccr = CLK / "clk_cpccr.c"
    text = cpccr.read_text()
    text = text.replace("extern void prom_putstr(char *s);\n", "")
    text = text.replace(
        "\tchar c8[2];\n"
        "\tc8[0]=(char)(80+CLK_CPCCR_NO(clk->flags)%16);c8[1]=0;"
        "prom_putstr(c8);\n",
        "",
    )
    text = text.replace("\tprom_putstr((char*)\"R8P1\\n\");\n", "")
    text = text.replace("\tprom_putstr((char*)\"R8P2\\n\");\n", "")
    cpccr.write_text(text)

    gate = CLK / "clk_gate.c"
    text = gate.read_text()
    text = text.replace("extern void prom_putstr(char *s);\n", "")
    text = text.replace("\tprom_putstr((char*)\"+\");\n", "")
    text = text.replace(
        "\t{static int gc=0; if(gc++%4==0){char n0[4];int k;"
        "for(k=0;k<3&&clk->name[k];k++)n0[k]=clk->name[k];n0[k]=0;"
        "prom_putstr(n0);prom_putstr((char*)\"|\");}} /*GATELOOP*/\n",
        "",
    )
    text = text.replace("\tprom_putstr((char*)\"p\");\n", "")
    text = text.replace("\tprom_putstr((char*)\"r\");\n", "")
    text = text.replace("\tprom_putstr((char*)\"g\\n\");\n", "")
    gate.write_text(text)


if __name__ == "__main__":
    clean_clk_c()
    clean_clk_cgu()
    clean_secondary_clk_files()
    print("T23ZN clock code normalized")
