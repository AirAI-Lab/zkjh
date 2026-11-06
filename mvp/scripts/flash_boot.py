import serial, time, sys, datetime, os
PORT="COM4"
LOGDIR=r"D:\github\zkjh\mvp\logs"
LOG=os.path.join(LOGDIR, "flashboot_%s.log" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
steps = [
    ("mw.b 0x80600000 0xff 0x40000", 4, None),
    ("fatload mmc 0 0x80600000 u-boot-with-spl.bin", 15, "bytes read"),
    ("sf probe", 6, "Detected"),
    ("sf erase 0x0 0x40000", 20, "Erased: OK"),
    ("sf write 0x80600000 0x0 0x40000", 20, "OK"),
    ("mw.b 0x81600000 0x0 0x40000", 4, None),
    ("sf read 0x81600000 0x0 0x40000", 10, "OK"),
    ("cmp.b 0x80600000 0x81600000 0x40000", 10, "otal of"),
]
ser = serial.Serial(PORT, 115200, timeout=0.05)
print("[flashboot] -> "+LOG)
ok_all = True
with open(LOG,"a",encoding="utf-8",errors="replace") as fp:
    def log(s): print(s); fp.write(s+"\n"); fp.flush()
    ser.write(b"\r\n"); time.sleep(0.5); ser.reset_input_buffer()
    for cmd, wait, expect in steps:
        log("\n>>> " + cmd)
        ser.write((cmd+"\n").encode())
        t0=time.time(); buf=b""
        while time.time()-t0 < wait:
            d=ser.read(4096)
            if d: buf+=d
        txt=buf.decode("ascii","replace")
        log(txt)
        if expect:
            if expect in txt:
                log("[STEP OK]")
            else:
                log("[STEP FAIL: expected '%s']" % expect); ok_all=False; break
        else:
            if "ERROR" in txt.upper():
                log("[STEP ERROR]"); ok_all=False; break
ser.close()
log("\nRESULT: " + ("ALL OK - NOR boot reflashed" if ok_all else "FAILED"))
