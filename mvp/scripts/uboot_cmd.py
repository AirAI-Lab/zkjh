#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""U-Boot 交互工具: 发命令, 读回应, 存日志"""
import sys, time, datetime, serial

PORT = "COM4"
BAUD = 115200
LOG = r"D:\github\zkjh\mvp\logs\uboot_cmd_%s.log" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def run(cmds, wait_each=1.5, first_wait=0.5):
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
    out = []
    with open(LOG, "a", encoding="utf-8", errors="replace") as fp:
        def log(s):
            print(s, end="")
            fp.write(s); fp.flush()
        # 触发提示符
        ser.write(b"\r\n")
        time.sleep(first_wait)
        data = ser.read(8192)
        if data:
            log("[recv] " + data.decode("utf-8", "replace") + "\n")
        for c in cmds:
            log("\n[send] %s\n" % c)
            ser.write((c + "\n").encode())
            t0 = time.time()
            buf = b""
            while time.time() - t0 < wait_each:
                time.sleep(0.2)
                d = ser.read(4096)
                if d: buf += d
            if buf:
                log(buf.decode("utf-8", "replace") + "\n")
                out.append(buf.decode("utf-8", "replace"))
            else:
                log("(no response)\n")
                out.append("")
    ser.close()
    return out

if __name__ == "__main__":
    cmds = sys.argv[1:]
    run(cmds, wait_each=float(__import__("os").environ.get("WAIT", "1.5")))
    print("\n[saved] " + LOG)
