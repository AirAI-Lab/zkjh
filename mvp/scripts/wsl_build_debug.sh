#!/bin/bash
set -e
ZK=/home/wennu/zkjh/Software
cd $ZK
set -a; source .env; set +a
export PATH=/home/wennu/zkjh/toolchain/bin-gnu:$PATH
# 改为 debug 构建(更详细的启动日志)
sed -i 's/^ZRT_ENV_BUILD_TYPE=.*/ZRT_ENV_BUILD_TYPE=debug/' .env
grep BUILD_TYPE .env
rm -f out/camera/uImage.jzlzma
find out -maxdepth 1 -name '*.bin' -delete || true
./build/build_camera_all.sh > /tmp/zk_build_debug.log 2>&1
RC=$?
echo "DEBUG BUILD EXIT=$RC $(date)"
ls -la out/*.bin 2>/dev/null
# 恢复 release
sed -i 's/^ZRT_ENV_BUILD_TYPE=.*/ZRT_ENV_BUILD_TYPE=release/' .env