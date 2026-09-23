# JKD-621-T23 地埋桩式甲烷泄漏监测终端（带摄像头）— 协同开发主入口

> 项目：基于君正 T23 + TP9950(AHD解码) + ML307R-DL(Cat.1) + HC32L136(低功耗MCU) 的
> 电池供电低功耗图片终端。4 路 AHD 摄像头轮询抓拍，燃气(JH-TG5110-M1-22)联动告警，
> 目标续航 3 年。
> 本仓库 = 原始资料 + 全部工程文档 + MVP 代码。**新成员从本文件开始读。**

## 1. 文档地图（按阅读顺序）
| 顺序 | 文档 | 内容 |
|---|---|---|
| ① | `docs/决策与历史记录.md` | **项目全部历史决策**（必读，避免重复踩坑/重复讨论） |
| ② | `需求理解与开发评估_JKD-621-T23_V0.2.md` | 需求理解、原理图解析、方案、计划、成本（附录A~G为各阶段增量） |
| ③ | `接口控制文档ICD_JKD-621-T23_V0.1.md` | 三条链路协议：HC32↔T23、燃气↔J6、T23↔ML307R |
| ④ | `mvp/docs/00_MVP开发交接总览.md` | MVP 目标、目录、进度、分工、六周里程碑 |
| ⑤ | `mvp/docs/01_环境搭建指南.md` | WSL 编译环境（含 9 个已踩坑记录） |
| ⑥ | `mvp/docs/03_完整构建与烧录流程.md` | 从零到固件烧录的端到端流程 |
| ⑦ | mvp/docs/02_板级调试指南.md | 如何进系统（无HDMI）、串口/telnet/看图 |
| ⑧ | mvp/docs/05_首次上电检查单.md | **板到手第一步**：接线/烧录/出流/通道切换检查单 |

## 2. 目录结构
```
D:\github\zkjh\
├── README.md                        ← 本文件（协同入口）
├── docs\决策与历史记录.md            ← 历史决策日志（持续追加）
├── 需求理解与开发评估_*.md           ← 主方案文档（V0.2+附录A~G）
├── 接口控制文档ICD_*.md              ← 协议文档
├── JKD-621-T23-设备功能需求说明.docx ← 原始需求（甲方）
├── 埋地式甲烷泄漏监测仪*说明书.pdf    ← 整机产品说明书
├── 扩散式激光甲烷传感器模块*.docx     ← 燃气模块说明书（协议来源）
├── 原理图_1-JKD-621-T23-V1.0*.pdf    ← 自研板原理图（2026-07-22）
├── tp9951.c                          ← 君正提供的 T23+TP9951 参考驱动
├── ML307R（中移AT固件版本）\          ← 4G 模组官方手册（17份）
├── Ingenic_Zeratul_T23_V4.0.0_\      ← 君正电池类IPC SDK（编译基线）
├── ISVP-T23-1.3.0-...\               ← 君正基础SDK+工具链
├── Ingenic-HDK-T23-*\                ← 硬件参考设计（GPIO表/原理图/BOM）
└── mvp\                              ← MVP 工作区（代码/脚本/文档/固件）
```

## 3. 当前状态（2026-09-22）
- ✅ 编译环境打通（WSL2 Ubuntu 24.04 + mips-gcc540-uclibc）
- ✅ **TP9950 驱动已集成并编译进固件**：`mvp/releases/ZRT_SOC_T23ZN_TP9950_DIRECT_FW.bin`
- ✅ 协议库（HC32↔T23 / 燃气）、模拟器、Mock 平台均可运行（自测通过）
- ⏳ 待上板：烧录验证、TP9950 出流、通道切换实测、低功耗闭环（板未连 PC，串口监控工具已备好：python mvp/scripts/serial_monitor.py）
- ⏳ 待开发：HC32 固件、T23 应用、4G 拨号、功耗调优

## 4. 协作约定
1. **文档即真相**：任何方案/接口/引脚变更，改文档 + 在 `docs/决策与历史记录.md` 追加一条（格式见该文件）。
2. **Git 工作流**：main 保护，成员建 `dev-<名字>-<模块>` 分支；提交信息 `模块: 改动摘要`。
3. **编译环境统一**：WSL 路径固定 `~/zkjh/Software`（勿在 /mnt/d 上编译）。
4. **SDK 目录只读**：vendor 目录（Ingenic_*/ISVP-*/ML307R*）不修改；定制一律放 `mvp/` 或
   WSL 侧 `~/zkjh/Software`（后者变更需在决策记录中登记 diff）。
5. 固件产物放 `mvp/releases/`（命名 `ZRT_..._<sensor>_<日期>.bin`），不提交中间产物。
6. 硬件相关结论必须注明来源（原理图页/手册章节/实测 log），便于复核。

## 5. 快速开始
```powershell
# 编译固件（首次约 10 分钟）
wsl -d Ubuntu -- bash /mnt/d/github/zkjh/mvp/scripts/wsl_setup_env.sh
wsl -d Ubuntu -- bash /mnt/d/github/zkjh/mvp/scripts/wsl_tp9950_patch4.sh   # TP9950 固件
# 协议自测（无需硬件）
python D:\github\zkjh\mvp\sim\zk_codec.py
python D:\github\zkjh\mvp\sim\gas_sim.py --selftest
```