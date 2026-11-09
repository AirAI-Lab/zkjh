#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wait for the JKD-621-T23 rescue shell and run the I2C0/TF smoke test."""
import argparse
import datetime
import os
import re
import sys
import time

import serial


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="COM6")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--timeout", type=float, default=240)
    parser.add_argument("--boot-command", help="optional U-Boot command to send immediately, e.g. boot")
    args = parser.parse_args()

    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(
        log_dir,
        "I2C_BRINGUP_%s.log" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
    )
    commands = [
        "echo ZKJH_SHELL_READY",
        "mkdir -p /mmc",
        "mount -t vfat /dev/mmcblk0p1 /mmc",
        "echo MOUNT_RC=$?",
        "ls -l /mmc",
        "/mmc/i2cscan 0",
        "echo ZKJH_I2C_DONE",
    ]

    started = time.time()
    shell_ready = False
    command_index = 0
    last_command_at = 0
    last_activity = started
    prompt = re.compile(r"\[root@Zeratul:~\]#\s*$")
    with serial.Serial(args.port, args.baud, timeout=0.1) as ser, open(
        log_path, "a", encoding="utf-8", errors="replace"
    ) as log:
        print("[auto] %s @ %d-8N1 -> %s" % (args.port, args.baud, log_path))
        log.write("===== I2C bring-up %s =====\n" % datetime.datetime.now().isoformat())
        log.flush()
        if args.boot_command:
            print(">>> " + args.boot_command)
            log.write(">>> %s\n" % args.boot_command)
            ser.write((args.boot_command + "\n").encode())
            ser.flush()
        while time.time() - started < args.timeout:
            data = ser.read(4096)
            if not data:
                if shell_ready and command_index < len(commands) and time.time() - last_command_at > 1.0:
                    cmd = commands[command_index]
                    print(">>> " + cmd)
                    log.write("\n>>> %s\n" % cmd)
                    ser.write((cmd + "\r\n").encode())
                    command_index += 1
                    last_command_at = time.time()
                if shell_ready and command_index == len(commands) and time.time() - last_command_at > 8:
                    print("[auto] smoke sequence complete")
                    log.write("\n===== smoke sequence complete =====\n")
                    break
                continue

            text = data.decode("utf-8", errors="replace")
            sys.stdout.write(text)
            sys.stdout.flush()
            log.write(text.replace("\r", ""))
            log.flush()
            last_activity = time.time()

            if b"Please press Enter" in data or "Please press Enter" in text:
                time.sleep(0.2)
                ser.write(b"\r\n")
            if not shell_ready and prompt.search(text.rstrip()):
                shell_ready = True
                last_command_at = 0

        else:
            print("[auto] timeout waiting for shell/smoke result")
            log.write("\n===== timeout =====\n")

    print("[auto] log: %s" % os.path.normpath(log_path))


if __name__ == "__main__":
    main()
