#!/bin/bash
set -e
P=/home/wennu/zkjh/Software/os/drivers/sensor-t23/zeratul/single_camera/tp9950/tp9950.c
# module_param 会引用 __this_module, 内建方式需去掉
sed -i '/^module_param(sensor_resolution/d; /^MODULE_PARM_DESC/d' $P
grep -n 'module_param\|MODULE_' $P || echo "no module_param left"
cd /home/wennu/zkjh/Software/os/drivers/sensor-t23/zeratul/single_camera/tp9950
set -a; source /home/wennu/zkjh/Software/.env; set +a
export PATH=/home/wennu/zkjh/toolchain/bin-gnu:$PATH
make clean >/dev/null 2>&1; make 2>&1 | grep -cE 'error' || true
ls -la sensor_tp9950_t23.ko
cp tp9950.o $ZRT_ENV_KERNEL_DIR/arch/mips/xburst/lib/isp-t23/tp9950.hex
cd /home/wennu/zkjh/Software
./build/build_camera_all.sh > /tmp/zk_build_tp9950.log 2>&1
echo "BUILD EXIT=$? $(date)"
ls -la out/*.bin 2>/dev/null || true