#!/bin/bash
set -euo pipefail

SOFTWARE=/home/wennu/zkjh/Software
ORIG=/tmp/zkjh-patch-orig
PATCH=/mnt/d/github/zkjh/mvp/patches/0001-t23zn-jkd621-clk-i2c-vfat.patch

rm -rf "$ORIG"
mkdir -p "$ORIG"
cd "$ORIG"
7z x -y "$SOFTWARE/os/kernel.7z" \
  kernel/arch/mips/configs/zeratul_SOC_T23_NOR_camera_IIC_V1_defconfig \
  kernel/arch/mips/xburst/core/prom.c \
  kernel/arch/mips/xburst/soc-t23/common/clk/clk.c \
  kernel/arch/mips/xburst/soc-t23/common/clk/clk_cgu.c \
  kernel/arch/mips/xburst/soc-t23/common/clk/clk_cpccr.c \
  kernel/arch/mips/xburst/soc-t23/common/clk/clk_gate.c \
  kernel/arch/mips/xburst/soc-t23/common/clk/clk_sources.c \
  >/dev/null

TMP=$(mktemp)
gen() {
  local rel=$1
  diff -u --label "a/$rel" --label "b/$rel" \
    "$ORIG/kernel/$rel" "$SOFTWARE/os/kernel/$rel" >> "$TMP" || true
}

: > "$TMP"
gen arch/mips/configs/zeratul_SOC_T23_NOR_camera_IIC_V1_defconfig
gen arch/mips/xburst/core/prom.c
gen arch/mips/xburst/soc-t23/common/clk/clk.c
gen arch/mips/xburst/soc-t23/common/clk/clk_cgu.c
gen arch/mips/xburst/soc-t23/common/clk/clk_cpccr.c
gen arch/mips/xburst/soc-t23/common/clk/clk_gate.c
gen arch/mips/xburst/soc-t23/common/clk/clk_sources.c

{
  cat <<'EOF'
From 0000000000000000000000000000000000000000 Mon Sep 17 00:00:00 2001
From: zkjh team <dev@example.com>
Date: 2026-11-09 15:24:00 +0800
Subject: [PATCH] T23ZN clock hardening and JKD-621 I2C/TF bring-up

- guard the absent T23ZN SSI CGU on rate/parent/init paths
- skip SSI0 gate and reparent it to EXT1
- bound CGU busy waits and remove temporary boot probes
- select I2C0 PA12/PA13, disable conflicting I2C1 PA16/PA17
- build VFAT into the kernel for the minimal rootfs
- synchronize the rescue initrd size
---
EOF
  cat "$TMP"
} > "$PATCH"

rm -f "$TMP"
echo "generated $PATCH ($(wc -l < "$PATCH") lines)"
