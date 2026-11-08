import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/core/prom.c"
s=io.open(p,encoding="utf-8").read()
if "HARD-INITRD" not in s:
    old="void __init prom_init(void)\n{\n\tprom_init_cmdline((int)fw_arg0, (char **)fw_arg1);"
    new="void __init prom_init(void)\n{\n\textern unsigned long initrd_start, initrd_end;\n\tinitrd_start = 0x82000040UL; initrd_end = 0x8241A100UL; /*HARD-INITRD: uboot fatloads uInitrd@0x82000000(+64 hdr), size 0x41A0C0*/\n\tprom_init_cmdline((int)fw_arg0, (char **)fw_arg1);"
    if old in s:
        s=s.replace(old,new,1); io.open(p,"w",encoding="utf-8").write(s); print("HARD-INITRD patched")
    else: print("anchor miss")
else: print("already")
