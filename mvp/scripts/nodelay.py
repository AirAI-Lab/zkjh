import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","nodelay_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial("COM6",115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[nodelay] storm + burn new boot")
buf=b""; t0=time.time(); prompt=False
while time.time()-t0<90:
    ser.write(b"\x1b"); time.sleep(0.03)
    d=ser.read(4096)
    if d:
        buf+=d; out.write(d.decode("ascii","replace")); out.flush()
    if b"isvp_t23#" in buf[-200:] and b"Booting kernel" not in buf[-600:]:
        prompt=True; break
if not prompt:
    out.close(); ser.close(); print("NO PROMPT"); exit(1)
time.sleep(0.6); ser.reset_input_buffer()
print("[nodelay] burning...")
def run(cmd,wait,expect=None):
    ser.write((cmd+"\n").encode())
    t1=time.time(); b=b""
    while time.time()-t1<wait:
        d=ser.read(4096)
        if d: b+=d
    out.write(">>> %s\n%s\n"%(cmd,b.decode("ascii","replace"))); out.flush()
    return b
run("fatload mmc 0 0x80600000 u-boot-1188-nodelay.bin",12)
run("sf probe",3)
run("mw.b 0x80600000 0xff 0x0",1)  # noop keepalive
run("sf erase 0x0 0x40000",15)
r=run("sf write 0x80600000 0x0 0x3ec10",8)
run("sf read 0x81600000 0x0 0x3ec10",6)
r2=run("cmp.b 0x80600000 0x81600000 0x3ec10",6)
ok=b"otal of 257024" in r2
print("BURN:", "OK" if ok else "FAIL")
ser.close(); out.close()
