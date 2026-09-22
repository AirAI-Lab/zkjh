#!/bin/bash
# JKD-621-T23 MVP - WSL 环境搭建脚本 (在 Ubuntu WSL 中执行)
# 用法: bash /mnt/d/github/zkjh/mvp/scripts/wsl_setup_env.sh
set -e
ZK=/home/wennu/zkjh
TC=$ZK/toolchain/mips-gcc540-uclibc0.9.33.2-64bit-r3.3.0.smaller
TCG=$ZK/toolchain/bin-gnu

echo "== [1/6] 基础依赖 =="
for p in p7zip-full bzip2 lbzip2 build-essential bc libncurses-dev rsync; do
  dpkg -s $p >/dev/null 2>&1 || sudo apt-get install -y $p >/dev/null 2>&1 || true
done
command -v 7z || sudo apt-get install -y p7zip-full
command -v 7z

echo "== [2/6] SDK 拷贝检查 =="
[ -d $ZK/Software ] || { mkdir -p $ZK; cp -a /mnt/d/github/zkjh/Ingenic_Zeratul_T23_V4.0.0_20250605/Zeratul_Release_20250605/Software $ZK/; }
ls $ZK/Software | head -5

echo "== [3/6] 工具链 =="
if [ ! -d $TC ]; then
  mkdir -p $ZK/toolchain && cd $ZK/toolchain
  cp /mnt/d/github/zkjh/ISVP-T23-1.3.0-20250821/ISVP-T23-1.3.0-20250821/software/pc/toolchain/mips-gcc540-uclibc0.9.33.2-64bit-r3.3.0.smaller.tar.bz2 .
  tar xjf mips-gcc540-uclibc0.9.33.2-64bit-r3.3.0.smaller.tar.bz2
fi
mkdir -p $TCG; cd $TCG
for f in $TC/bin/mips-linux-uclibc-*; do b=$(basename "$f" | sed 's/uclibc/gnu/'); ln -sf "$f" "$b"; done
export PATH=$TCG:$PATH
mips-linux-gnu-gcc --version | head -1

echo "== [4/6] 生成 .env =="
cat > $ZK/Software/.env <<EOF
ZRT_ENV_TOP_DIR=$ZK/Software
ZRT_ENV_BUILD_TYPE=release
ZRT_ENV_FW_VERSION="ZRT_release_JKD621;[VERSION];ver=CAMERA_SOC_T23ZN_gc2053_V100;"
ZRT_ENV_UPDATE_VERSION=CAMERA_SOC_T23ZN_gc2053_5.4.0_V100
ZRT_ENV_BUILD_JOBS=$(nproc)
ZRT_ENV_BUILD_DIR=$ZK/Software/build
ZRT_ENV_OS_DIR=$ZK/Software/os
ZRT_ENV_TMP_DIR=
ZRT_ENV_OUT_DIR=$ZK/Software/out
ZRT_ENV_FW_DIR=
ZRT_ENV_USERLAND_DIR=$ZK/Software/userland
ZRT_ENV_TOOLS_DIR=$ZK/Software/tools
ZRT_ENV_DRIVERS_DIR=$ZK/Software/os/drivers
ZRT_ENV_SOC_TYPE=SOC_T23ZN
ZRT_ENV_FLASH_TYPE=NOR
ZRT_ENV_SENSOR_NUM=one
ZRT_ENV_I2C_NUM=
ZRT_ENV_SENSOR=gc2053
ZRT_ENV_SENSOR0=gc2053
ZRT_ENV_SENSOR1=
ZRT_ENV_SENSOR2=
ZRT_ENV_TRANSFER_MODE=IIC
ZRT_ENV_TOOL_CHAIN=5.4.0
ZRT_ENV_OUT_CAMERA_DIR=$ZK/Software/out/camera
ZRT_ENV_OUT_CAMERA_BOOT_FILE_PATH=$ZK/Software/out/camera/boot.bin
ZRT_ENV_OUT_CAMERA_TAG_FILE_PATH=$ZK/Software/out/camera/tag.bin
ZRT_ENV_OUT_CAMERA_KERNEL_FILE_PATH=$ZK/Software/out/camera/uImage.jzlzma
ZRT_ENV_OUT_CAMERA_ROOTFS_FILE_PATH=$ZK/Software/out/camera/rootfs_camera.cpio.recp
ZRT_ENV_OUT_CAMERA_RECOVERY_FILE_PATH=$ZK/Software/out/camera/recovery.bin
ZRT_ENV_OUT_CAMERA_SYSTEM_FILE_PATH=$ZK/Software/out/camera/system.bin
ZRT_ENV_OUT_CAMERA_CONFIG_FILE_PATH=$ZK/Software/out/camera/config.bin
EOF
echo "PATH=$TCG:\$PATH" >> $ZK/Software/.env
cat $ZK/Software/.env | head -3

echo "== [5/6] 解包 SDK =="
cd $ZK/Software
if [ ! -d os/kernel ]; then ./build/unpack_all.sh; else echo "already unpacked"; fi
ls os/

echo "== [6/6] 完成 =="
echo "后续编译: cd ~/zkjh/Software && source .env && ./build/build_camera_all.sh"
