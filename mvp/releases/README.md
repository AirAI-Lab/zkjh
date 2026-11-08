# releases/final 五件套说明 (2026-11-08)

## 当前可跑通组合(上电即root shell)

| 文件 | 用途 | 烧录位置 |
|---|---|---|
| uImage-moved-lzma.bin | 最终内核(T23ZN防御+skip54+reparent+硬initrd@0x81600000) | TF FAT |
| rootfs-ask.cpio | 最终rootfs(实体/init+静态dev+askfirst shell) | TF FAT |
| t23_sdcard_uboot_uart1.bin | SD启动uboot(救生索) | TF raw@17KB(17408) |
| u-boot-hardlzma-sfcnor-1188.bin | NOR版1188(备用) | NOR@0x0 |
| tag-tp9950-debug.bin | TAG(NOR启动用) | NOR@0x40000 |
| uInitrd | mkimage封装ramdisk(备用) | TF FAT |
| ZRT_FW.bin x2 | 原厂固件(参考) | - |

## 一键重建TF卡
1. raw@17KB: t23_sdcard_uboot_uart1.bin (scripts/raw_rebuild.ps1)
2. FAT: 拷贝 uImage-moved-lzma.bin + rootfs-ask.cpio
3. env@0x40400: scripts/envwritePS.ps1 (含CRC32)

## 上电流程
SD启动 -> autoboot: fatload内核+cpio -> bootm ->
内核启动 -> initramfs unpack -> busybox init -> rcS ->
"Please press Enter" -> [root@Zeratul:~]#
