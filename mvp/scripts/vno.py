import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","vno_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial("COM3",115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[vno] wait 1188 clean prompt...")
buf=b""; t0=time.time(); last_ka=0
while time.time()-t0<180:
    now=time.time()
    if now-last_ka>10: ser.write(b"\r\n"); last_ka=now
    d=ser.read(4096)
    if d: buf+=d; out.write(d.decode("ascii","replace")); out.flush()
    if b"stop autoboot" in buf[-600:]:
        ser.write(b"\x1b"); time.sleep(0.05); ser.write(b"\r\n"); buf+=b"isvp_t23#"
    if b"isvp_t23#" in buf[-300:]: break
if b"isvp_t23#" not in buf[-300:]:
    out.close(); ser.close(); print("NO 1188 PROMPT"); exit(1)
time.sleep(0.6); ser.reset_input_buffer()
print("[vno] verify=no + single read + bootm")
def run(cmd,wait):
    ser.write((cmd+"\n").encode())
    t1=time.time(); b=b""
    while time.time()-t1<wait:
        d=ser.read(4096)
        if d: b+=d
    out.write(">>> %s\n%s\n"%(cmd,b.decode("ascii","replace"))); out.flush()
    print(">>>",cmd,"->",b.decode('ascii','replace')[:70].replace("\n","|"))
    return b
run("setenv verify no",2)
run("saveenv",6)
run("sf probe",2)
run("sf read 0x80600000 0xb18000 0x2629bc",5)
b=run("bootm 0x80600000",18)
t2=time.time()
while time.time()-t2<100:
    d=ser.read(4096)
    if d: out.write(d.decode("ascii","replace")); out.flush()
ser.close(); out.close(); print("DONE")

