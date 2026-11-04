#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""串口快速诊断: 打开->发回车/HELP->听N秒(带时间戳). 用法:
   python serial_diag.py --port COM3 [--listen 8] [--probe]
"""
import sys, time, argparse, datetime

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="COM3")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--listen", type=float, default=8.0)
    ap.add_argument("--probe", action="store_true", help="send ENTER/help probes")
    a = ap.parse_args()
    import serial
    try:
        ser = serial.Serial(a.port, a.baud, timeout=0.2)
    except Exception as e:
        print("[FATAL] open %s failed: %s" % (a.port, e)); sys.exit(2)
    print("[OK] %s opened %d-8N1, listening %.0fs ..." % (a.port, a.baud, a.listen))
    t0 = time.time(); rx_total = 0
    def log(s):
        print("[%6.2fs] %s" % (time.time()-t0, s), flush=True)
    if a.probe:
        time.sleep(0.3)
        ser.write(b"\r\n");           log("TX: <ENTER>")
        time.sleep(1.0)
        ser.write(b"help\r\n");       log("TX: help")
        time.sleep(0.5)
        ser.write(b"version\r\n");    log("TX: version")
    while time.time()-t0 < a.listen:
        d = ser.read(512)
        if d:
            rx_total += len(d)
            log("RX(%d): %r" % (len(d), d))
    ser.close()
    print("[SUMMARY] rx_bytes=%d %s" % (rx_total, " <-- 有数据" if rx_total else "<-- 完全无输出"))
if __name__ == "__main__":
    main()