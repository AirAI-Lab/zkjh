#!/bin/bash
set -e
P=/home/wennu/zkjh/Software/os/drivers/sensor-t23/zeratul/single_camera/tp9950/tp9950.c
sed -i 's/\.owner[[:space:]]*=[[:space:]]*THIS_MODULE/.owner = NULL/' $P
grep -n 'THIS_MODULE' $P || echo 'THIS_MODULE removed'
cd /home/wennu/zkjh/Software/os/drivers/sensor-t23/zeratul/single_camera/tp9950
set -a; source /home/wennu/zkjh/Software/.env; set +a
export PATH=/home/wennu/zkjh/toolchain/bin-gnu:$PATH
make clean >/dev/null 2>&1; make 2>&1 | grep -E ' error' | head -5 || true
nm -u tp9950.o | grep -c __this_module || echo "no __this_module ref"
ls -la sensor_tp9950_t23.ko
cp tp9950.o $ZRT_ENV_KERNEL_DIR/arch/mips/xburst/lib/isp-t23/tp9950.hex
cd /home/wennu/zkjh/Software
./build/build_camera_all.sh > /tmp/zk_build_tp9950.log 2>&1
RC=$?
echo "TP9950 FULL BUILD EXIT=$RC $(date)"
tail -4 /tmp/zk_build_tp9950.log
find out -maxdepth 1 -name '*.bin' -exec ls -la {} \;