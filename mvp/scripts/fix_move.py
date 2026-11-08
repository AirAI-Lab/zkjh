import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/xburst/core/prom.c"
s=io.open(p,encoding="utf-8").read()
s=s.replace("initrd_start = 0x82000000UL; initrd_end = 0x8241A0C0UL;","initrd_start = 0x81600000UL; initrd_end = 0x81A100C0UL;",1)
io.open(p,"w",encoding="utf-8").write(s); print("moved to 0x81600000")
