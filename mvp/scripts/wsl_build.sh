#!/bin/bash
# 修复 7z 解包时被忽略的符号链接 + 启动整包编译
set -e
ZK=/home/wennu/zkjh/Software
# kernel dts include 链接
mkdir -p $ZK/os/kernel/arch/mips/boot/dts/include
ln -sfn ../../../../../include/dt-bindings $ZK/os/kernel/arch/mips/boot/dts/include/dt-bindings
mkdir -p $ZK/os/kernel/arch/arm/boot/dts/include
ln -sfn ../../../../../include/dt-bindings $ZK/os/kernel/arch/arm/boot/dts/include/dt-bindings
# rootfs profiles 链接
ln -sfn /config/profiles $ZK/os/rootfs/5.4.0/camera/rootfs_camera/etc/profiles
ln -sfn /system/profiles $ZK/os/rootfs/5.4.0/camera/rootfs_camera_recovery/etc/profiles
ln -sfn /config/profiles/webrtc_profile.ini $ZK/os/rootfs/5.4.0/camera/rootfs_camera/etc/webrtc_profile.ini
echo "== symlinks fixed =="
cd $ZK
source .env
export PATH=/home/wennu/zkjh/toolchain/bin-gnu:$PATH
./build/check_toolchain.sh || true
echo "== start full build $(date) =="
./build/build_camera_all.sh 2>&1 | tail -200
echo "== build exit: $? $(date) =="
ls -la out/camera/ 2>/dev/null || true
