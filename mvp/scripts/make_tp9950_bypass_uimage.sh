#!/bin/bash
set -euo pipefail

KERNEL=/home/wennu/zkjh/Software/os/kernel
TOOLCHAIN=/home/wennu/zkjh/toolchain/bin-gnu
OUT=/mnt/d/github/zkjh/mvp/releases/uImage-mmc-lzma.bin
ENTRY=0xffffffff803c6660

export PATH="${TOOLCHAIN}:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
cd "$KERNEL"

# Patch only the two inlined version-read failure branches.  Do not run make
# after this point: relinking changes text layout and can move the kernel entry.
python3 /mnt/d/github/zkjh/mvp/scripts/patch_tp9950_vmlinux.py

rm -f arch/mips/boot/vmlinux.bin \
      arch/mips/boot/vmlinux.bin.lzma \
      arch/mips/boot/uImage.lzma

mips-linux-gnu-objcopy \
  -O binary \
  --remove-section=.reginfo \
  --remove-section=.mdebug \
  --remove-section=.comment \
  --remove-section=.note \
  --remove-section=.pdr \
  --remove-section=.options \
  --remove-section=.MIPS.options \
  vmlinux arch/mips/boot/vmlinux.bin

(cat arch/mips/boot/vmlinux.bin | lzma -9 && printf '\370\372\124\000') \
  > arch/mips/boot/vmlinux.bin.lzma

/bin/bash scripts/mkuboot.sh \
  -A mips -O linux -C lzma -T kernel \
  -a 0xffffffff80010000 -e "$ENTRY" \
  -n 'Linux-3.10.14-Archon' \
  -d arch/mips/boot/vmlinux.bin.lzma \
  arch/mips/boot/uImage.lzma

cp arch/mips/boot/uImage.lzma "$OUT"
mkimage -l "$OUT"
sha256sum "$OUT"
