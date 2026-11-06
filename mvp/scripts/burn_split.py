import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","burn_split_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial("COM4",115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
ser.write(b"\r\n"); time.sleep(0.5); ser.reset_input_buffer()
steps=[
 ("sf probe",6,b"Detected"),
 ("sf write 0x80600000 0x898000 0x200000",15,b"Written: OK"),   # 2MB
 ("sf write 0x80800000 0x8a98000 0x62600",10,b"Written: OK"),   # tail
 ("sf read 0x81600000 0x898000 0x200000",8,b"Read: OK"),
 ("cmp.b 0x80600000 0x81600000 0x200000",8,b"otal of 2097152"),
 ("sf read 0x81600000 0x8a98000 0x62600",8,b"Read: OK"),
 ("cmp.b 0x80800000 0x81600000 0x62600",8,b"otal of 401408"),
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
    ser.write(b"\r\n"); time.sleep(0.15); ser.read(2048)
ser.close(); out.write("\nRESULT: %s\n"%("SPLIT BURN OK" if allok else "FAILED")); out.close()
print("RESULT:","SPLIT BURN OK" if allok else "FAILED")
