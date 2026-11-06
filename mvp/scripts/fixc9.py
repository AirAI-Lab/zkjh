import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","fixc9_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial("COM3",115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[fixc9] wait prompt...")
buf=b""; t0=time.time(); last_ka=0
while time.time()-t0<150:
    now=time.time()
    if now-last_ka>10: ser.write(b"\r\n"); last_ka=now
    d=ser.read(4096)
    if d: buf+=d; out.write(d.decode("ascii","replace")); out.flush()
    if b"stop autoboot" in buf[-600:]:
        ser.write(b"\x1b"); time.sleep(0.05); ser.write(b"\r\n"); buf+=b"isvp_t23#"
    if b"isvp_t23#" in buf[-300:]: break
if b"isvp_t23#" not in buf[-300:]:
    out.close(); ser.close(); print("NO PROMPT"); exit(1)
time.sleep(0.4); ser.reset_input_buffer()
print("[fixc9] verify & fix 0xc98000 segment")
script = b"""fatload mmc 0 0x80600000 uImage-dbg.jzlzma
sf probe
sf read 0x81600000 0xc98000 0x80000
cmp.b 0x80780000 0x81600000 0x80000
sf erase 0xc98000 0x80000
sf write 0x80780000 0xc98000 0x80000
sf read 0x81600000 0xc98000 0x80000
cmp.b 0x80780000 0x81600000 0x80000
reset
"""
for line in script.split(b"\n"):
    if line.strip():
        ser.write(line+b"\n"); time.sleep(0.5)
print("[fixc9] sent, listening 120s...")
t2=time.time()
while time.time()-t2<120:
    d=ser.read(4096)
    if d: out.write(d.decode("ascii","replace")); out.flush()
ser.close(); out.close()
print("DONE")
