import serial, time, io, datetime, os
PORT=os.environ.get("PORT","COM3")
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","blast_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial(PORT,115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[blast] wait prompt (COM%s)..."%PORT)
buf=b""; t0=time.time()
while time.time()-t0<150:
    if int(time.time()-t0)%6==0: ser.write(b"\r\n")
    d=ser.read(4096)
    if d: buf+=d; out.write(d.decode("ascii","replace")); out.flush()
    if b"stop autoboot" in buf[-600:]:
        ser.write(b"\x1b"); time.sleep(0.05); ser.write(b"\r\n"); buf+=b"isvp_t23#"
    if b"isvp_t23#" in buf[-300:]: break
if b"isvp_t23#" not in buf[-300:]:
    out.close(); ser.close(); print("NO PROMPT"); exit(1)
time.sleep(0.3); ser.reset_input_buffer()
print("[blast] fire ALL commands, then listen 100s")
script = b"""fatload mmc 0 0x80600000 uImage-dbg.jzlzma
sf probe
sf erase 0x898000 0x264000
sf write 0x80600000 0x898000 0x200000
sf write 0x80800000 0xa98000 0x58000
sf write 0x80858000 0xaf0000 0xa95c
sf read 0x81600000 0x898000 0x200000
cmp.b 0x80600000 0x81600000 0x200000
sf read 0x81600000 0xa98000 0x58000
cmp.b 0x80800000 0x81600000 0x58000
sf read 0x81600000 0xaf0000 0xa95c
cmp.b 0x80858000 0x81600000 0xa95c
setenv bootcmd 'sf probe; sf read 0x80600000 0x898000 0x200000; sf read 0x80800000 0xa98000 0x58000; sf read 0x80858000 0xaf0000 0xa95c; bootm 0x80600000'
saveenv
boot
"""
for line in script.split(b"\n"):
    if line.strip():
        ser.write(line+b"\n"); time.sleep(0.35)
print("[blast] all sent, listening...")
t2=time.time()
while time.time()-t2<100:
    d=ser.read(4096)
    if d: out.write(d.decode("ascii","replace")); out.flush()
ser.close(); out.close()
print("DONE - analyze blast log")
