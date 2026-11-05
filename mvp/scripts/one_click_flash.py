#!/usr/bin/env python3
"""JKD-621-T23 一键烧录脚本
用法: 回来后 1.断电 2.上电 3.运行本脚本
脚本自动: 监听启动 → 打断autoboot → 加载固件 → 擦写NOR → 确认完成
"""
import serial, time, sys
sys.stdout.reconfigure(encoding='utf-8')

PORT = 'COM4'
BAUD = 115200
FW = 'zrt_soc_t23zn_tp9950_debug_fw.bin'
FLASH_CMD = ("setenv bootcmd ''; "
             "mw.b 0x80600000 0xff 0x1000000; "
             "fatload mmc 0 0x80600000 " + FW + "; "
             "sf probe; sf erase 0x0 0x1000000; "
             "sf write 0x80600000 0x0 0x1000000")

print('JKD-621-T23 One-Click Flasher')
print('=' * 50)
print('步骤:')
print('  1. 确认: 原始29.7GB TF卡在板上 + J16短接')
print('  2. 断电 → 等3秒 → 上电')
print('  3. 脚本自动完成烧录')
print('=' * 50)

ser = serial.Serial(PORT, BAUD, timeout=0.01)
print('\n[%s] 监听 %s @ %d ...' % (time.strftime('%H:%M:%S'), PORT, BAUD))
print('POWER OFF → POWER ON NOW!\n')

t0 = time.time()
all_rx = b''
flashed = False
done = False

try:
    while time.time() - t0 < 600:  # 10分钟超时
        d = ser.read(16384)
        if d:
            all_rx += d
            txt = d.decode('utf-8', 'replace')
            print(txt, end='', flush=True)

            # 打断autoboot
            if not flashed and (b'stop autoboot' in all_rx or b'autoboot' in all_rx):
                ser.write(b'\x03')  # Ctrl+C
                time.sleep(0.5)
                ser.write(b'\r\n')
                time.sleep(1)
                print('\n>>> AUTOBOOT INTERRUPTED <<<')
                ser.reset_input_buffer()
                ser.write((FLASH_CMD + '\n').encode())
                flashed = True
                t_flash = time.time()
                print('>>> FLASH COMMAND SENT <<<\n')

            # 提示符出现 → 发烧录命令
            if not flashed and b'isvp_t23#' in all_rx and time.time() - t0 > 3:
                print('\n>>> U-BOOT PROMPT FOUND <<<')
                ser.reset_input_buffer()
                ser.write((FLASH_CMD + '\n').encode())
                flashed = True
                t_flash = time.time()
                print('>>> FLASH COMMAND SENT <<<\n')

            # 烧录完成
            if flashed and b'isvp_t23#' in all_rx[-20:] and time.time() - t_flash > 30:
                done = True
                print('\n\n' + '=' * 50)
                print('FLASH COMPLETE!')
                print('=' * 50)
                print('\n下一步:')
                print('  1. 断电')
                print('  2. 取掉J16短接线')
                print('  3. 重新上电')
                print('  4. 观察UART1启动日志')
                break
        time.sleep(0.01)
except KeyboardInterrupt:
    print('\n[中断]')

if not done:
    print('\n[超时或未完成] RX=%dB flashed=%s' % (len(all_rx), flashed))

ser.close()