#!/bin/sh
# /etc/init.d/S99drivers - Load all drivers from initramfs
M=/lib/modules
echo "Loading drivers..."
/bin/busybox insmod $M/mmc_core.ko 2>&1
/bin/busybox insmod $M/jzmmc.ko 2>&1
/bin/busybox insmod $M/mmc_block.ko 2>&1
sleep 1
echo "MMC: $(ls /dev/mmcblk* 2>/dev/null)"
mkdir -p /mmc 2>/dev/null
/bin/busybox mount -t vfat /dev/mmcblk0p1 /mmc 2>&1
echo "TF: $(ls /mmc/ 2>/dev/null | grep -c .) files"
/bin/busybox insmod $M/jz_sfc.ko 2>&1
/bin/busybox insmod $M/squashfs.ko 2>&1
/bin/busybox insmod $M/jffs2.ko 2>&1
/bin/busybox insmod $M/sensor_tp9950_t23.ko 2>&1
echo "=== I2C ==="
ls /sys/bus/i2c/devices/
echo "=== Video ==="
ls /sys/class/video4linux/ 2>/dev/null
echo "=== TP9950 ==="
dmesg | /bin/busybox grep tp9950
echo "Drivers loaded."
