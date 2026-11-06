import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","burndbg_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial("COM4",115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[burndbg] wait prompt (power cycle)...")
buf=b""; t0=time.time()
while time.time()-t0<150:
    d=ser.read(4096)
    if d: buf+=d; out.write(d.decode("ascii","replace")); out.flush()
    if b"stop autoboot" in buf[-600:]:
        ser.write(b"\x1b"); time.sleep(0.05); ser.write(b"\r\n"); buf+=b"isvp_t23#"
    if b"isvp_t23#" in buf[-300:]: break
if b"isvp_t23#" not in buf[-300:]:
    out.close(); ser.close(); print("NO PROMPT"); exit(1)
time.sleep(0.3); ser.reset_input_buffer()
print("[burndbg] burn instrumented kernel 3-seg + fix bootcmd + reset")
segs=[(0x80600000,0x200000),(0x80800000,0x58000),(0x80858000,0xa95c)]
steps=[("fatload mmc 0 0x80600000 uImage-dbg.jzlzma",12,b"2500956 bytes read"),
       ("sf probe",4,b"Detected"),
       ("sf erase 0xb18000 0x264000",15,b"Erased: OK")]
off=0xb18000
for src,ln in segs:
    steps.append(("sf write 0x%x 0x%x 0x%x"%(src,off,ln),8,b"isvp_t23#")); off+=ln
off=0xb18000
for src,ln in segs:
    steps.append(("sf read 0x81600000 0x%x 0x%x"%(off,ln),5,b"isvp_t23#"))
    steps.append(("cmp.b 0x%x 0x81600000 0x%x"%(src,ln),5,b"isvp_t23#")); off+=ln
steps+=[("setenv bootcmd 'sf probe; sf read 0x80600000 0xb18000 0x200000; sf read 0x80800000 0xd18000 0x58000; sf read 0x80858000 0xd70000 0xa95c; bootm 0x80600000'",3,b"isvp_t23#"),
        ("saveenv",6,b"done"),
        ("reset",18,b"Starting kernel")]
allok=True
for cmd,wait,expect in steps:
    ser.write((cmd+"\n").encode())
    t1=time.time(); b=b""
    while time.time()-t1<wait:
        d=ser.read(4096)
        if d: b+=d; out.write(d.decode("ascii","replace")); out.flush()
    ok=expect in b
    out.write("[%s] %s\n"%("OK" if ok else "FAIL",cmd)); out.flush()
    if not ok and cmd!="reset": allok=False; break
    ser.write(b"\r\n"); time.sleep(0.08); ser.read(2048)
# capture DBG kernel output 50s
t2=time.time()
while time.time()-t2<50:
    d=ser.read(4096)
    if d: out.write(d.decode("ascii","replace")); out.flush()
ser.close(); out.write("RESULT: %s\n"%("BURN+BOOT OK - check DBG markers" if allok else "FAILED")); out.close()
print("RESULT:","DONE" if allok else "FAILED")
