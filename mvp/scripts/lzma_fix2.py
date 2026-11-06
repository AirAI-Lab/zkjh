import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","lzma_mem_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial("COM6",115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[lzma-mem] wait 1188 prompt (J16 open)...")
buf=b""; t0=time.time(); last_ka=0
while time.time()-t0<150:
    now=time.time()
    if now-last_ka>8: ser.write(b"\r\n"); last_ka=now
    d=ser.read(4096)
    if d: buf+=d; out.write(d.decode("ascii","replace")); out.flush()
    if b"stop autoboot" in buf[-600:]:
        ser.write(b"\x1b"); time.sleep(0.05); ser.write(b"\r\n"); buf+=b"isvp_t23#"
    if b"isvp_t23#" in buf[-300:]: break
if b"isvp_t23#" not in buf[-300:]:
    out.close(); ser.close(); print("NO PROMPT"); exit(1)
time.sleep(0.6); ser.reset_input_buffer()
print("[lzma-mem] fatload + bootm in RAM")
def run(cmd,wait):
    ser.write((cmd+"\n").encode())
    t1=time.time(); b=b""
    while time.time()-t1<wait:
        d=ser.read(4096)
        if d: b+=d
    out.write(">>> %s\n%s\n"%(cmd,b.decode("ascii","replace"))); out.flush()
    print(">>>",cmd,"->",b.decode('ascii','replace')[:90].replace("\n","|"))
    return b
run("setenv verify no",2)
run("fatload mmc 0 0x80600000 uImage-fix2-lzma.bin",12)
b=run("bootm 0x80600000",20)
print("listening 90s for DBG...")
t2=time.time()
while time.time()-t2<90:
    d=ser.read(4096)
    if d: out.write(d.decode("ascii","replace")); out.flush()
ser.close(); out.close(); print("DONE")

