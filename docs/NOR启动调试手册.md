
# JKD-621-T23 NOR启动调试手册 V1.0（2026-11-06）

> 适用：团队成员复现/继续内核启动调试。前置阅读 `docs/决策与历史记录.md` 2026-11-06 节。

## 1. 硬件与连接
| 项 | 值 |
|---|---|
| 串口 | J14: 1=UART1_TX→CH340 RXD, 2=RX→TXD, 3=GND, 115200-8N1 |
| J16(BOOT_SEL0) | 断开=NOR启动 / 短接=SD启动 |
| TF卡 | 仅29.7GB原卡可用（T23 ROM限制），布局见§3 |
| 监控 | python mvp/scripts/raw_monitor.py --port COM4（先开监控再上电！） |

## 2. 当前NOR分区（已验证可用状态）
```
0x000000  boot    257,040B  u-boot-hardlzma-sfcnor-1188.bin  勿动
0x040000  tag     360,448B  tag-tp9950-debug.bin
0x0598000 rootfs  (GC2053版, 未配套更新)
0x098000  kernel  (旧release内核)
0x0B18000 system  2,500,832B EARLY_PRINTK内核(#11)  bootcmd指向
NOR env:  bootcmd=三段sf read(见下)
```
三段bootcmd（绕单命令长度陷阱，0x2628E0 不等于 0x262600，长度必须精确）：
```
sf probe; sf read 0x80600000 0xb18000 0x200000; sf read 0x80800000 0xd18000 0x58000; sf read 0x80858000 0xd70000 0xa8e0; bootm 0x80600000
```

## 3. TF卡布局
- FAT分区(10MB起)：u-boot-hardlzma-sfcnor-1188.bin / uImage-early.jzlzma / tag-tp9950-debug.bin
- 裸扇区@17KB：SD启动uboot(t23_sdcard_uboot_uart1.bin)
- 裸扇区@3MB：内核uImage（供SD版autoboot mmc read）

## 4. 标准烧录流程（SD U-Boot下）
```
J16短接上电 → autoboot中断 → fatload文件 → sf probe → sf erase目标区 → sf write(分段不超512KB) → sf read回 → cmp.b校验
```
铁律：
1. 每步检查 isvp_t23# 回显（板子空闲约25秒自动重启，命令会发进死端口）
2. 写入长度按512KB分段（单命令大长度有陷阱史）
3. 长度十进制换算十六进制后回算验证（2500832=0x2628E0）

## 5. 启动验证（NOR）
断电→J16断开→上电，预期链：
```
U-Boot SPL(Nov 06 2026) → DDR 1188/600 → 三段读 → jzlzma解压OK
→ [0.000000]Linux version... → early0 enabled → ... → FPU revision(当前终点)
```

## 6. 已知坑速查
| 坑 | 现象 | 对策 |
|---|---|---|
| 官方boot.bin无jzlzma | Unimplemented compression type 5 | 只用自编1188版 |
| MP档时钟 | DDR 400M内核静默 | isvp_t23.h else分支已改1188/600 |
| 板子空闲自重启 | 命令无响应/乱码 | 每步活性校验+紧凑流程 |
| COM口漂移 | PermissionError | 每次前 [IO.Ports.SerialPort]::GetPortNames() |
| 用户串口助手抢占 | python收不到数据 | 关闭所有串口工具 |

## 7. 下一步任务（交接）
1. 内核挂点定位：arch/mips/kernel/setup.c setup_arch插桩 prom_putstr("S1\n") 逐段定位（挂点在FPU revision输出后）
2. TAG深校验：sensor区/i2c地址/时钟与内核期望比对
3. rootfs配套：GC2053版rootfs重打tp9950版
4. 跑通后：MVP最小闭环（定时唤醒→抓拍→TF缓存→回睡）

## 8. SDK环境（WSL ~/zkjh/Software）
- .env: BUILD_TYPE=debug, SENSOR=tp9950, BOARD_VERSION=V1, IVDC=un-direct, KERNEL_DIR已补
- 内核：bash -c "export PATH=$HOME/zkjh/toolchain/bin-gnu:$PATH; set -a; source .env; set +a; bash build/build_camera_uImage.sh"
- U-Boot：cd os/uboot/u-boot && make isvp_t23n_sfcnor_config && make -j20
