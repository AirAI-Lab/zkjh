#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JKD-621-T23 串口监控/上电日志采集工具
用法:
  python serial_monitor.py                    # 自动扫描 COM 口, 115200, 日志存 logs/
  python serial_monitor.py --port COM3        # 指定口
  python serial_monitor.py --list             # 列出所有串口
运行中: Ctrl+C 退出; 自动时间戳; 可选 --send "命令" 发送单条
"""
import sys, os, time, argparse, datetime
from serial.tools import list_ports as _list_ports

def list_ports():
    from serial.tools import list_ports
    for p in list_ports.comports():
        print("%-8s %s" % (p.device, p.description))

def monitor(port, baud, logfile, send=None):
    import serial
    ser = serial.Serial(port, baud, timeout=0.2)
    print("[serial_monitor] %s @ %d-8N1 -> %s (Ctrl+C 退出)" % (port, baud, logfile))
    if send:
        ser.write((send + "\r\n").encode())
        print("[sent] %s" % send)
    os.makedirs(os.path.dirname(logfile), exist_ok=True)
    t0 = time.time()
    with open(logfile, "a", encoding="utf-8", errors="replace") as fp:
        fp.write("\n===== session %s =====\n" % datetime.datetime.now().isoformat())
        fp.flush()
        while True:
            data = ser.read(4096)
            if data:
                txt = data.decode("utf-8", errors="replace")
                stamp = "[%7.2fs]" % (time.time() - t0)
                sys.stdout.write(txt); sys.stdout.flush()
                fp.write(stamp + " " + txt.replace("\r", ""))
                fp.flush()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port"); ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--send")
    a = ap.parse_args()
    if a.list:
        list_ports(); return
    port = a.port
    if not port:
        ports = [p.device for p in _list_ports.comports()]
        if not ports:
            print("未发现任何串口! 请插入 USB-TTL 并确认驱动(CH340/CP2102)。"); sys.exit(1)
        if len(ports) == 1:
            port = ports[0]
        else:
            print("发现多个串口, 请用 --port 指定:")
            for _p in _list_ports.comports(): print(_p.device, _p.description)
            sys.exit(1)
    log = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs",
                       "serial_%s_%s.log" % (port, datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
    try:
        monitor(port, a.baud, os.path.normpath(log), a.send)
    except KeyboardInterrupt:
        print("\n[exit] 日志已保存")

if __name__ == "__main__":
    main()