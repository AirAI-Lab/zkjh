import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","SHELL_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial("COM6",115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[SHELL] wait direct prompt (no autoboot)...")
buf=b""; t0=time.time(); last_ka=0
while time.time()-t0<90:
    now=time.time()
    if now-last_ka>3: ser.write(b"\r\n"); last_ka=now
    d=ser.read(4096)
    if d:
        buf+=d; out.write(d.decode("ascii","replace")); out.flush()
    if b"isvp_t23#" in buf[-300:]: break
if b"isvp_t23#" not in buf[-300:]:
    out.close(); ser.close(); print("NO PROMPT"); exit(1)
time.sleep(0.6); ser.reset_input_buffer()
print("[SHELL] FINAL BOOT: fix3 kernel + tp9950 rootfs")
def run(cmd,wait):
    ser.write((cmd+"\n").encode())
    t1=time.time(); b=b""
    while time.time()-t1<wait:
        d=ser.read(4096)
        if d: b+=d
    out.write(">>> %s\n%s\n"%(cmd,b.decode("ascii","replace"))); out.flush()
    return b
run("setenv verify no",2)
run("fatload mmc 0 0x80600000 uImage-fix3-lzma.bin",12)
run("bootm 0x80600000",20)
print("[SHELL] listening 180s...")
t2=time.time()
while time.time()-t2<180:
    d=ser.read(4096)
    if d: out.write(d.decode("ascii","replace")); out.flush()
ser.close(); out.close(); print("DONE")
