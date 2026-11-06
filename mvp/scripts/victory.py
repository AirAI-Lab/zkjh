import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","VICTORY_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial("COM6",115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[VICTORY] storm ready - POWER ON NOW")
buf=b""; t0=time.time(); prompt=False
while time.time()-t0<90:
    ser.write(b"\x1b"); time.sleep(0.03)
    d=ser.read(4096)
    if d:
        buf+=d; out.write(d.decode("ascii","replace")); out.flush()
    if b"isvp_t23#" in buf[-200:] and b"compression" in buf[-800:]:
        prompt=True; break
    if b"isvp_t23#" in buf[-100:] and b"U-Boot 2013" in buf and b"MMC" in buf:
        prompt=True; break
if not prompt:
    out.close(); ser.close(); print("NO PROMPT"); exit(1)
print("[VICTORY] prompt! firing in <1s...")
ser.reset_input_buffer()
ser.write(b"fatload mmc 0 0x80600000 uImage-fix3-lzma.bin\n")
time.sleep(3)
r1=ser.read(4096); out.write(r1.decode("ascii","replace")); out.flush()
print("fatload:",r1.decode("ascii","replace")[:70].replace("\n","|"))
if b"1674872 bytes read" not in r1:
    print("FATLOAD FAIL"); ser.close(); out.close(); exit(1)
ser.write(b"setenv verify no; bootm 0x80600000\n")
print("[VICTORY] kernel launching... 180s listen")
t2=time.time()
while time.time()-t2<180:
    d=ser.read(4096)
    if d: out.write(d.decode("ascii","replace")); out.flush()
ser.close(); out.close(); print("DONE")
