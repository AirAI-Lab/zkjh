import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","fix3c_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial("COM6",115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[fix3c] ESC-storm interrupt")
t0=time.time(); buf=b""
# storm ESC for 12s (covers bootdelay), stop at prompt
while time.time()-t0<12:
    ser.write(b"\x1b")
    time.sleep(0.03)
    d=ser.read(4096)
    if d:
        buf+=d; out.write(d.decode("ascii","replace")); out.flush()
        if b"isvp_t23#" in buf[-200:]:
            break
# gentle probing until prompt (max 120s)
t1=time.time()
while time.time()-t1<120 and b"isvp_t23#" not in buf[-200:]:
    ser.write(b"\r\n"); time.sleep(0.5)
    d=ser.read(4096)
    if d: buf+=d; out.write(d.decode("ascii","replace")); out.flush()
if b"isvp_t23#" not in buf[-300:]:
    out.close(); ser.close(); print("NO PROMPT"); exit(1)
time.sleep(0.5); ser.reset_input_buffer()
print("[fix3c] prompt OK")
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
b=run("bootm 0x80600000",20)
t3=time.time()
while time.time()-t3<110:
    d=ser.read(4096)
    if d: out.write(d.decode("ascii","replace")); out.flush()
ser.close(); out.close(); print("DONE")
