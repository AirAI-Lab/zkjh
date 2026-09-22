#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JH-TG5110-M1-22 甲烷传感器模拟器 (MVP 用, 按 ICD/说明书 D45 真实协议)
用法:
  交互:   python gas_sim.py --port COM3 [--baud 115200] [--interval 1.0]
  自检:   python gas_sim.py --selftest
运行中命令(回车发送):
  set <Vol%>   设置浓度, 如 set 3.20
  low / high / normal   快捷场景(0.80 / 3.20 / 0.00 %Vol)
  fault <码>   故障码, 如 fault 01
  drop / resume  停止/恢复上报
接法: USB-TTL 的 TX->模块RX(蓝), RX->模块TX(绿), GND 共地; 3.3V LVTTL
"""
import sys, time, threading, argparse, queue

sys.path.insert(0, r"D:\github\zkjh\mvp\sim")
from zk_codec import gas_build, gas_parse

class GasSim:
    def __init__(self, interval=1.0):
        self.conc = 0.00; self.t1 = 21.4; self.press = 1001.01
        self.t2 = 21.5; self.t3 = 21.6; self.fault = "00"
        self.interval = interval; self.active = True
        self.q = queue.Queue()   # 发送队列(模拟器 -> 串口)
        self.rx = queue.Queue()  # 串口 -> 模拟器(预留, 模块为主动上报)
    def frame(self):
        return gas_build(self.conc, self.t1, self.press, self.t2, self.t3, self.fault)
    def loop(self):
        while True:
            if self.active:
                self.q.put(self.frame())
            time.sleep(self.interval)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port"); ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--interval", type=float, default=1.0)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    sim = GasSim(a.interval)

    if a.selftest:
        for c in (0.0, 0.8, 3.2):
            sim.conc = c
            f = sim.frame(); r = gas_parse(f)
            print(f.strip().decode(), "->", r)
            assert r["checksum_ok"] and abs(r["conc"]-c) < 1e-6
        print("SELFTEST OK"); return

    ser = None
    if a.port:
        import serial  # pip install pyserial
        ser = serial.Serial(a.port, a.baud, timeout=0.1)

    t = threading.Thread(target=sim.loop, daemon=True); t.start()
    print("GasSim running", "on", a.port if ser else "(no port)", "- commands: set/low/high/normal/fault/drop/resume/quit")
    while True:
        try:
            f = sim.q.get_nowait()
            if ser: ser.write(f)
            else: print("TX:", f.strip().decode())
        except queue.Empty:
            pass
        # 交互命令(非阻塞)
        try:
            import msvcrt
            if msvcrt.kbhit():
                line = input().strip()
                if not line: continue
                cmd = line.split()
                if cmd[0] == "quit": break
                elif cmd[0] == "set": sim.conc = float(cmd[1])
                elif cmd[0] == "low": sim.conc = 0.80
                elif cmd[0] == "high": sim.conc = 3.20
                elif cmd[0] == "normal": sim.conc = 0.00; sim.fault = "00"
                elif cmd[0] == "fault": sim.fault = cmd[1]
                elif cmd[0] == "drop": sim.active = False
                elif cmd[0] == "resume": sim.active = True
                print(">>", line)
        except ImportError:
            pass
        time.sleep(0.05)
    if ser: ser.close()

if __name__ == "__main__":
    main()