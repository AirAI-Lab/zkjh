import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","nor_final_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial("COM3",115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[nor-final] wait 1188 prompt (J16 REMOVED)...")
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
    out.close(); ser.close(); print("NO PROMPT"); exit(1)
time.sleep(0.5); ser.reset_input_buffer()
print("[nor-final] single read + bootm on 1188")
ser.write(b"sf probe\n"); time.sleep(1.5); ser.read(4096)
ser.write(b"sf read 0x80600000 0xb18000 0x2629bc\n"); time.sleep(4)
r=ser.read(4096)
print("read:",r.decode("ascii","replace")[:120])
ser.write(b"bootm 0x80600000\n")
print("[nor-final] listening 120s for DBG markers...")
t2=time.time()
while time.time()-t2<120:
    d=ser.read(4096)
    if d: out.write(d.decode("ascii","replace")); out.flush()
ser.close(); out.close()
print("DONE")
