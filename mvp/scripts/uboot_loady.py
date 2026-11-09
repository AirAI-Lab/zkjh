#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Send a file to U-Boot with loady/Ymodem, optionally boot it."""
import argparse
import os
import time

import serial

SOH = 0x01
STX = 0x02
EOT = 0x04
ACK = 0x06
NAK = 0x15
CRC_CHAR = 0x43


def crc16(data):
    crc = 0
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if (crc & 0x8000) else (crc << 1)
            crc &= 0xFFFF
    return crc


def frame(block_no, payload, use_stx=None):
    if use_stx is None:
        use_stx = len(payload) == 1024
    start = STX if use_stx else SOH
    out = bytearray([start, block_no & 0xFF, ~(block_no & 0xFF) & 0xFF])
    out.extend(payload)
    crc = crc16(payload)
    out.extend([crc >> 8, crc & 0xFF])
    return bytes(out)


def drain(ser, seconds=0.2):
    end = time.time() + seconds
    out = b""
    while time.time() < end:
        data = ser.read(4096)
        if data:
            out += data
            end = time.time() + seconds
    return out


def wait_for(ser, accepted, timeout=15):
    end = time.time() + timeout
    seen = bytearray()
    while time.time() < end:
        data = ser.read(1)
        if not data:
            continue
        seen.extend(data)
        if data[0] in accepted:
            return data[0], bytes(seen)
    raise TimeoutError("waiting for %r, saw %r" % (accepted, bytes(seen)))


def pad(data, size):
    return data + bytes([0x1A]) * (size - len(data))


def ymodem_send(ser, path, log):
    payload = open(path, "rb").read()
    name = os.path.basename(path).encode()
    header = name + b"\0" + str(len(payload)).encode() + b"\0"
    header = pad(header, 128)

    print("[loady] waiting for receiver CRC request")
    char, noise = wait_for(ser, {CRC_CHAR})
    log.write("[receiver] %r %r\n" % (chr(char), noise))
    ser.write(frame(0, header, use_stx=False))
    ser.flush()
    char, noise = wait_for(ser, {ACK, NAK})
    if char != ACK:
        raise RuntimeError("header block rejected: %r %r" % (char, noise))
    char, _ = wait_for(ser, {CRC_CHAR})

    total = (len(payload) + 1023) // 1024
    started = time.time()
    for index in range(total):
        chunk = payload[index * 1024:(index + 1) * 1024]
        if len(chunk) < 1024:
            if len(chunk) < 128:
                chunk = pad(chunk, 128)
            else:
                chunk = pad(chunk, 1024)
        for attempt in range(10):
            ser.write(frame(index + 1, chunk))
            ser.flush()
            char, noise = wait_for(ser, {ACK, NAK})
            if char == ACK:
                break
            print("[loady] block %d/%d NAK, retry %d" % (index + 1, total, attempt + 1))
        else:
            raise RuntimeError("block %d rejected" % (index + 1))
        if (index + 1) % 32 == 0 or index + 1 == total:
            rate = (index + 1) * 1024 / max(time.time() - started, 0.001) / 1024
            print("[loady] %d/%d blocks, %.1f KiB/s" % (index + 1, total, rate))

    ser.write(bytes([EOT]))
    ser.flush()
    # Many Ymodem receivers NAK the first EOT and ACK the duplicate.
    try:
        char, _ = wait_for(ser, {ACK, NAK}, timeout=5)
        if char == NAK:
            ser.write(bytes([EOT]))
            ser.flush()
            wait_for(ser, {ACK}, timeout=5)
    except TimeoutError:
        pass

    char, _ = wait_for(ser, {CRC_CHAR}, timeout=5)
    ser.write(frame(0, bytes(128), use_stx=False))
    ser.flush()
    wait_for(ser, {ACK}, timeout=5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="COM6")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--addr", default="0x80600000")
    parser.add_argument("file")
    parser.add_argument("--boot", action="store_true", help="send bootm after transfer")
    args = parser.parse_args()

    with serial.Serial(args.port, args.baud, timeout=0.1) as ser:
        ser.write(b"\r\n")
        print(drain(ser, 0.5).decode("utf-8", "replace"), end="")
        cmd = "loady %s" % args.addr
        print(">>> " + cmd)
        ser.write((cmd + "\n").encode())
        ser.flush()
        ymodem_send(ser, args.file, open(os.devnull, "w"))
        print("[loady] transfer complete")
        if args.boot:
            cmd = "bootm %s" % args.addr
            print(">>> " + cmd)
            ser.write((cmd + "\n").encode())
            ser.flush()
            while True:
                data = ser.read(4096)
                if data:
                    print(data.decode("utf-8", "replace"), end="")


if __name__ == "__main__":
    main()
