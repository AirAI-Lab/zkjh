# JKD-621-T23 MVP 工作区

快速开始：
```bash
# 1. 协议自测（无硬件）
python sim/zk_codec.py
python sim/gas_sim.py --selftest

# 2. 平台模拟
python sim/mock_server.py            # http://localhost:8080

# 3. 燃气模拟器（接好 USB-TTL 到 J6 后）
python sim/gas_sim.py --port COM3    # 运行中: set 3.20 / high / low / fault 01 / drop

# 4. 固件编译（WSL）
wsl -d Ubuntu -- bash /mnt/d/github/zkjh/mvp/scripts/wsl_setup_env.sh   # 首次
wsl -d Ubuntu -- bash /mnt/d/github/zkjh/mvp/scripts/wsl_run_build.sh   # 编译
```
文档：docs/00_MVP开发交接总览.md → 01_环境搭建指南.md → 02_板级调试指南.md