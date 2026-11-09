# Changelog

## [0.5.0] - 2026-11-09
### Changed
- 依据最新原理图修正 TP9950 → T23 链路：实际为 MIPI CSI-2 2-lane，不是 DVP。
- I2C0 改为 PA12/PA13 显式复用，禁用依赖 U-Boot 预初始化的 `I2C0_BOOT_DEFAULT`。
- 禁用 I2C1 PA16/PA17，避免抢占 T23 MIPI/DVP 共享复用域。
- VFAT/FAT 从 module 改为内置，解决最小 rootfs 无法挂载 TF FAT 分区问题。
- T23ZN 时钟防御收敛：保留 SSI 拦截/SSI0 skip/EXT1 reparent/busy 超时，移除全部临时插桩。

### Added
- `mvp/docs/06_T23ZN时钟与TP9950链路修复.md`
- `mvp/patches/0001-t23zn-jkd621-clk-i2c-vfat.patch`
- `mvp/scripts/clean_clock_debug.py`、`generate_t23_patch.sh`

### Fixed
- 修正硬编码 initrd 长度，当前 `rootfs-ask.cpio` 为 4,799,488 字节（0x493c00）。
- 上板实测 TP9950 I2C 7bit 地址为 `0x30`（修正参考驱动默认 `0x44`）。
- 最终 ISP 测试内核保持 9389b24 可启动布局，用二进制 NOP 忽略 TP995x 版本寄存器 NACK，避免重排内核入口触发早期复位。

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

