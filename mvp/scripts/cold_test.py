import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","cold_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial("COM3",115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[cold] wait prompt after FULL discharge...")
buf=b""; t0=time.time(); last_ka=0
while time.time()-t0<180:
    now=time.time()
    if now-last_ka>12: ser.write(b"\r\n"); last_ka=now
    d=ser.read(4096)
    if d: buf+=d; out.write(d.decode("ascii","replace")); out.flush()
    if b"stop autoboot" in buf[-600:]:
        ser.write(b"\x1b"); time.sleep(0.05); ser.write(b"\r\n"); buf+=b"isvp_t23#"
    if b"isvp_t23#" in buf[-300:]: break
if b"isvp_t23#" not in buf[-300:]:
    out.close(); ser.close(); print("NO PROMPT"); exit(1)
time.sleep(0.4); ser.reset_input_buffer()
print("[cold] minimal diagnostic: fatload->write1->version->write2->version")
steps=[
 (b"fatload mmc 0 0x80600000 uImage-dbg.jzlzma\n",3.0,b"bytes read"),
 (b"sf probe\n",1.5,b"Detected"),
 (b"sf erase 0xb18000 0x80000\n",6.0,b"Erased: OK"),
 (b"sf write 0x80600000 0xb18000 0x80000\n",5.0,b"Written: OK"),
 (b"version\n",2.0,b"U-Boot"),          # ALIVE CHECK after write1
 (b"sf erase 0xb98000 0x80000\n",6.0,b"Erased: OK"),
 (b"sf write 0x80680000 0xb98000 0x80000\n",5.0,b"Written: OK"),
 (b"version\n",2.0,b"U-Boot"),          # ALIVE CHECK after write2
]
alive=[]
for cmd,w,expect in steps:
    ser.write(cmd)
    t1=time.time(); b=b""
    while time.time()-t1<w:
        d=ser.read(4096)
        if d: b+=d; out.write(d.decode("ascii","replace")); out.flush()
    ok=expect in b
    if cmd==b"version\n": alive.append(ok)
    out.write("[%s] %s\n"%("OK" if ok else "DEAD",cmd.decode().strip())); out.flush()
ser.close(); out.close()
print("after write1:", "ALIVE" if alive[0] else "DEAD")
print("after write2:", "ALIVE" if alive[1] else "DEAD")
