import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","burn_spl_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial("COM4",115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[burn-spl] wait power-on / prompt ...")
buf=b""; t0=time.time()
while time.time()-t0<120:
    d=ser.read(4096)
    if d: buf+=d; out.write(d.decode("ascii","replace")); out.flush()
    if b"stop autoboot" in buf[-600:]:
        ser.write(b"\x1b"); time.sleep(0.05); ser.write(b"\r\n"); buf+=b"isvp_t23#"
    if b"isvp_t23#" in buf[-300:]: break
if b"isvp_t23#" not in buf[-300:]:
    out.write("[NO PROMPT]"); out.close(); ser.close(); print("NO PROMPT"); exit(1)
time.sleep(0.3); ser.reset_input_buffer()
print("[prompt] burn SPL 251956B ...")
steps=[
 ("fatload mmc 0 0x80600000 u-boot-with-spl.bin",12,b"251956 bytes read"),
 ("sf probe",5,b"Detected"),
 ("sf erase 0x0 0x40000",15,b"Erased: OK"),
 ("sf write 0x80600000 0x0 0x3d834",10,b"Written: OK"),
 ("sf read 0x81600000 0x0 0x3d834",8,b"Read: OK"),
 ("cmp.b 0x80600000 0x81600000 0x3d834",8,b"otal of 251956"),
 ("reset",25,b"U-Boot"),
]
allok=True
for cmd,wait,expect in steps:
    ser.write((cmd+"\n").encode())
    t1=time.time(); b=b""
    while time.time()-t1<wait:
        d=ser.read(4096)
        if d: b+=d; out.write(d.decode("ascii","replace")); out.flush()
    ok=expect in b
    out.write("\n[%s] %s\n"%("OK" if ok else "FAIL",cmd)); out.flush()
    if not ok and cmd!="reset": allok=False; break
# capture post-reset banner+bootm
t2=time.time(); b2=b""
while time.time()-t2<20:
    d=ser.read(4096)
    if d: b2+=d; out.write(d.decode("ascii","replace")); out.flush()
ser.close(); out.write("\nRESULT: %s\n"%("SPL BURN OK" if allok else "FAILED")); out.close()
print("RESULT:","SPL BURN OK" if allok else "FAILED")
