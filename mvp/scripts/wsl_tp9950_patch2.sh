#!/bin/bash
set -e
P=/home/wennu/zkjh/Software/os/drivers/sensor-t23/zeratul/single_camera/tp9950/tp9950.c
python3 - <<'EOF'
p = '/home/wennu/zkjh/Software/os/drivers/sensor-t23/zeratul/single_camera/tp9950/tp9950.c'
s = open(p, encoding='utf-8', errors='ignore').read()
marker = 'static __init int init_tp9950(void)'
i = s.find(marker)
assert i > 0, 'init marker not found'
wrapper = '''/* ===== Zeratul built-in sensor wrapper (提供 ISP 期望的导出符号) ===== */
char * get_sensor_name(void)
{
	return "tp9950";
}

int get_sensor_i2c_addr(void)
{
	return 0x44;   /* TP9950/TP9951 Techpoint 默认 7bit 地址, 上板用 i2cdetect 复核 */
}

int get_sensor_width(void)
{
	return tp9950_win_sizes->width;
}

int get_sensor_height(void)
{
	return tp9950_win_sizes->height;
}

int init_sensor(void)
{
	return private_i2c_add_driver(&tp9950_driver);
}

void exit_sensor(void)
{
	private_i2c_del_driver(&tp9950_driver);
}
'''
s = s[:i] + wrapper
# THIS_MODULE -> NULL (内建, 避免 __this_module 未定义)
s = s.replace('.owner\t\t= THIS_MODULE,', '.owner\t\t= NULL,')
s = s.replace('.owner = THIS_MODULE,', '.owner = NULL,')
open(p, 'w', encoding='utf-8').write(s)
print('wrapper appended, module_init removed')
EOF
cd /home/wennu/zkjh/Software/os/drivers/sensor-t23/zeratul/single_camera/tp9950
set -a; source /home/wennu/zkjh/Software/.env; set +a
export PATH=/home/wennu/zkjh/toolchain/bin-gnu:$PATH
make clean >/dev/null 2>&1 || true
make 2>&1 | grep -E 'error|warning: .*tp9950|LD|MODPOST' | head -10
ls -la sensor_tp9950_t23.ko
cp tp9950.o $ZRT_ENV_KERNEL_DIR/arch/mips/xburst/lib/isp-t23/tp9950.hex
# 符号自检
/home/wennu/zkjh/toolchain/bin-gnu/mips-linux-gnu-nm tp9950.o | grep -E ' T (init_sensor|get_sensor_name|get_sensor_i2c_addr|exit_sensor)' 