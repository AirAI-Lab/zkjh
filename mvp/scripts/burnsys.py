import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","burnsys_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial("COM4",115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[burnsys] wait prompt...")
buf=b""; t0=time.time()
while time.time()-t0<120:
    d=ser.read(4096)
    if d: buf+=d; out.write(d.decode("ascii","replace")); out.flush()
    if b"stop autoboot" in buf[-600:]:
        ser.write(b"\x1b"); time.sleep(0.05); ser.write(b"\r\n"); buf+=b"isvp_t23#"
    if b"isvp_t23#" in buf[-300:]: break
if b"isvp_t23#" not in buf[-300:]:
    out.close(); ser.close(); print("NO PROMPT"); exit(1)
time.sleep(0.3); ser.reset_input_buffer()
print("[burnsys] kernel -> 0xb18000 (system area)...")
BASE=0xb18000
segs=[(0x80600000,0x80000),(0x80680000,0x80000),(0x80700000,0x80000),
      (0x80780000,0x80000),(0x80800000,0x58000),(0x80858000,0xa600)]
steps=[("fatload mmc 0 0x80600000 uImage-early.jzlzma",12,b"2500832 bytes read"),
       ("sf probe",4,b"Detected"),
       ("sf erase 0x%x 0x263000"%BASE,15,b"Erased: OK")]
off=BASE
for src,ln in segs:
    steps.append(("sf write 0x%x 0x%x 0x%x"%(src,off,ln),8,b"Written: OK")); off+=ln
off=BASE
for src,ln in segs:
    steps.append(("sf read 0x81600000 0x%x 0x%x"%(off,ln),5,b"Read: OK"))
    steps.append(("cmp.b 0x%x 0x81600000 0x%x"%(src,ln),5,("otal of %d"%ln).encode())); off+=ln
steps += [
 ("setenv bootcmd 'sf probe; sf read 0x80600000 0x%x 0x262600; bootm 0x80600000'"%BASE,3,b"isvp_t23#"),
 ("saveenv",6,b"done"),
 ("printenv bootcmd",4,("0x%x"%BASE).encode()),
]
allok=True
for cmd,wait,expect in steps:
    ser.write((cmd+"\n").encode())
    t1=time.time(); b=b""
    while time.time()-t1<wait:
        d=ser.read(4096)
        if d: b+=d; out.write(d.decode("ascii","replace")); out.flush()
    ok=expect in b
    out.write("[%s] %s\n"%("OK" if ok else "FAIL",cmd)); out.flush()
    if not ok: allok=False; break
    ser.write(b"\r\n"); time.sleep(0.08); ser.read(2048)
ser.close(); out.write("RESULT: %s\n"%("SYSTEM AREA BURN OK" if allok else "FAILED")); out.close()
print("RESULT:","SYSTEM AREA BURN OK" if allok else "FAILED")
