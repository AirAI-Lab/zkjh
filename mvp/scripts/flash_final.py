import serial, time, datetime, os
PORT="COM4"
LOG=os.path.join(r"D:\github\zkjh\mvp\logs", "flash_final_%s.log" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
steps = [
    # burn boot 1188
    ("mw.b 0x80600000 0xff 0x40000", 4, None),
    ("fatload mmc 0 0x80600000 u-boot-hardlzma-sfcnor-1188.bin", 15, "bytes read"),
    ("sf probe", 6, "Detected"),
    ("sf erase 0x0 0x40000", 20, "Erased: OK"),
    ("sf write 0x80600000 0x0 0x40000", 20, "OK"),
    ("sf read 0x81600000 0x0 0x3ec10", 12, "OK"),
    ("cmp.b 0x80600000 0x81600000 0x3ec10", 10, "otal of 257040"),
    # burn new kernel to recovery area
    ("fatload mmc 0 0x80600000 uImage-early.jzlzma", 15, "bytes read"),
    ("sf erase 0x898000 0x263000", 30, "Erased: OK"),
    ("sf write 0x80600000 0x898000 0x262600", 30, "OK"),
    ("sf read 0x81600000 0x898000 0x262600", 15, "OK"),
    ("cmp.b 0x80600000 0x81600000 0x262600", 12, "otal of 2500832"),
    ("reset", 8, "U-Boot"),
]
ser=serial.Serial(PORT,115200,timeout=0.05)
print("[flash-final] -> "+LOG)
ok=True
with open(LOG,"a",encoding="utf-8",errors="replace") as fp:
    def log(s): print(s); fp.write(s+"\n"); fp.flush()
    ser.write(b"\r\n"); time.sleep(0.5); ser.reset_input_buffer()
    for cmd,wait,expect in steps:
        log("\n>>> "+cmd)
        ser.write((cmd+"\n").encode())
        t0=time.time(); buf=b""
        while time.time()-t0<wait:
            d=ser.read(4096)
            if d: buf+=d
        log(buf.decode("ascii","replace"))
        if expect:
            if expect.encode() in buf: log("[OK]")
            else: log("[FAIL exp %s]"%expect); ok=False; break
ser.close()
log("RESULT: "+("ALL DONE" if ok else "FAILED"))
