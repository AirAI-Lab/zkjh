# Changelog

## [0.4.0] - 2026-11-08
### Added
- TP9950 摄像头链路验证通过（I2C总线 + sensor insmod + video capture v2 + DMA + VPU）
- releases/final/ 七件套精简部署包（内核+rootfs+4个.ko+TAG）
- 交互式 Root Shell（busybox init + askfirst console + 静态dev节点）

### Fixed
- T23ZN 时钟防御：CGU_SSI统一拦截 + SSI0 gate skip + reparent EXT1
- initrd 五层修复：fw_arg传递→页对齐→rmem安全区→实体/init→静态dev
- DEVTMPFS 手动挂载（initramfs 场景内核不自动挂）

### Changed
- releases 目录重构：final/(7件套) + archive/(33历史版)
- TF 卡精简至 7 文件（内核+rootfs+4.ko+TAG）
- releases/final 移除原厂固件（git 减重）

## [0.3.0] - 2026-11-07
### Added
- T23ZN-DEFENSE 时钟集中防御（clk_cgu.c 统一拦截）
- SSI0 reparent EXT1（修复 ops-enable 层第7 gate 挂死）
- env PC 直写（sector 413 对齐写 + CRC32 重算）

### Fixed
- 内核完整启动（BogoMIPS 1185 + console[ttyS1] + 全驱动 probe）
- TF 卡 raw 区重建（@17KB SD uboot + @3MB 内核）

## [0.2.0] - 2026-11-06
### Added
- 自编 U-Boot 1188 版（HARD_LZMA + console + DDR600）
- EARLY_PRINTK 内核（prom_putstr 直写串口）
- 四轮插桩定位法（setup_arch→mem_init→clk→CGU_SSI）

### Fixed
- T23ZN 缺 SSI 单元根因确认（CGU_SSI 寄存器总线挂死）
- verify=no 绕过 Bad Data CRC
- LZMA 内存 bootm（替代 jzlzma 硬件解压）

## [0.1.0] - 2026-11-05
### Added
- JKD-621-T23 完整开发方案
- TF 卡烧录体系（raw@17KB + FAT 三件套）
- SDK 编译链（debug 模式 + tp9950 传感器）

### Fixed
- quiet 参数根因定位
- TF 卡兼容性确认（仅 29.7GB 原卡可用）
