import re, io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/soc-t23/common/clk/clk_cgu.c"
s=io.open(p,encoding="utf-8").read()
if "CGU-TO4" in s:
    print("already"); raise SystemExit
pat=re.compile(r"\twhile\(cpm_inl\(CPM_DDRCDR\) & 1 << 28\) \{[^}]*serial_put_hex[^}]*\n\t\}")
m=pat.search(s)
if not m:
    print("pattern miss"); raise SystemExit
new = "\t{int to=10000000;while(cpm_inl(CPM_DDRCDR) & 1 << 28) {if(--to<=0){prom_putstr((char*)\"CGU-TO4\\n\");break;}serial_put_hex(cpm_inl(CPM_DDRCDR));TCSM_PCHAR('\\r');TCSM_PCHAR('\\n');}}"
s=s[:m.start()]+new+s[m.end():]
io.open(p,"w",encoding="utf-8").write(s)
print("TO4 patched")
