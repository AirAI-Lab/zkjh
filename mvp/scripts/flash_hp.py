import serial, time, datetime, os
PORT="COM4"
LOG=os.path.join(r"D:\github\zkjh\mvp\logs", "flash_hp_%s.log" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
steps = [
    ("mw.b 0x80600000 0xff 0x40000", 4, None),
    ("fatload mmc 0 0x80600000 u-boot-hardlzma-sfcnor-hp.bin", 15, "bytes read"),
    ("sf probe", 6, "Detected"),
    ("sf erase 0x0 0x40000", 20, "Erased: OK"),
    ("sf write 0x80600000 0x0 0x40000", 20, "OK"),
    ("sf read 0x81600000 0x0 0x10", 8, "OK"),
    ("md.b 0x81600000 0x10", 6, "81600000:"),
]
ser = serial.Serial(PORT, 115200, timeout=0.05)
print("[flash-hp] -> "+LOG)
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
        log(buf.decode("ascii","replace"))
        if expect:
            if expect in buf.decode("ascii","replace"): log("[STEP OK]")
            else: log("[STEP FAIL]"); ok_all=False; break
        elif b"ERROR" in buf.upper():
            log("[STEP ERROR]"); ok_all=False; break
ser.close()
log("RESULT: " + ("HP FLASH DONE" if ok_all else "FAILED"))
