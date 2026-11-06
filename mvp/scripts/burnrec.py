import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","burnrec_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial(__import__("os").environ.get("PORT","COM3"),115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[burnrec] wait prompt...")
buf=b""; t0=time.time()
while time.time()-t0<150:
    d=ser.read(4096)
    if d: buf+=d; out.write(d.decode("ascii","replace")); out.flush()
    if b"stop autoboot" in buf[-600:]:
        ser.write(b"\x1b"); time.sleep(0.05); ser.write(b"\r\n"); buf+=b"isvp_t23#"
    if b"isvp_t23#" in buf[-300:]: break
if b"isvp_t23#" not in buf[-300:]:
    out.close(); ser.close(); print("NO PROMPT"); exit(1)
time.sleep(0.3); ser.reset_input_buffer()
print("[burnrec] kernel -> recovery 0x898000 (3-seg) + bootcmd + boot")
BASE=0x898000
segs=[(0x80600000,0x200000),(0x80800000,0x58000),(0x80858000,0xa95c)]
cmds=[(b"fatload mmc 0 0x80600000 uImage-dbg.jzlzma\n",2.5,b"2500956 bytes read"),
      (b"sf probe\n",1.0,b"Detected"),
      (b"sf erase 0x898000 0x264000\n",12.0,b"Erased: OK")]
off=BASE
for src,ln in segs:
    cmds.append((("sf write 0x%x 0x%x 0x%x\n"% (src,off,ln)).encode(),3.0,b"isvp_t23#")); off+=ln
off=BASE
for src,ln in segs:
    cmds.append((("sf read 0x81600000 0x%x 0x%x\n"% (off,ln)).encode(),1.8,b"isvp_t23#"))
    cmds.append((("cmp.b 0x%x 0x81600000 0x%x\n"% (src,ln)).encode(),1.8,("otal of %d"%ln).encode())); off+=ln
bc = "setenv bootcmd 'sf probe; sf read 0x80600000 0x898000 0x200000; sf read 0x80800000 0xa98000 0x58000; sf read 0x80858000 0xaf0000 0xa95c; bootm 0x80600000'\n"
cmds.append((bc.encode(),1.5,b"isvp_t23#"))
cmds.append((b"saveenv\n",2.5,b"done"))
cmds.append((b"boot\n",18,b"Starting kernel"))
allok=True; lastcmp=b""
for cmd,w,expect in cmds:
    ser.write(cmd)
    t1=time.time(); b=b""
    while time.time()-t1<w:
        d=ser.read(4096)
        if d: b+=d; out.write(d.decode("ascii","replace")); out.flush()
    if b"cmp.b" in cmd: lastcmp=b
    if expect not in b:
        out.write("[FAIL] %s\n"%cmd.decode(errors="replace")); allok=False; break
# capture DBG output 60s
t2=time.time()
while time.time()-t2<60:
    d=ser.read(4096)
    if d: out.write(d.decode("ascii","replace")); out.flush()
ser.close(); out.close()
print("RESULT:","DONE" if allok else "FAILED")



