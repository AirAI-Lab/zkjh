import serial, time, io, datetime, os
PORT="COM4"
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","burn_kernel_v2_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial(PORT,115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[burn-v2] waiting for SD U-Boot prompt... (power on now)")
# wait for prompt
buf=b""; t0=time.time()
while time.time()-t0<120:
    d=ser.read(4096)
    if d:
        buf+=d; out.write(d.decode("ascii","replace")); out.flush()
    if b"isvp_t23#" in buf[-2000:]:
        break
    # interrupt autoboot when countdown appears
    if b"stop autoboot" in buf[-500:]:
        ser.write(b"\x1b"); time.sleep(0.05); ser.write(b"\r\n")
if b"isvp_t23#" not in buf[-2000:]:
    out.write("\n[FAIL] no prompt\n"); out.close(); ser.close(); print("NO PROMPT"); exit(1)
print("[prompt OK] burn kernel...")
time.sleep(0.5); ser.reset_input_buffer()
steps=[
 ("fatload mmc 0 0x80600000 uImage-early.jzlzma",18,b"bytes read"),
 ("sf probe",6,b"Detected"),
 ("sf erase 0x898000 0x263000",18,b"Erased: OK"),
 ("sf write 0x80600000 0x898000 0x262600",18,b"Written: OK"),
 ("sf read 0x81600000 0x898000 0x262600",10,b"Read: OK"),
 ("cmp.b 0x80600000 0x81600000 0x262600",12,b"otal of 2500832"),
]
allok=True
for cmd,wait,expect in steps:
    ser.write((cmd+"\n").encode())
    t1=time.time(); b=b""
    while time.time()-t1<wait:
        d=ser.read(4096)
        if d: b+=d; out.write(d.decode("ascii","replace")); out.flush()
    ok = expect in b
    out.write("\n[%s] %s\n"%("OK" if ok else "FAIL",cmd)); out.flush()
    if not ok: allok=False; break
    ser.write(b"\r\n"); time.sleep(0.2); ser.read(4096)  # keepalive
ser.close(); out.write("\nRESULT: %s\n"%("BURN OK" if allok else "FAILED")); out.close()
print("RESULT:", "BURN OK" if allok else "FAILED")
