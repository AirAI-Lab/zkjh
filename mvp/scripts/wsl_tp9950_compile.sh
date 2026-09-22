#!/bin/bash
set -e
SD=/home/wennu/zkjh/Software/os/drivers/sensor-t23/zeratul/single_camera
# 1. 建立 tp9950 目录（如已存在先清理对象文件）
mkdir -p $SD/tp9950
cp /mnt/d/github/zkjh/tp9951.c $SD/tp9950/tp9950.c
# 2. 符号重命名 tp9951 -> tp9950
sed -i 's/tp9951/tp9950/g; s/TP9951/TP9950/g' $SD/tp9950/tp9950.c
# 3. 芯片 ID 双兼容(0x2850=TP9950 / 0x2860=TP9951, 上板前无法确认, 两者都放行)
python3 - <<'EOF'
import re
p = '/home/wennu/zkjh/Software/os/drivers/sensor-t23/zeratul/single_camera/tp9950/tp9950.c'
s = open(p, encoding='utf-8', errors='ignore').read()
old = '''	if (v != TP9950_CHIP_ID_L)
		return -ENODEV;
	*ident = (*ident << 8) | v;'''
new = '''	/* JKD-621-T23: 兼容 TP9950(0x2850) 与参考 TP9951(0x2860), 上板后按实测固定 */
	if (v != 0x50 && v != 0x60)
		return -ENODEV;
	printk("tp995x chip id = 0x28%02x (%s)\\n", v, (v == 0x50 ? "TP9950" : "TP9951"));
	*ident = (*ident << 8) | v;'''
assert old in s, 'detect block not found'
s = s.replace(old, new)
open(p, 'w', encoding='utf-8').write(s)
print('patched detect()')
EOF
# 4. Makefile(照抄 gc2053, TARGET=tp9950)
cat > $SD/tp9950/Makefile <<'EOF'
CROSS_COMPILE ?= mips-linux-gnu-

TARGET=tp9950

KDIR := $(ZRT_ENV_KERNEL_DIR)

MODULE_NAME := sensor_$(TARGET)_t23

EXTRA_CFLAGS += -I$(PWD)/../include

all: modules

.PHONY: modules clean

$(MODULE_NAME)-objs := $(TARGET).o
obj-m := $(MODULE_NAME).o

modules:
	@$(MAKE) -C $(KDIR) M=$(shell pwd) $@

clean:
	@rm -rf *.o *~ .depend ..*.cmd  *.mod.c .tmp_versions *.ko *.symvers modules.order

release:
	cp $(TARGET).o $(KDIR)/arch/mips/xburst/lib/isp-t23/$(TARGET).hex
EOF
# 5. 编译
cd $SD/tp9950
set -a; source /home/wennu/zkjh/Software/.env; set +a
export PATH=/home/wennu/zkjh/toolchain/bin-gnu:$PATH
make 2>&1 | tail -15
ls -la *.ko 2>/dev/null || echo "NO KO"