# MVP releases（2026-11-09）

> 统一使用本目录，不再使用 `final/` 子目录。

## 当前测试组合

| 文件 | 用途 | 状态 |
|---|---|---|
| `uImage-mmc-lzma.bin` | T23ZN ISP 测试内核：保持可启动布局并用二进制NOP忽略TP995x版本读NACK | 待上电复核 |
| `rootfs-ask.cpio` | 最小交互 rootfs，原 cpio，严禁 WSL 解包重打包 | 已验证 |
| `i2cscan` | MIPS I2C 总线扫描工具 | 已实测 `0x30` ACK |
| `i2creg` | MIPS I2C 寄存器读写工具 | 待拷贝到 TF 后读 ID/制式 |
| `isp_reprobe.ko` | 运行时 NOP 版本读失败分支，并通过 `/proc/isp_reprobe` 手工调用 `tx_isp_init` | A/B 隔离用 |
| `tag-tp9950-debug.bin` | TP9950 TAG 数据，ISP 阶段使用 | 保留 |

当前内核 SHA256：

```text
2E140BB7605F4C479D84293FD1E166E13B01FF21C854ED1D722F1852A7132FA4
```

## TF 卡 FAT 区

保留：

```text
uImage-mmc-lzma.bin
rootfs-ask.cpio
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
0x30 ACK
```

详细排障见 `../docs/06_T23ZN时钟与TP9950链路修复.md`。

> 该文件必须来自 `os/kernel/arch/mips/boot/uImage.lzma`，不能误用 header 为 LZ4 的 `uImage.jzlzma`。

