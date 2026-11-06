import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","rootfsburn_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial("COM6",115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[rootfs] 90s ESC storm...")
buf=b""; t0=time.time(); prompt=False
while time.time()-t0<90:
    ser.write(b"\x1b"); time.sleep(0.05)
    d=ser.read(4096)
    if d:
        buf+=d; out.write(d.decode("ascii","replace")); out.flush()
    if b"isvp_t23#" in buf[-200:] and b"Booting kernel" not in buf[-600:]:
        prompt=True; break
if not prompt:
    out.close(); ser.close(); print("NO PROMPT"); exit(1)
time.sleep(0.6); ser.reset_input_buffer()
print("[rootfs] burning 4-seg to 0x598000")
def run(cmd,wait,expect=None):
    ser.write((cmd+"\n").encode())
    t1=time.time(); b=b""
    while time.time()-t1<wait:
        d=ser.read(4096)
        if d: b+=d
    out.write(">>> %s\n%s\n"%(cmd,b.decode("ascii","replace"))); out.flush()
    return b
run("fatload mmc 0 0x80600000 rootfs-tp9950-debug.jzlzma",12)
run("sf probe",3)
# erase rootfs region
run("sf erase 0x598000 0x1b0000",10)
# 4 segments (1716937 = 0x1A32B9 -> segs 0x80000*3 + 0x232b9... compute: 3*0x80000=0x180000, rest=0x232b9)
segs=[(0x80600000,0x598000,0x80000),(0x80680000,0x618000,0x80000),(0x80700000,0x698000,0x80000),(0x80780000,0x718000,0x232b9)]
for src,off,ln in segs:
    r=run("sf write 0x%x 0x%x 0x%x"%(src,off,ln),6)
    if b"Written: OK" not in r:
        out.write("[SEG-FAIL] 0x%x\n"%off); out.flush(); print("SEG FAIL at 0x%x"%off); break
    time.sleep(0.1); ser.write(b"\r\n"); ser.read(1024)
for src,off,ln in segs:
    run("sf read 0x81600000 0x%x 0x%x"%(off,ln),4)
    r=run("cmp.b 0x%x 0x81600000 0x%x"%(src,ln),4)
    ok=("otal of %d"%ln).encode() in r
    out.write("[%s] cmp 0x%x\n"%("OK" if ok else "FAIL",off)); out.flush()
    print("cmp 0x%x:"%off,"OK" if ok else "FAIL")
ser.close(); out.close(); print("BURN DONE - power cycle to boot")
