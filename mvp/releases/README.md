# MVP releases（2026-11-09）

> 统一使用本目录，不再使用 `final/` 子目录。

## 当前测试组合

| 文件 | 用途 | 状态 |
|---|---|---|
| `uImage-mmc-lzma.bin` | T23ZN 测试内核：I2C0=PA12/13、I2C1 禁用、VFAT 内置、时钟防御收敛 | 待上电复核 |
| `rootfs-ask.cpio` | 最小交互 rootfs，原 cpio，严禁 WSL 解包重打包 | 已验证 |
| `sensor_tp9950_t23.ko` | TP9950 MIPI 驱动模块 | 已 insmod，待 I2C ACK |
| `i2cscan` | MIPS I2C 总线扫描工具 | 待 `0x44` ACK |
| `tag-tp9950-debug.bin` | TP9950 TAG 数据，ISP 阶段使用 | 保留 |

当前内核 SHA256：

```text
AF52D6767F083D0304FA5728B717DD8C0D6A7F3B18C1720A9FC55D1634D70119
```

## TF 卡 FAT 区

保留：

```text
uImage-mmc-lzma.bin
rootfs-ask.cpio
sensor_tp9950_t23.ko
i2cscan
tag-tp9950-debug.bin
```

raw@17KB 的 `t23_sdcard_uboot_uart1.bin` 已在既有卡上保留；不要用普通文件复制方式重建 raw 区。

## 上电验证

```bash
mkdir -p /mmc
mount -t vfat /dev/mmcblk0p1 /mmc
ls /mmc
/mmc/i2cscan 0
```

预期日志：

```text
i2c i2c-0: i2c0 register ok.
0x44 ACK
```

详细排障见 `../docs/06_T23ZN时钟与TP9950链路修复.md`。

