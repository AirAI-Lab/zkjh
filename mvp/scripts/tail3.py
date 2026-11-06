import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","tail3_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial("COM3",115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[tail3] wait prompt...")
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
print("[tail3] write only 2 segs + verify + reset")
script = b"""fatload mmc 0 0x80600000 uImage-dbg.jzlzma
sf probe
sf write 0x80800000 0xd18000 0x58000
sf write 0x80858000 0xd70000 0xa95c
sf read 0x81600000 0xd18000 0x58000
cmp.b 0x80800000 0x81600000 0x58000
sf read 0x81600000 0xd70000 0xa95c
cmp.b 0x80858000 0x81600000 0xa95c
reset
"""
for line in script.split(b"\n"):
    if line.strip():
        ser.write(line+b"\n"); time.sleep(0.5)
print("[tail3] sent, listening 120s...")
t2=time.time()
while time.time()-t2<120:
    d=ser.read(4096)
    if d: out.write(d.decode("ascii","replace")); out.flush()
ser.close(); out.close()
print("DONE")
