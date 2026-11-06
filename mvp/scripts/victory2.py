import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","V2_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial("COM6",115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[V2] storm...")
buf=b""; t0=time.time(); prompt=False
while time.time()-t0<90:
    ser.write(b"\x1b"); time.sleep(0.03)
    d=ser.read(4096)
    if d:
        buf+=d; out.write(d.decode("ascii","replace")); out.flush()
    if b"isvp_t23#" in buf[-200:]:
        prompt=True; break
if not prompt:
    out.close(); ser.close(); print("NO PROMPT"); exit(1)
# settle: stop storm, clear, confirm prompt
time.sleep(0.8); ser.reset_input_buffer()
ser.write(b"\r\n"); time.sleep(0.4)
c=ser.read(4096)
if b"isvp_t23#" not in c:
    ser.write(b"\r\n"); time.sleep(0.4); c+=ser.read(4096)
print("settle:",repr(c.decode("ascii","replace")[-40:]))
if b"isvp_t23#" not in c:
    print("UNSTABLE"); ser.close(); out.close(); exit(1)
ser.reset_input_buffer()
# fatload with echo verification
ser.write(b"fatload mmc 0 0x80600000 uImage-fix3-lzma.bin\n")
time.sleep(3)
r1=ser.read(4096); out.write(r1.decode("ascii","replace")); out.flush()
print("fatload:",r1.decode("ascii","replace")[:70].replace("\n","|"))
if b"1674872 bytes read" not in r1:
    print("FATLOAD FAIL"); ser.close(); out.close(); exit(1)
ser.write(b"setenv verify no; bootm 0x80600000\n")
print("[V2] listening 180s")
t2=time.time()
while time.time()-t2<180:
    d=ser.read(4096)
    if d: out.write(d.decode("ascii","replace")); out.flush()
ser.close(); out.close(); print("DONE")
