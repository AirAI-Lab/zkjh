import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","burn_all_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial("COM4",115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
# wait prompt / interrupt
buf=b""; t0=time.time()
while time.time()-t0<90:
    d=ser.read(4096)
    if d: buf+=d; out.write(d.decode("ascii","replace")); out.flush()
    if b"stop autoboot" in buf[-600:]:
        ser.write(b"\x1b"); time.sleep(0.05); ser.write(b"\r\n"); buf+=b"isvp_t23#"
    if b"isvp_t23#" in buf[-300:]: break
if b"isvp_t23#" not in buf[-300:]:
    out.write("[NO PROMPT]"); out.close(); ser.close(); print("NO PROMPT"); exit(1)
time.sleep(0.3); ser.reset_input_buffer()
print("[prompt] one-shot burn...")
steps=[
 ("fatload mmc 0 0x80600000 uImage-early.jzlzma",12,b"2500832 bytes read"),
 ("sf probe",4,b"Detected"),
 ("sf write 0x80600000 0x898000 0x200000",12,b"Written: OK"),
 ("sf write 0x80800000 0xa98000 0x62600",8,b"Written: OK"),
 ("sf read 0x81600000 0x898000 0x200000",6,b"Read: OK"),
 ("cmp.b 0x80600000 0x81600000 0x200000",6,b"otal of 2097152"),
 ("sf read 0x81600000 0xa98000 0x62600",6,b"Read: OK"),
 ("cmp.b 0x80800000 0x81600000 0x62600",6,b"otal of 401408"),
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
    if not ok: allok=False; break
ser.close(); out.write("\nRESULT: %s\n"%("KERNEL COMPLETE" if allok else "FAILED")); out.close()
print("RESULT:","KERNEL COMPLETE" if allok else "FAILED")
