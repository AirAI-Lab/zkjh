#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Upload a small file to the JKD-621-T23 Linux shell over USB-TTL.

The kernel image is too large for the currently unreliable loady path, but a
6 KiB diagnostic kernel module can be transferred safely as shell printf hex.
Every binary byte is encoded as \\xHH, avoiding raw control characters.
"""
from pathlib import Path
import argparse
import hashlib
import sys
import time

import serial


def drain(serial_port, seconds=0.15):
    output = bytearray()
    deadline = time.time() + seconds
    while time.time() < deadline:
        data = serial_port.read(4096)
        if data:
            output.extend(data)
            deadline = time.time() + seconds
    return output.decode("utf-8", "replace")


def send_command(serial_port, command, wait=0.12):
    serial_port.write((command + "\r\n").encode("ascii"))
    serial_port.flush()
    return drain(serial_port, wait)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="COM6")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--file", default=r"D:\github\zkjh\mvp\releases\isp_reprobe.ko")
    parser.add_argument("--remote", default="/tmp/isp_reprobe.ko")
    parser.add_argument("--chunk", type=int, default=256)
    parser.add_argument("--insmod", action="store_true",
                        help="insmod after upload; do not trigger ISP reprobe")
    args = parser.parse_args()

    source = Path(args.file)
    payload = source.read_bytes()
    expected_md5 = hashlib.md5(payload).hexdigest()
    if len(payload) > 128 * 1024:
        raise SystemExit("refusing to transfer >128 KiB over 115200 shell")
    if args.chunk < 1 or args.chunk > 512:
        raise SystemExit("chunk must be 1..512 bytes")

    with serial.Serial(args.port, args.baud, timeout=0.1) as serial_port:
        serial_port.write(b"\r\n")
        serial_port.flush()
        initial = drain(serial_port, 1.0)
        print(initial, end="")
        if "root@Zeratul" not in initial:
            raise SystemExit("Root Shell not detected; power the known-good kernel first")

        send_command(serial_port, "stty -echo 2>/dev/null || true")
        send_command(serial_port, "rm -f %s" % args.remote)

        chunks = [payload[i:i + args.chunk] for i in range(0, len(payload), args.chunk)]
        for index, chunk in enumerate(chunks, 1):
            escaped = "".join("\\x%02x" % byte for byte in chunk)
            command = "printf '%%b' '%s' >> %s" % (escaped, args.remote)
            output = send_command(serial_port, command, 0.10)
            if "Syntax error" in output or "not found" in output:
                send_command(serial_port, "stty echo 2>/dev/null || true")
                raise SystemExit("target rejected chunk %d: %s" % (index, output))
            if index % 4 == 0 or index == len(chunks):
                print("uploaded %d/%d bytes" % (min(index * args.chunk, len(payload)), len(payload)))

        send_command(serial_port, "sync")
        result = send_command(
            serial_port,
            "ls -l %s; md5sum %s; echo UPLOAD_DONE" % (args.remote, args.remote),
            0.5,
        )
        send_command(serial_port, "stty echo 2>/dev/null || true")
        print(result, end="")

        if expected_md5 not in result:
            raise SystemExit("MD5 mismatch: expected %s" % expected_md5)
        print("UPLOAD_OK md5=%s" % expected_md5)

        if args.insmod:
            output = send_command(
                serial_port,
                "insmod %s; echo INSMOD_RC=$?; cat /proc/isp_reprobe; "
                "dmesg | grep isp_reprobe" % args.remote,
                1.0,
            )
            print(output, end="")
            if "INSMOD_RC=0" not in output:
                raise SystemExit("insmod failed")
            print("MODULE_READY; trigger manually with: echo 1 > /proc/isp_reprobe")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
