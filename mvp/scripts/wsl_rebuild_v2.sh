#!/bin/bash
set -e
ZK=/home/wennu/zkjh/Software
cd $ZK
set -a; source .env; set +a
export PATH=/home/wennu/zkjh/toolchain/bin-gnu:$PATH

# TAG 已修改(无quiet), 重新构建完整固件
rm -f out/camera/tag.bin
./build/build_camera_all.sh > /tmp/zk_build_v2.log 2>&1
RC=$?
echo "BUILD EXIT=$RC $(date)"
ls -la out/*.bin 2>/dev/null
cp out/ZRT_SOC_T23ZN_TP9950_DIRECT_FW.bin /mnt/d/github/zkjh/mvp/releases/ZRT_SOC_T23ZN_TP9950_DEBUG_V2_FW.bin 2>/dev/null && echo "COPIED TO D:"