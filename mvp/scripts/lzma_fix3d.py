import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","fix3d_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial("COM6",115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[fix3d] 90s ESC storm - power on anytime")
buf=b""; t0=time.time(); prompt_at=None
while time.time()-t0<90:
    ser.write(b"\x1b")
    time.sleep(0.05)
    d=ser.read(4096)
    if d:
        buf+=d; out.write(d.decode("ascii","replace")); out.flush()
    if b"isvp_t23#" in buf[-200:] and b"Booting kernel" not in buf[-600:]:
        prompt_at=time.time(); break
if prompt_at is None:
    out.close(); ser.close(); print("NO PROMPT in 90s"); exit(1)
time.sleep(0.6); ser.reset_input_buffer()
print("[fix3d] prompt at %.1fs"%(prompt_at-t0))
def run(cmd,wait):
    ser.write((cmd+"\n").encode())
    t2=time.time(); b=b""
    while time.time()-t2<wait:
        d=ser.read(4096)
        if d: b+=d
    out.write(">>> %s\n%s\n"%(cmd,b.decode("ascii","replace"))); out.flush()
    return b
run("setenv verify no",2)
run("fatload mmc 0 0x80600000 uImage-fix3-lzma.bin",12)
run("bootm 0x80600000",20)
t3=time.time()
while time.time()-t3<110:
    d=ser.read(4096)
    if d: out.write(d.decode("ascii","replace")); out.flush()
ser.close(); out.close(); print("DONE")
