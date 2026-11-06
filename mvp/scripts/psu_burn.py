import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","psu_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial("COM3",115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[psu] wait prompt (stable 3.9V PSU)...")
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
print("[psu] full burn + boot sequence...")
script = b"""fatload mmc 0 0x80600000 uImage-dbg.jzlzma
sf probe
sf erase 0xb18000 0x200000
sf erase 0xd18000 0x64000
sf write 0x80600000 0xb18000 0x80000
sf write 0x80680000 0xb98000 0x80000
sf write 0x80700000 0xc18000 0x80000
sf write 0x80780000 0xc98000 0x80000
sf write 0x80800000 0xd18000 0x58000
sf write 0x80858000 0xd70000 0xa95c
sf read 0x81600000 0xb18000 0x80000
cmp.b 0x80600000 0x81600000 0x80000
sf read 0x81600000 0xb98000 0x80000
cmp.b 0x80680000 0x81600000 0x80000
sf read 0x81600000 0xc18000 0x80000
cmp.b 0x80700000 0x81600000 0x80000
sf read 0x81600000 0xc98000 0x80000
cmp.b 0x80780000 0x81600000 0x80000
sf read 0x81600000 0xd18000 0x58000
cmp.b 0x80800000 0x81600000 0x58000
sf read 0x81600000 0xd70000 0xa95c
cmp.b 0x80858000 0x81600000 0xa95c
setenv bootcmd 'sf probe; sf read 0x80600000 0xb18000 0x200000; sf read 0x80800000 0xd18000 0x58000; sf read 0x80858000 0xd70000 0xa95c; bootm 0x80600000'
saveenv
reset
"""
for line in script.split(b"\n"):
    if line.strip():
        ser.write(line+b"\n"); time.sleep(0.45)
print("[psu] all sent, listening 130s for DBG markers...")
t2=time.time()
while time.time()-t2<130:
    d=ser.read(4096)
    if d: out.write(d.decode("ascii","replace")); out.flush()
ser.close(); out.close()
print("DONE")
