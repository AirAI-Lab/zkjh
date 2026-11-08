import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/core/prom.c"
s=io.open(p,encoding="utf-8").read()
s=s.replace("initrd_start = 0x82000040UL; initrd_end = 0x8241A100UL; /*HARD-INITRD: uboot fatloads uInitrd@0x82000000(+64 hdr), size 0x41A0C0*/",
"initrd_start = 0x82000000UL; initrd_end = 0x8241A0C0UL; /*HARD-INITRD: page-aligned raw cpio via fatload rootfs.cpio, size 0x41A0C0*/",1)
io.open(p,"w",encoding="utf-8").write(s)
print("aligned")
