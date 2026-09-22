#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JKD-621-T23 协议 Python 实现(与 common/*.c 互为跨语言校验)
1) gas: JH-TG5110-M1-22 激光甲烷模块 ASCII 帧 (115200-8N1 主动上报)
2) zk : HC32<->T23 二进制帧(CRC16-MODBUS)
校验说明: 说明书样例2按"前40字节XOR(含故障码+空格)"吻合(=23);
样例1(28)与任何前缀XOR均不符, 疑为文档笔误, 待厂家确认。MVP阶段统一按40字节实现。
"""
import struct

# ---------------- gas ----------------
GAS_CHK_SPAN = 40  # 0..39: 帧头..故障码+空格

def gas_checksum(payload: bytes) -> str:
    x = 0
    for b in payload[:GAS_CHK_SPAN]:
        x ^= b
    return str(x)[-2:]

def gas_build(conc: float, t1=21.4, press=1001.01, t2=21.5, t3=21.6, fault="00") -> bytes:
    body = "A{:+07.2f} {:+05.1f} {:07.2f} {:+05.1f} B{:+06.1f} {} XX".format(
        conc, t1, press, t2, t3, fault).encode("ascii")
    return body[:-2] + gas_checksum(body).encode() + b"\r\n"

def gas_parse(frame: bytes):
    f = frame.strip()
    assert f[0:1] == b"A", "bad head"
    parts = f.split(b" ")
    conc = float(parts[0][1:])
    t1 = float(parts[1]); press = float(parts[2])
    t2 = float(parts[3]); t3 = float(parts[4][1:])  # 去B前缀
    fault = parts[5].decode(); chk = parts[6].decode()
    ok = chk == gas_checksum(f)
    level = 2 if conc >= 2.5 else (1 if conc >= 0.5 else 0)
    return dict(conc=conc, t1=t1, press=press, t2=t2, t3=t3,
                fault=fault, checksum_ok=ok, level=level)

# ---------------- zk (HC32<->T23) ----------------
def zk_crc16(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc

def zk_pack(cmd: int, payload: bytes = b"") -> bytes:
    body = bytes([cmd]) + payload
    return bytes([0xAA, 0x55, len(body)]) + body + struct.pack("<H", zk_crc16(bytes([0xAA, 0x55, len(body)]) + body))

class ZkParser:
    def __init__(self):
        self.buf = b""
    def feed(self, data: bytes):
        self.buf += data
        out = []
        while True:
            r = self._try_frame()
            if r is None:
                break
            out.append(r)
        return out
    def _try_frame(self):
        b = self.buf
        if len(b) < 5:
            return None
        if b[0] != 0xAA or b[1] != 0x55:
            self.buf = b[1:]
            return self._try_frame()
        ln = b[2]
        if len(b) < 5 + ln:
            return None
        crc = struct.unpack("<H", b[3 + ln:5 + ln])[0]
        if zk_crc16(b[:3 + ln]) != crc:
            self.buf = b[1:]
            return self._try_frame()
        self.buf = b[5 + ln:]
        return (b[3], b[4:3 + ln])

if __name__ == "__main__":
    doc2 = b"A+002.01 -09.4 0829.00 +30.6 B+030.7 00 23\r\n"
    r = gas_parse(doc2)
    print("doc2:", r["conc"], "checksum_ok =", r["checksum_ok"], "level =", r["level"])
    assert r["checksum_ok"] and r["conc"] == 2.01 and r["level"] == 1
    f = gas_build(3.30, t1=-9.4, press=829.00, t2=30.6, t3=30.7)
    r = gas_parse(f)
    print("loopback:", f.strip().decode(), "->", r)
    assert r["conc"] == 3.30 and r["checksum_ok"] and r["level"] == 2
    p = ZkParser()
    got = p.feed(zk_pack(0x01, bytes([6, 2])) + zk_pack(0x30, b"\x07"))
    print("zk frames:", got)
    assert got == [(0x01, bytes([6, 2])), (0x30, b"\x07")]
    print("ALL SELF TESTS PASSED")