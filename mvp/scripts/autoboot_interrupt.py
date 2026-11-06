#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动中断 autoboot 并执行命令序列"""
import sys, time, serial, datetime, os

PORT = os.environ.get("PORT", "COM3")
CMDS = [c for c in sys.argv[1:]]
LOGDIR = r"D:\github\zkjh\mvp\logs"
os.makedirs(LOGDIR, exist_ok=True)
LOG = os.path.join(LOGDIR, "autoboot_%s.log" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

ser = serial.Serial(PORT, 115200, timeout=0.05)
print("[wait] 板子重新上电后自动中断 autoboot... 日志: " + LOG)

interrupted = False
booted = False
buf = b""
t0 = time.time()
with open(LOG, "a", encoding="utf-8", errors="replace") as fp:
    def log(s):
        print(s, end=""); sys.stdout.flush()
        fp.write(s); fp.flush()

    # 阶段1: 等待启动输出, 见倒计时立即打断
    while time.time() - t0 < 120:
        d = ser.read(4096)
        if d:
            buf += d
            log(d.decode("utf-8", "replace"))
        txt = buf.decode("utf-8", "replace")
        if ("stop autoboot" in txt or "boot in" in txt.lower()) and not interrupted:
            ser.write(b"\x1b")  # ESC
            time.sleep(0.05)
            ser.write(b"\r\n")
            interrupted = True
            log("\n[INTERRUPT SENT]\n")
        if "isvp_t23#" in txt and interrupted:
            break
        if time.time() - t0 > 90 and not interrupted:
            # 超时也试发回车
            ser.write(b"\r\n")

    # 阶段2: 执行命令
    if interrupted or "isvp_t23#" in buf.decode("utf-8", "replace"):
        time.sleep(0.5)
        ser.reset_input_buffer()
        for c in CMDS:
            log("\n[send] %s\n" % c)
            ser.write((c + "\n").encode())
            t1 = time.time()
            cb = b""
            while time.time() - t1 < 3.0:
                d = ser.read(4096)
                if d: cb += d
            log(cb.decode("utf-8", "replace") + "\n")
            time.sleep(0.2)
    else:
        log("\n[FAIL] 120s 内未检测到 U-Boot 提示符\n")

ser.close()
print("\n[done] " + LOG)

