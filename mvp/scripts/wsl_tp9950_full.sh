#!/bin/bash
set -e
ZK=/home/wennu/zkjh/Software
rm -f $ZK/out/camera/uImage.jzlzma
find $ZK/out -maxdepth 1 -name '*.bin' -delete || true
cd $ZK
set -a; source .env; set +a
export PATH=/home/wennu/zkjh/toolchain/bin-gnu:$PATH
./build/build_camera_all.sh > /tmp/zk_build_tp9950.log 2>&1
RC=$?
echo "TP9950 BUILD EXIT=$RC $(date)"
tail -6 /tmp/zk_build_tp9950.log
ls -la $ZK/out/*.bin 2>/dev/null || true
SD=$ZK/os/drivers/sensor-t23/zeratul/single_camera/tp9950
cp $SD/sensor_tp9950_t23.ko /mnt/d/github/zkjh/mvp/t23app/ || true
cp $SD/tp9950.c /mnt/d/github/zkjh/mvp/t23app/tp9950_adapted.c || true
cp $ZK/out/ZRT_SOC_T23ZN_*.bin /mnt/d/github/zkjh/mvp/ 2>/dev/null || true
echo "--- delivered ---"
ls -la /mnt/d/github/zkjh/mvp/*.bin /mnt/d/github/zkjh/mvp/t23app/ 2>/dev/null || true