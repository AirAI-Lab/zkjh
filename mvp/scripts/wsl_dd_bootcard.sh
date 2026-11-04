#!/bin/bash
# 将 SD 启动 uboot dd 到 TF 卡 17KB 偏移(官方烧录说明 1.1), 带磁盘安全选择+回读校验
# 用法: wsl_dd_bootcard.sh <期望容量GB>   (由 make_sd_bootcard_wsl.ps1 传入)
set -e
WANT_GB="${1:-29.7}"
UBOOT="/mnt/d/github/zkjh/mvp/releases/t23_sdcard_uboot_uart1.bin"
ROOT_DEV=$(findmnt -no SOURCE / | sed 's/[0-9]*$//')
[ -f "$UBOOT" ] || { echo "uboot not found: $UBOOT"; exit 1; }

# 候选 = 容量误差<5% 且非系统盘 且无挂载分区
CAND=""
while read -r name size type mnt; do
  dev="/dev/$name"
  sz_gb=$(echo "$size 1073741824" | awk '{printf "%.2f", $1/$2}')
  ok=$(echo "$sz_gb $WANT_GB" | awk '{d=$1-$2; if(d<0)d=-d; print (d/$2<0.05)?"1":"0"}')
  if [ "$type" = "disk" ] && [ "$ok" = "1" ] && [ "$dev" != "$ROOT_DEV" ] && [ -z "$mnt" ]; then
    CAND="$dev"
  fi
done < <(lsblk -nrbo NAME,SIZE,TYPE,MOUNTPOINT)

if [ -z "$CAND" ]; then
  echo "ABORT: no candidate disk ~${WANT_GB}GB found. lsblk:"; lsblk -o NAME,SIZE,TYPE,MOUNTPOINT; exit 1
fi
echo "target = $CAND ($(blockdev --getsize64 $CAND | awk '{printf "%.1fGB",$1/1073741824}'))"
read -p "type yes to dd uboot to $CAND : " ok
[ "$ok" = "yes" ] || { echo cancelled; exit 1; }

dd if="$UBOOT" of="$CAND" bs=1024 seek=17 conv=notrunc status=none
sync
# 回读校验
LEN=$(stat -c %s "$UBOOT")
if cmp -n "$LEN" <(dd if="$CAND" bs=1024 skip=17 count=$(( (LEN/1024)+1 )) status=none) "$UBOOT"; then
  echo "VERIFY OK - TF BOOT CARD READY"
  echo "next: hold BOOTSEL power-on, in uboot serial run:"
  echo "  mw.b 0x80600000 0xff 0x1000000"
  echo "  fatload mmc 0 0x80600000 ZRT_SOC_T23ZN_TP9950_DIRECT_FW.bin"
  echo "  sf probe;sf erase 0x0 0x1000000;sf write 0x80600000 0x0 0x1000000"
else
  echo "VERIFY FAILED - restore backup via logs/sd_backup_*.bin"; exit 1
fi