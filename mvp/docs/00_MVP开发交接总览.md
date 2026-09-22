# JKD-621-T23 MVP 开发交接总览（V1.0，2026-09-16）

> 本目录（D:\github\zkjh\mvp）为 MVP 阶段工作区。
> **协同规则与全部历史决策见根目录 README.md 与 docs/决策与历史记录.md（新成员必读）。**
> 需求/接口/成本详见上级目录：
> - 需求理解与开发评估_JKD-621-T23_V0.2.md（含原理图解析、方案、计划、成本）
> - 接口控制文档ICD_JKD-621-T23_V0.1.md（三条链路协议）

## 1. MVP 目标（验收标准）
在两块 JKD-621-T23 V1.0 板上打通：
1. **低功耗闭环**：RTC 定时唤醒 → 抓拍（TP9950 通道轮询）→ TF 缓存 → 4G 上传（mock 平台）→ 回睡
2. **燃气高报联动**：gas_sim.py 模拟浓度 → HC32 判级唤醒 → 联动抓拍 → 上报 → 平台可见
3. **功耗初测**：休眠电流 + 单轮能耗数据（外推 3 年续航模型）

## 2. 系统架构（一句话）
HC32L136（常电域：RTC/ADXL345震动倾角位移/AH3716磁感应/燃气J6监听/拨码）
→ 唤醒时 PWR 上电 T23（UART0 通告原因）→ T23 快起 → I2C 配 TP9950 → AHD→DVP 抓 JPEG
→ TF 缓存 → USB RNDIS 拨号 ML307R → 上传 → UART0 命令 HC32 断电回睡（MCU_WDT 贯穿）。

## 3. 目录结构
```
mvp/
├── common/          # C 协议库（T23/HC32 固件共用）
│   ├── zk_protocol.*    HC32<->T23 二进制帧（AA55+CRC16-MODBUS，已自测）
│   └── gas_protocol.*   燃气 ASCII 帧解析（已按说明书实测校验）
├── sim/             # 可立即运行的工具
│   ├── zk_codec.py      协议 Python 版 + 自测（python zk_codec.py）
│   ├── gas_sim.py       燃气模拟器（--selftest / --port COMx）
│   └── mock_server.py   平台模拟（POST /api/event, /api/image/<devid>/<name>）
├── scripts/
│   ├── wsl_setup_env.sh 环境一键搭建（已验证）
│   └── wsl_run_build.sh 一键编译（已验证，产出完整固件）
├── hc32fw/          # HC32L136 固件骨架（待开发，Keil/HC32 工具链）
├── t23app/          # T23 应用骨架（待开发，交叉编译进 rootfs/system）
├── tests/           # 测试
├── releases/        # 固件存档（ZRT_SOC_T23ZN_TP9950_DIRECT_FW.bin）
└── docs/            # 本文档 + 环境指南 + 完整构建流程 + 板级调试指南
```

## 4. 当前进度（2026-09-16）
| 项 | 状态 |
|---|---|
| WSL2 Ubuntu 24.04 编译环境 | ✅ 搭建完成并验证 |
| Zeratul SDK 解包+工具链 | ✅ ~/zkjh/Software（含坑位修复） |
| 整包固件编译 | ✅ ZRT_SOC_T23ZN_GC2053_DIRECT_FW.bin 13.8MB（gc2053 参考配置） |
| 燃气协议解析+模拟器 | ✅ 按说明书实测（样例2校验吻合；样例1疑文档笔误已标注） |
| HC32<->T23 协议库 | ✅ C+Python 双实现自测通过 |
| Mock 平台服务器 | ✅ 事件/图片上传/统计 自测通过 |
| TP9950 驱动适配 | ✅ 已完成代码集成并编译进固件 ZRT_SOC_T23ZN_TP9950_DIRECT_FW.bin（上板验证=W2） |
| HC32 固件 | ⏳ W2-W3（唤醒调度/传感器/燃气监听/UART 协议） |
| 板子实机联调 | ⏳ 待硬件接入（串口线+USB网卡+SIM） |

## 5. 六周里程碑（2 人：A=BSP/T23，B=HC32/测试）
- W1 环境与烧录：两板烧固件、串口进系统、USB 网卡 telnet、carrier-server 出图（gc2053 EVK 可先验）
- W2 视频链路：TP9950 驱动移植（YUV DVP sensor 模板）→ 单通道出图 → 通道切换
- W3 低功耗框架：HC32 固件 v0.1（RTC 唤醒+UART 协议+PWR 控制）+ T23 侧 wake/sleep 流程 + MCU_WDT
- W4 缓存与 4G：TF 队列/断电恢复 + ML307R RNDIS 拨号 + mock 平台上传（首图先行）
- W5 传感器与燃气：ADXL345/AH3716 判级 + gas_sim 联动端到端演示 + 拨码维护
- W6 功耗与验收：休眠电流测量、单轮能耗、演示脚本、交接文档

## 6. 团队分工建议
| 角色 | 负责模块 | 关键输入 |
|---|---|---|
| A 嵌入式 Linux/BSP | TP9950 移植、T23 app、4G 拨号、OTA 底座 | mvp/docs/01 环境指南、SDK 文档 |
| B MCU/固件 | HC32L136 全部（ADXL345/AH3716/RTC/燃气/UART0/PWR） | ICD 第2/3章、common/*.c |
| C 测试/平台(0.5) | mock 平台、模拟器、用例矩阵、功耗测试 | sim/ 目录 |

## 7. 遗留问题清单（按优先级）
1. 燃气校验字节范围（样例1不符算法，待厂家确认；当前统一前 40 字节 XOR）
2. 燃气模块 5V 供电域：40mA 常供电 3 年不可行 → 需占空比采样或独立电池（产品决策）
3. TP9950 四通道切换锁定时间实测（预算 200-500ms）
4. ML307R VID/PID(0x2ecc:0x3012) 在 T23 3.10 内核 RNDIS 实测
5. HC32 PA00/PA01 复用为 UART 的配置确认（查 HC32L136 数据手册复用表）
6. 电池容量/太阳能功率未提供（续航模型输入）